"""
HTML Extraction Method 3: Trafilatura

Trafilatura is designed specifically for web content extraction.
It automatically identifies and extracts the main content, stripping boilerplate
(navigation, ads, footers, sidebars).

Best for: Extracting article/main content from web pages, automatic boilerplate removal.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import trafilatura

from unstructured_documents.shared.chunking import (
    chunk_by_recursive_split,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def extract_plain_text(html_path: Path) -> str | None:
    """Extract main content as plain text (default)."""
    html = html_path.read_text()
    return trafilatura.extract(html)


def extract_with_metadata(html_path: Path) -> dict | None:
    """Extract content along with metadata (title, author, date, etc.)."""
    html = html_path.read_text()
    result = trafilatura.extract(
        html,
        output_format="json",
        include_comments=False,
        include_tables=True,
        include_links=False,
    )
    if result:
        import json

        return json.loads(result)
    return None


def extract_as_xml(html_path: Path) -> str | None:
    """Extract content as XML with structural markup preserved."""
    html = html_path.read_text()
    return trafilatura.extract(
        html,
        output_format="xml",
        include_tables=True,
    )


def extract_with_tables(html_path: Path) -> str | None:
    """Extract content including table data."""
    html = html_path.read_text()
    return trafilatura.extract(
        html,
        include_tables=True,
        include_comments=False,
        include_links=False,
    )


if __name__ == "__main__":
    article_path = SAMPLE_DIR / "article_page.html"
    table_path = SAMPLE_DIR / "table_heavy_page.html"
    nested_path = SAMPLE_DIR / "nested_structure.html"

    # --- Plain text extraction ---
    print("=" * 60)
    print("1. PLAIN TEXT EXTRACTION (article_page.html)")
    print("=" * 60)
    text = extract_plain_text(article_path)
    if text:
        print(f"Extracted {len(text)} characters")
        print(text[:500])
    else:
        print("No content extracted (trafilatura may not detect main content in simple HTML)")

    # --- With metadata ---
    print(f"\n{'=' * 60}")
    print("2. EXTRACTION WITH METADATA")
    print("=" * 60)
    meta_result = extract_with_metadata(article_path)
    if meta_result:
        print(f"Title: {meta_result.get('title', 'N/A')}")
        print(f"Author: {meta_result.get('author', 'N/A')}")
        print(f"Date: {meta_result.get('date', 'N/A')}")
        print(f"Text length: {len(meta_result.get('text', ''))}")
        print(f"First 300 chars: {meta_result.get('text', '')[:300]}")
    else:
        print("No metadata extracted")

    # --- Table-heavy page ---
    print(f"\n{'=' * 60}")
    print("3. TABLE-HEAVY PAGE EXTRACTION")
    print("=" * 60)
    table_text = extract_with_tables(table_path)
    if table_text:
        print(f"Extracted {len(table_text)} characters")
        print(table_text[:500])

        # Chunk the result
        print("\nChunked output:")
        chunks = chunk_by_recursive_split(table_text, chunk_size=300)
        preview_chunks(chunks)
    else:
        print("No content extracted")

    # --- Nested structure ---
    print(f"\n{'=' * 60}")
    print("4. NESTED STRUCTURE / DOCUMENTATION PAGE")
    print("=" * 60)
    nested_text = extract_plain_text(nested_path)
    if nested_text:
        print(f"Extracted {len(nested_text)} characters")
        print(nested_text[:500])
    else:
        print("No content extracted (documentation pages may be tricky for trafilatura)")

    # --- XML output format ---
    print(f"\n{'=' * 60}")
    print("5. XML OUTPUT FORMAT (preserves structure)")
    print("=" * 60)
    xml_out = extract_as_xml(article_path)
    if xml_out:
        print(f"XML output length: {len(xml_out)} chars")
        print(xml_out[:500])
    else:
        print("No XML output")
