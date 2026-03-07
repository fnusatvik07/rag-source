"""
PDF extraction using pdfplumber.

pdfplumber is built on top of pdfminer.six and provides fine-grained access
to text, characters, words, lines, rectangles, and tables within PDFs.

Strengths:  Excellent table detection/extraction, character-level access,
            layout-aware text extraction, detailed positional data.
Weaknesses: Slower than PyMuPDF, heavier dependency chain.

Usage:
    uv run python unstructured_documents/01_pdf/02_pdfplumber_extraction.py
"""

import sys
from pathlib import Path

import pdfplumber

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
SIMPLE_TEXT_PDF = SAMPLE_DIR / "simple_text.pdf"
TABLES_PDF = SAMPLE_DIR / "tables.pdf"


# ---------------------------------------------------------------------------
# 1. Text extraction with better formatting
# ---------------------------------------------------------------------------


def extract_text_with_layout(pdf_path: Path) -> list[dict]:
    """
    Extract text page by page, preserving layout spacing.

    pdfplumber's extract_text() uses positional data to reconstruct
    whitespace and layout, producing more readable output than basic
    extractors.
    """
    results = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # extract_text with layout settings for better column handling
            text_layout = (
                page.extract_text(
                    layout=True,  # Use layout-aware extraction
                    x_density=7.25,  # Horizontal character density
                    y_density=13,  # Vertical line density
                )
                or ""
            )
            results.append(
                {
                    "page": i + 1,
                    "text_default": text,
                    "text_layout": text_layout,
                    "width": float(page.width),
                    "height": float(page.height),
                }
            )
    return results


def demo_text_extraction():
    """Demonstrate text extraction with default and layout modes."""
    print("=" * 70)
    print("1. TEXT EXTRACTION (pdfplumber) - simple_text.pdf")
    print("=" * 70)

    pages = extract_text_with_layout(SIMPLE_TEXT_PDF)

    for page_info in pages[:2]:  # Show first 2 pages
        pn = page_info["page"]
        print(f"\n--- Page {pn} (size: {page_info['width']:.0f} x {page_info['height']:.0f}) ---")

        print(f"\n  [Default extraction] ({len(page_info['text_default'])} chars):")
        preview = page_info["text_default"][:400].strip()
        for line in preview.split("\n")[:8]:
            print(f"    {line}")
        if len(page_info["text_default"]) > 400:
            print("    ...")

        print(f"\n  [Layout extraction] ({len(page_info['text_layout'])} chars):")
        preview = page_info["text_layout"][:400].strip()
        for line in preview.split("\n")[:8]:
            print(f"    {line}")
        if len(page_info["text_layout"]) > 400:
            print("    ...")

    print(f"\nTotal pages: {len(pages)}")


# ---------------------------------------------------------------------------
# 2. Character-level and word-level extraction
# ---------------------------------------------------------------------------


def demo_character_level():
    """Show character-level and word-level data available via pdfplumber."""
    print("\n" + "=" * 70)
    print("2. CHARACTER-LEVEL & WORD-LEVEL EXTRACTION")
    print("=" * 70)

    with pdfplumber.open(str(SIMPLE_TEXT_PDF)) as pdf:
        page = pdf.pages[0]

        # Character-level data
        chars = page.chars
        print(f"\n  Total characters on page 1: {len(chars)}")
        print("\n  First 5 characters with metadata:")
        print(f"  {'Char':<6s} {'x0':>8s} {'y0':>8s} {'x1':>8s} {'y1':>8s} {'Font':<30s} {'Size':>6s}")
        print(f"  {'-' * 6} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 30} {'-' * 6}")
        for c in chars[:5]:
            print(
                f"  {repr(c['text']):<6s} {c['x0']:>8.2f} {c['top']:>8.2f} "
                f"{c['x1']:>8.2f} {c['bottom']:>8.2f} "
                f"{c.get('fontname', 'N/A'):<30s} {c.get('size', 0):>6.1f}"
            )

        # Word-level data
        words = page.extract_words()
        print(f"\n  Total words on page 1: {len(words)}")
        print("\n  First 10 words with bounding boxes:")
        print(f"  {'Word':<20s} {'x0':>8s} {'top':>8s} {'x1':>8s} {'bottom':>8s}")
        print(f"  {'-' * 20} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8}")
        for w in words[:10]:
            text = w["text"][:20]
            print(f"  {text:<20s} {w['x0']:>8.2f} {w['top']:>8.2f} {w['x1']:>8.2f} {w['bottom']:>8.2f}")


