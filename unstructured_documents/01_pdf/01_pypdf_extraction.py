"""
PDF text extraction using pypdf.

pypdf is a pure-Python library for reading and writing PDFs.
It provides basic text extraction, metadata access, and page manipulation.

Strengths:  Pure Python, no external dependencies, good for simple text PDFs.
Weaknesses: Limited layout awareness, no table extraction, may lose formatting.

Usage:
    uv run python unstructured_documents/01_pdf/01_pypdf_extraction.py
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pypdf import PdfReader

from unstructured_documents.shared.chunking import (
    chunk_by_characters,
    chunk_by_recursive_split,
    chunk_by_sentences,
    preview_chunks,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
SIMPLE_TEXT_PDF = SAMPLE_DIR / "simple_text.pdf"


def extract_text_page_by_page(pdf_path: Path) -> list[str]:
    """Extract text from each page of a PDF individually."""
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(text)
    return pages


def extract_full_text(pdf_path: Path) -> str:
    """Extract all text from a PDF as a single string."""
    pages = extract_text_page_by_page(pdf_path)
    return "\n\n".join(pages)


def extract_metadata(pdf_path: Path) -> dict:
    """Extract document metadata (title, author, creation date, etc.)."""
    reader = PdfReader(str(pdf_path))
    meta = reader.metadata
    if meta is None:
        return {}
    return {
        "title": meta.title,
        "author": meta.author,
        "subject": meta.subject,
        "creator": meta.creator,
        "producer": meta.producer,
        "creation_date": str(meta.creation_date) if meta.creation_date else None,
        "modification_date": str(meta.modification_date) if meta.modification_date else None,
        "num_pages": len(reader.pages),
    }


def demo_page_by_page_extraction():
    """Show page-by-page text extraction."""
    print("=" * 70)
    print("1. PAGE-BY-PAGE TEXT EXTRACTION (pypdf)")
    print("=" * 70)

    pages = extract_text_page_by_page(SIMPLE_TEXT_PDF)
    for i, page_text in enumerate(pages):
        print(f"\n--- Page {i + 1} ({len(page_text)} chars) ---")
        # Show first 300 characters of each page
        preview = page_text[:300].strip()
        if len(page_text) > 300:
            preview += "..."
        print(preview)

    print(f"\nTotal pages: {len(pages)}")
    total_chars = sum(len(p) for p in pages)
    print(f"Total characters extracted: {total_chars:,}")


def demo_metadata_extraction():
    """Show PDF metadata extraction."""
    print("\n" + "=" * 70)
    print("2. METADATA EXTRACTION (pypdf)")
    print("=" * 70)

    metadata = extract_metadata(SIMPLE_TEXT_PDF)
    for key, value in metadata.items():
        print(f"  {key:20s}: {value}")


def demo_chunking():
    """Show how to chunk extracted text for RAG using shared utilities."""
    print("\n" + "=" * 70)
    print("3. CHUNKING FOR RAG (using shared chunking utilities)")
    print("=" * 70)

    full_text = extract_full_text(SIMPLE_TEXT_PDF)
    print(f"\nFull text length: {len(full_text):,} characters")

    # Strategy 1: Fixed-size character chunks
    print("\n--- Strategy: Character Chunking (500 chars, 50 overlap) ---")
    char_chunks = chunk_by_characters(full_text, chunk_size=500, overlap=50)
    preview_chunks(char_chunks, max_preview=2, max_chars=150)

    # Strategy 2: Sentence-based chunks
    print("\n--- Strategy: Sentence Chunking (5 sentences per chunk) ---")
    sent_chunks = chunk_by_sentences(full_text, sentences_per_chunk=5, overlap_sentences=1)
    preview_chunks(sent_chunks, max_preview=2, max_chars=150)

    # Strategy 3: Recursive splitting
    print("\n--- Strategy: Recursive Split (500 char target) ---")
    rec_chunks = chunk_by_recursive_split(full_text, chunk_size=500)
    preview_chunks(rec_chunks, max_preview=2, max_chars=150)

    # Summary comparison
    print("\n--- Chunking Strategy Comparison ---")
    print(f"  {'Strategy':<25s} {'Chunks':>8s} {'Avg Size':>10s} {'Min':>6s} {'Max':>6s}")
    print(f"  {'-' * 25} {'-' * 8} {'-' * 10} {'-' * 6} {'-' * 6}")
    for name, chunks in [
        ("Character (500)", char_chunks),
        ("Sentence (5/chunk)", sent_chunks),
        ("Recursive Split (500)", rec_chunks),
    ]:
        sizes = [len(c) for c in chunks]
        avg = sum(sizes) / len(sizes) if sizes else 0
        print(f"  {name:<25s} {len(chunks):>8d} {avg:>10.1f} {min(sizes):>6d} {max(sizes):>6d}")


if __name__ == "__main__":
    if not SIMPLE_TEXT_PDF.exists():
        print(f"ERROR: {SIMPLE_TEXT_PDF} not found.")
        print("Run generate_samples.py first:")
        print("  uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py")
        sys.exit(1)

    demo_page_by_page_extraction()
    demo_metadata_extraction()
    demo_chunking()

    print("\n" + "=" * 70)
    print("Done. pypdf provides basic but reliable text extraction.")
    print("For better layout handling, see 02_pdfplumber_extraction.py")
    print("=" * 70)
