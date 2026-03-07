"""
DOCX extraction using docx2txt — the simplest, text-only approach.

docx2txt extracts plain text from a DOCX file in a single function call.
It strips all formatting, styles, and structure, returning a clean text string.

This script demonstrates:

  1. One-line text extraction
  2. What is preserved and what is lost compared to python-docx
  3. When this simple approach is "good enough"
  4. Character-based chunking with the shared utility

Run:
    uv run python unstructured_documents/02_docx/03_docx2txt_extraction.py
"""

import sys
from pathlib import Path

import docx2txt

# ---------------------------------------------------------------------------
# Make shared utilities importable from the project root
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from unstructured_documents.shared.chunking import (
    chunk_by_characters,
    chunk_by_recursive_split,
    chunk_by_sentences,
    preview_chunks,
)

SAMPLE_DOC = Path(__file__).resolve().parent / "sample_docs" / "simple_document.docx"


# ===================================================================
# 1. Basic text extraction
# ===================================================================


def extract_text(doc_path: Path) -> str:
    """
    Extract the full plain-text content of a DOCX file.

    docx2txt.process() returns a single string with all the visible text.
    Paragraphs are separated by newlines.  Tables are rendered with tabs
    between cells and newlines between rows.
    """
    return docx2txt.process(str(doc_path))


# ===================================================================
# 2. Analysis: what is preserved vs. lost
# ===================================================================


def analyse_extraction(text: str) -> dict:
    """
    Run simple heuristics to illustrate what docx2txt keeps and drops.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    words = text.split()

    return {
        "total_characters": len(text),
        "total_words": len(words),
        "non_empty_lines": len(lines),
        "contains_tabs": "\t" in text,  # tables survive as tab-separated
        "contains_bullet_markers": False,  # bullet symbols are lost
        "heading_markers_present": False,  # heading markup is lost
    }


# ===================================================================
# Main demonstration
# ===================================================================


def main() -> None:
    print("=" * 70)
    print("DOCX Extraction with docx2txt")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Extract plain text
    # ------------------------------------------------------------------
    print("\n\n--- 1. Plain-Text Extraction ---\n")
    text = extract_text(SAMPLE_DOC)

    print(f"Extracted {len(text)} characters of plain text.\n")
    print("First 600 characters:")
    print("-" * 50)
    print(text[:600])
    print("-" * 50)

    # ------------------------------------------------------------------
    # 2. What is preserved and what is lost
    # ------------------------------------------------------------------
    print("\n\n--- 2. Preservation Analysis ---\n")
    info = analyse_extraction(text)

    print(f"  Total characters:        {info['total_characters']:,}")
    print(f"  Total words:             {info['total_words']:,}")
    print(f"  Non-empty lines:         {info['non_empty_lines']}")
    print(f"  Tab characters present:  {info['contains_tabs']}  (tables as TSV)")

    print("\n  PRESERVED by docx2txt:")
    print("    + All visible text content")
    print("    + Paragraph breaks (as newlines)")
    print("    + Table cell text (tab-separated)")
    print("    + Text from headers and footers")

    print("\n  LOST by docx2txt:")
    print("    - Heading levels / style names (no way to tell H1 from Normal)")
    print("    - Bold, italic, underline formatting")
    print("    - Bullet and number list markers")
    print("    - Font names, sizes, and colours")
    print("    - Table grid structure (only tab-separated text remains)")
    print("    - Hyperlink URLs (link text is kept, target URL is dropped)")

    # ------------------------------------------------------------------
    # 3. When is docx2txt sufficient?
    # ------------------------------------------------------------------
    print("\n\n--- 3. When to Use docx2txt ---\n")

    print("  USE docx2txt when:")
    print("    - You only need the raw text for keyword search or full-text indexing.")
    print("    - Speed matters more than structure (it is the fastest option).")
    print("    - The document has little meaningful structure (e.g. a plain letter).")
    print("    - You will apply your own NLP sentence/paragraph segmentation.")

    print("\n  AVOID docx2txt when:")
    print("    - You need heading-based chunking (use python-docx or mammoth instead).")
    print("    - You need to preserve tables with headers (use python-docx).")
    print("    - You need the document converted to HTML or markdown (use mammoth).")
    print("    - You need inline formatting metadata (use python-docx runs).")

    # ------------------------------------------------------------------
    # 4. Chunking strategies for plain text
    # ------------------------------------------------------------------
    print("\n\n--- 4. Chunking Plain Text for RAG ---\n")

    print("Since docx2txt output has no heading markers, heading-based chunking")
    print("is NOT available.  Instead, we use character, sentence, or recursive")
    print("splitting.\n")

    # 4a. Character-based
    print("(a) Character-based chunking (500 chars, 50 overlap):")
    char_chunks = chunk_by_characters(text, chunk_size=500, overlap=50)
    preview_chunks(char_chunks, max_preview=3, max_chars=150)

    # 4b. Sentence-based
    print("\n(b) Sentence-based chunking (5 sentences/chunk):")
    sent_chunks = chunk_by_sentences(text, sentences_per_chunk=5, overlap_sentences=1)
    preview_chunks(sent_chunks, max_preview=3, max_chars=150)

    # 4c. Recursive split
    print("\n(c) Recursive split (500 char target):")
    rec_chunks = chunk_by_recursive_split(text, chunk_size=500)
    preview_chunks(rec_chunks, max_preview=3, max_chars=150)

    print("\n\nTip: For plain-text output, recursive splitting usually gives the")
    print("best balance between chunk size uniformity and semantic boundaries.")


if __name__ == "__main__":
    main()