# ---------------------------------------------------------------------------
# 3. Table detection and extraction
# ---------------------------------------------------------------------------


def extract_tables_from_pdf(pdf_path: Path) -> list[dict]:
    """
    Detect and extract all tables from a PDF.

    pdfplumber identifies tables by analysing lines and edges on each page.
    Returns a list of dicts with page number, table index, and cell data.
    """
    tables = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for j, table in enumerate(page_tables):
                tables.append(
                    {
                        "page": i + 1,
                        "table_index": j,
                        "data": table,  # list of rows, each row is a list of cells
                        "num_rows": len(table),
                        "num_cols": len(table[0]) if table else 0,
                    }
                )
    return tables


def demo_table_extraction():
    """Demonstrate table detection and extraction from tables.pdf."""
    print("\n" + "=" * 70)
    print("3. TABLE DETECTION & EXTRACTION (pdfplumber) - tables.pdf")
    print("=" * 70)

    tables = extract_tables_from_pdf(TABLES_PDF)
    print(f"\n  Tables found: {len(tables)}")

    for t in tables:
        pn = t["page"]
        ti = t["table_index"]
        nr = t["num_rows"]
        nc = t["num_cols"]
        print(f"\n  --- Page {pn}, Table {ti + 1}: {nr} rows x {nc} cols ---")

        # Print header row
        if t["data"]:
            header = t["data"][0]
            print(f"  Header: {header}")

        # Print first few data rows
        for row in t["data"][1:4]:
            print(f"  Row:    {row}")
        if nr > 4:
            print(f"  ... ({nr - 4} more rows)")


def demo_table_settings():
    """Show how pdfplumber table detection settings affect results."""
    print("\n" + "=" * 70)
    print("4. TABLE DETECTION SETTINGS")
    print("=" * 70)

    with pdfplumber.open(str(TABLES_PDF)) as pdf:
        page = pdf.pages[0]

        # Default settings
        default_tables = page.extract_tables()
        print(f"\n  Default settings:  {len(default_tables)} table(s) found")

        # Custom settings for more aggressive table detection
        custom_settings = {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "snap_tolerance": 5,
            "join_tolerance": 5,
            "min_words_vertical": 3,
            "min_words_horizontal": 1,
        }
        custom_tables = page.extract_tables(table_settings=custom_settings)
        print(f"  Custom settings:   {len(custom_tables)} table(s) found")

        # Show table finder debug info
        table_finder = page.debug_tablefinder()
        print("\n  Table finder debug:")
        print(f"    Tables detected: {len(table_finder.tables)}")
        for idx, tbl in enumerate(table_finder.tables):
            bbox = tbl.bbox
            print(
                f"    Table {idx + 1} bbox: x0={bbox[0]:.1f}, top={bbox[1]:.1f}, x1={bbox[2]:.1f}, bottom={bbox[3]:.1f}"
            )


if __name__ == "__main__":
    missing = []
    if not SIMPLE_TEXT_PDF.exists():
        missing.append(str(SIMPLE_TEXT_PDF))
    if not TABLES_PDF.exists():
        missing.append(str(TABLES_PDF))

    if missing:
        print("ERROR: Missing sample PDF(s):")
        for m in missing:
            print(f"  {m}")
        print("\nRun generate_samples.py first:")
        print("  uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py")
        sys.exit(1)

    demo_text_extraction()
    demo_character_level()
    demo_table_extraction()
    demo_table_settings()

    print("\n" + "=" * 70)
    print("Done. pdfplumber excels at structured extraction and tables.")
    print("For faster extraction, see 03_pymupdf_extraction.py")
    print("For dedicated table work, see 04_table_extraction.py")
    print("=" * 70)
