"""
DOCX extraction using mammoth — semantic conversion to HTML and markdown.

mammoth focuses on *semantic* conversion: it maps Word styles to HTML tags
rather than trying to reproduce the visual layout.  This makes its output
especially clean for downstream NLP / RAG pipelines.

This script demonstrates:

  1. Convert DOCX to HTML
  2. Convert DOCX to markdown (via mammoth style mapping)
  3. Heading-aware chunking on the markdown output
  4. Side-by-side comparison of HTML vs. markdown output

Run:
    uv run python unstructured_documents/02_docx/02_mammoth_extraction.py
"""

import sys
from pathlib import Path

import mammoth

# ---------------------------------------------------------------------------
# Make shared utilities importable from the project root
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from unstructured_documents.shared.chunking import (
    chunk_by_headings,
    preview_chunks,
)

SAMPLE_DOC = Path(__file__).resolve().parent / "sample_docs" / "simple_document.docx"


# ===================================================================
# 1. Convert DOCX to HTML
# ===================================================================


def docx_to_html(doc_path: Path) -> tuple[str, list[str]]:
    """
    Convert the DOCX file to clean, semantic HTML.

    mammoth maps:
      Heading 1  ->  <h1>
      Heading 2  ->  <h2>
      List Bullet ->  <ul><li>
      Bold       ->  <strong>
      Italic     ->  <em>

    Returns (html_string, messages) where messages are any warnings
    from the conversion (e.g. unrecognised styles).
    """
    with open(doc_path, "rb") as f:
        result = mammoth.convert_to_html(f)
    return result.value, [str(m) for m in result.messages]


# ===================================================================
# 2. Convert DOCX to markdown
# ===================================================================


def docx_to_markdown(doc_path: Path) -> tuple[str, list[str]]:
    """
    Convert the DOCX file to markdown using mammoth's built-in converter.

    mammoth produces markdown that naturally preserves the document's
    semantic structure — headings become # / ## / ###, bold becomes **,
    lists become - items.  This output is ideal for heading-aware chunking.

    Returns (markdown_string, messages).
    """
    with open(doc_path, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    return result.value, [str(m) for m in result.messages]


# ===================================================================
# 3. Heading-aware chunking on markdown output
# ===================================================================


def chunk_markdown_by_headings(markdown_text: str) -> list[dict]:
    """
    Use the shared heading-aware chunker on mammoth's markdown output.

    Because mammoth already produces well-formed markdown with # headings,
    this works out of the box — no extra pre-processing needed.
    """
    return chunk_by_headings(markdown_text)


# ===================================================================
# Main demonstration
# ===================================================================


def main() -> None:
    print("=" * 70)
    print("DOCX Extraction with mammoth")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. HTML conversion
    # ------------------------------------------------------------------
    print("\n\n--- 1. DOCX -> HTML ---\n")
    html, html_msgs = docx_to_html(SAMPLE_DOC)

    print(f"HTML length: {len(html)} characters")
    if html_msgs:
        print(f"Conversion warnings ({len(html_msgs)}):")
        for msg in html_msgs[:5]:
            print(f"  - {msg}")
    else:
        print("No conversion warnings.")

    print("\nHTML output (first 800 chars):")
    print("-" * 50)
    print(html[:800])
    print("-" * 50)

    # ------------------------------------------------------------------
    # 2. Markdown conversion
    # ------------------------------------------------------------------
    print("\n\n--- 2. DOCX -> Markdown ---\n")
    markdown, md_msgs = docx_to_markdown(SAMPLE_DOC)

    print(f"Markdown length: {len(markdown)} characters")
    if md_msgs:
        print(f"Conversion warnings ({len(md_msgs)}):")
        for msg in md_msgs[:5]:
            print(f"  - {msg}")
    else:
        print("No conversion warnings.")

    print("\nMarkdown output (first 800 chars):")
    print("-" * 50)
    print(markdown[:800])
    print("-" * 50)

    # ------------------------------------------------------------------
    # 3. Side-by-side comparison
    # ------------------------------------------------------------------
    print("\n\n--- 3. HTML vs. Markdown Comparison ---\n")

    print(f"{'Metric':<30s} {'HTML':>12s} {'Markdown':>12s}")
    print("-" * 56)
    print(f"{'Total characters':<30s} {len(html):>12,d} {len(markdown):>12,d}")
    print(f"{'Lines':<30s} {len(html.splitlines()):>12,d} {len(markdown.splitlines()):>12,d}")

    # Count headings in each format
    html_headings = html.count("<h1>") + html.count("<h2>") + html.count("<h3>")
    md_headings = sum(1 for line in markdown.splitlines() if line.strip().startswith("#"))
    print(f"{'Heading elements':<30s} {html_headings:>12d} {md_headings:>12d}")

    # Count list items
    html_list_items = html.count("<li>")
    md_list_items = sum(
        1 for line in markdown.splitlines() if line.strip().startswith("- ") or line.strip().startswith("* ")
    )
    print(f"{'List items':<30s} {html_list_items:>12d} {md_list_items:>12d}")

    print("\nKey observations:")
    print("  - HTML is more verbose due to tags, but preserves semantic elements.")
    print("  - Markdown is more compact and human-readable.")
    print("  - Both preserve headings, bold, italic, and lists.")
    print("  - Markdown output is directly usable for heading-based RAG chunking.")
    print("  - HTML is better if you need to render or further parse with BeautifulSoup.")

    # ------------------------------------------------------------------
    # 4. Heading-aware chunking on markdown
    # ------------------------------------------------------------------
    print("\n\n--- 4. RAG-Ready Heading-Aware Chunks (from Markdown) ---\n")
    chunks = chunk_markdown_by_headings(markdown)
    preview_chunks(chunks, max_preview=4, max_chars=300)

    print("\nWhy mammoth's markdown is RAG-friendly:")
    print("  - Clean heading hierarchy maps directly to chunk boundaries.")
    print("  - Inline formatting (bold, italic) is preserved for context.")
    print("  - Lists are rendered as plain text, easy for embeddings.")
    print("  - No layout artifacts or noise from visual formatting.")


if __name__ == "__main__":
    main()
