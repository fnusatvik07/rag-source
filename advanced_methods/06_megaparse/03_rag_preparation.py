"""
MegaParse - RAG Document Preparation
=======================================
End-to-end example showing how to use MegaParse to prepare
documents for a RAG pipeline:

1. Parse document to Markdown
2. Chunk the output for embedding
3. Add metadata for retrieval

MegaParse's Markdown output is already optimized for LLMs,
making it an efficient first step in any RAG pipeline.

uv pip install megaparse
"""

import re
import sys
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"
sys.path.insert(0, str(SAMPLES_DIR / "shared"))


def rag_preparation_pipeline():
    """Full pipeline: parse -> chunk -> prepare for embedding."""
    print("=" * 60)
    print("MEGAPARSE RAG PREPARATION PIPELINE")
    print("=" * 60)

    # Step 1: Parse document
    markdown_text = _get_parsed_content()
    if not markdown_text:
        return

    print(f"\nStep 1: Parsed document ({len(markdown_text)} chars)")

    # Step 2: Chunk by headings (Markdown-aware)
    chunks = chunk_markdown_by_headings(markdown_text, max_chars=500)
    print(f"Step 2: Created {len(chunks)} chunks")

    # Step 3: Add metadata
    enriched_chunks = []
    for i, chunk in enumerate(chunks):
        enriched_chunks.append(
            {
                "id": f"chunk_{i}",
                "text": chunk["text"],
                "metadata": {
                    "heading": chunk.get("heading", ""),
                    "char_count": len(chunk["text"]),
                    "chunk_index": i,
                    "source": "megaparse",
                },
            }
        )

    print("Step 3: Enriched with metadata")

    # Display results
    print(f"\n{'=' * 60}")
    print("CHUNK PREVIEW")
    print(f"{'=' * 60}")
    for chunk in enriched_chunks[:5]:
        print(f"\n--- {chunk['id']} ---")
        print(f"  Heading: {chunk['metadata']['heading']}")
        print(f"  Length: {chunk['metadata']['char_count']} chars")
        print(f"  Text: {chunk['text'][:150]}...")


def chunk_markdown_by_headings(text, max_chars=500):
    """Split Markdown text by headings, respecting size limits."""
    chunks = []
    current_heading = ""
    current_text = ""

    for line in text.split("\n"):
        if re.match(r"^#{1,3}\s", line):
            # Save previous chunk
            if current_text.strip():
                for sub_chunk in _split_if_too_long(current_text.strip(), max_chars):
                    chunks.append({"heading": current_heading, "text": sub_chunk})
            current_heading = line.strip("# ").strip()
            current_text = line + "\n"
        else:
            current_text += line + "\n"

    # Save last chunk
    if current_text.strip():
        for sub_chunk in _split_if_too_long(current_text.strip(), max_chars):
            chunks.append({"heading": current_heading, "text": sub_chunk})

    return chunks


def _split_if_too_long(text, max_chars):
    """Split text into smaller pieces if it exceeds max_chars."""
    if len(text) <= max_chars:
        return [text]

    pieces = []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > max_chars and current:
            pieces.append(current.strip())
            current = sentence
        else:
            current += " " + sentence if current else sentence

    if current.strip():
        pieces.append(current.strip())

    return pieces


def _get_parsed_content():
    """Get parsed content from MegaParse or use sample Markdown."""
    try:
        from megaparse import MegaParse

        pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf")
        megaparse = MegaParse()
        return megaparse.load(pdf_path)
    except ImportError:
        print("[MegaParse not installed - using sample Markdown for demo]")
        print("Install: uv pip install megaparse\n")

        # Use existing Markdown file as fallback
        md_path = SAMPLES_DIR / "08_markdown_txt" / "sample_docs" / "technical_doc.md"
        if md_path.exists():
            return md_path.read_text()

        return """# Sample Document

## Introduction
This is a sample document demonstrating the RAG preparation pipeline.
MegaParse would normally convert your PDF into clean Markdown like this.

## Data Processing
The data processing module handles input validation, transformation,
and output formatting. It supports multiple data formats including
JSON, CSV, and XML.

## Results
Our experiments show significant improvement over baseline methods.
The accuracy increased from 78% to 94% using the new approach.

| Method | Accuracy | Speed |
|--------|----------|-------|
| Baseline | 78% | 100ms |
| New Method | 94% | 120ms |

## Conclusion
The new method provides substantially better results with minimal
overhead in processing time.
"""


if __name__ == "__main__":
    rag_preparation_pipeline()
