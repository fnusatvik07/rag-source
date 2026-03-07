"""
HTML Extraction Method 2: html2text

html2text converts HTML to clean, readable markdown.
It handles most HTML structures automatically with minimal configuration.

Best for: Quick HTML-to-text conversion, when you want markdown output for heading-aware chunking.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import html2text

from unstructured_documents.shared.chunking import (
    chunk_by_headings,
    chunk_by_sentences,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def extract_with_default_settings(html_path: Path) -> str:
    """Convert HTML to markdown with default settings."""
    converter = html2text.HTML2Text()
    return converter.handle(html_path.read_text())


def extract_clean_text(html_path: Path) -> str:
    """Convert HTML to plain text (no markdown formatting)."""
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.ignore_emphasis = True
    converter.body_width = 0  # No line wrapping
    return converter.handle(html_path.read_text())


def extract_with_custom_settings(html_path: Path) -> str:
    """Convert HTML to markdown with RAG-optimized settings."""
    converter = html2text.HTML2Text()
    converter.body_width = 0  # No line wrapping (better for chunking)
    converter.ignore_links = True  # Links add noise for RAG
    converter.ignore_images = True  # Can't embed images in text chunks
    converter.ignore_emphasis = False  # Keep bold/italic for context
    converter.protect_links = False
    converter.unicode_snob = True  # Use unicode instead of ASCII approximations
    converter.skip_internal_links = True
    return converter.handle(html_path.read_text())


if __name__ == "__main__":
    article_path = SAMPLE_DIR / "article_page.html"
    table_path = SAMPLE_DIR / "table_heavy_page.html"
    nested_path = SAMPLE_DIR / "nested_structure.html"

    # --- Default conversion ---
    print("=" * 60)
    print("1. DEFAULT HTML2TEXT CONVERSION (article_page.html)")
    print("=" * 60)
    md_default = extract_with_default_settings(article_path)
    print(f"Output length: {len(md_default)} chars")
    print(md_default[:500])

    # --- Clean text (no formatting) ---
    print(f"\n{'=' * 60}")
    print("2. CLEAN TEXT (no markdown formatting)")
    print("=" * 60)
    clean = extract_clean_text(article_path)
    print(f"Output length: {len(clean)} chars")
    print(clean[:500])

    # --- RAG-optimized ---
    print(f"\n{'=' * 60}")
    print("3. RAG-OPTIMIZED CONVERSION")
    print("=" * 60)
    rag_text = extract_with_custom_settings(article_path)
    print(f"Output length: {len(rag_text)} chars")
    print(rag_text[:500])

    # --- Heading-aware chunking on markdown output ---
    print(f"\n{'=' * 60}")
    print("4. HEADING-AWARE CHUNKING on markdown output")
    print("=" * 60)
    chunks = chunk_by_headings(rag_text)
    preview_chunks(chunks)

    # --- Table-heavy page ---
    print(f"\n{'=' * 60}")
    print("5. TABLE-HEAVY PAGE CONVERSION")
    print("=" * 60)
    table_md = extract_with_custom_settings(table_path)
    print(table_md[:600])

    # --- Nested/documentation page ---
    print(f"\n{'=' * 60}")
    print("6. NESTED STRUCTURE PAGE")
    print("=" * 60)
    nested_md = extract_with_custom_settings(nested_path)
    chunks = chunk_by_sentences(nested_md, sentences_per_chunk=4)
    print(f"Extracted {len(nested_md)} chars, split into {len(chunks)} sentence-based chunks")
    preview_chunks(chunks)
