"""
Compare PDF extraction methods side by side.

Runs pypdf, pdfplumber, and PyMuPDF on the same PDFs and compares:
  - Text output length and content
  - Extraction speed
  - First 500 characters of output

Also compares table extraction approaches on tables.pdf.

Usage:
    uv run python unstructured_documents/01_pdf/06_comparison.py
"""

import sys
import time
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
from pypdf import PdfReader
from tabulate import tabulate

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
SIMPLE_TEXT_PDF = SAMPLE_DIR / "simple_text.pdf"
TABLES_PDF = SAMPLE_DIR / "tables.pdf"
MIXED_CONTENT_PDF = SAMPLE_DIR / "mixed_content.pdf"


# ---------------------------------------------------------------------------
# Extraction wrappers
# ---------------------------------------------------------------------------


def extract_pypdf(pdf_path: Path) -> str:
    """Extract text using pypdf."""
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def extract_pdfplumber(pdf_path: Path) -> str:
    """Extract text using pdfplumber (default mode)."""
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n\n".join(pages)


def extract_pdfplumber_layout(pdf_path: Path) -> str:
    """Extract text using pdfplumber (layout mode)."""
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text(layout=True) or ""
            pages.append(text)
    return "\n\n".join(pages)


def extract_pymupdf(pdf_path: Path) -> str:
    """Extract text using PyMuPDF."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text()
        pages.append(text)
    doc.close()
    return "\n\n".join(pages)


def extract_pymupdf_sorted(pdf_path: Path) -> str:
    """Extract text using PyMuPDF with sort=True for reading order."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text("text", sort=True)
        pages.append(text)
    doc.close()
    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# Timing utility
# ---------------------------------------------------------------------------


def time_extraction(func, pdf_path: Path, runs: int = 5) -> tuple[str, float]:
    """Run an extraction function multiple times and return text + avg time."""
    times = []
    text = ""
    for _ in range(runs):
        start = time.perf_counter()
        text = func(pdf_path)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    avg_ms = (sum(times) / len(times)) * 1000
    return text, avg_ms


# ---------------------------------------------------------------------------
# 1. Text extraction comparison
# ---------------------------------------------------------------------------


def compare_text_extraction():
    """Compare all methods on simple_text.pdf."""
    print("=" * 70)
    print("1. TEXT EXTRACTION COMPARISON - simple_text.pdf")
    print("=" * 70)

    methods = [
        ("pypdf", extract_pypdf),
        ("pdfplumber", extract_pdfplumber),
        ("pdfplumber (layout)", extract_pdfplumber_layout),
        ("PyMuPDF", extract_pymupdf),
        ("PyMuPDF (sorted)", extract_pymupdf_sorted),
    ]

    results = []
    texts = {}
    for name, func in methods:
        text, avg_ms = time_extraction(func, SIMPLE_TEXT_PDF, runs=5)
        word_count = len(text.split())
        line_count = len(text.strip().split("\n"))
        results.append(
            {
                "Method": name,
                "Chars": f"{len(text):,}",
                "Words": f"{word_count:,}",
                "Lines": f"{line_count:,}",
                "Avg Time (ms)": f"{avg_ms:.1f}",
            }
        )
        texts[name] = text

    # Print comparison table
    print(f"\n{tabulate(results, headers='keys', tablefmt='grid')}")

    # Show first 500 chars from each method
    print("\n" + "-" * 70)
    print("FIRST 500 CHARACTERS FROM EACH METHOD:")
    print("-" * 70)
    for name, text in texts.items():
        print(f"\n  --- {name} ---")
        preview = text[:500].strip()
        for line in preview.split("\n")[:10]:
            print(f"    {line}")
        if len(text) > 500:
            print("    ...")


# ---------------------------------------------------------------------------
# 2. Table extraction comparison
# ---------------------------------------------------------------------------


def compare_table_extraction():
    """Compare table extraction on tables.pdf."""
    print("\n" + "=" * 70)
    print("2. TABLE EXTRACTION COMPARISON - tables.pdf")
    print("=" * 70)

    # --- pdfplumber table extraction ---
    print("\n  --- pdfplumber: extract_tables() ---")
    start = time.perf_counter()
    with pdfplumber.open(str(TABLES_PDF)) as pdf:
        plumber_tables = []
        for page in pdf.pages:
            page_tables = page.extract_tables()
            plumber_tables.extend(page_tables)
    plumber_time = (time.perf_counter() - start) * 1000

    print(f"  Tables found: {len(plumber_tables)}")
    print(f"  Time: {plumber_time:.1f} ms")
    for i, table in enumerate(plumber_tables):
        if table:
            print(f"  Table {i + 1}: {len(table)} rows x {len(table[0])} cols")
            print(f"    Header: {table[0]}")

    # --- pdfplumber with custom settings ---
    print("\n  --- pdfplumber: extract_tables() with text strategy ---")
    start = time.perf_counter()
    with pdfplumber.open(str(TABLES_PDF)) as pdf:
        custom_tables = []
        for page in pdf.pages:
            settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
            }
            page_tables = page.extract_tables(table_settings=settings)
            custom_tables.extend(page_tables)
    custom_time = (time.perf_counter() - start) * 1000

    print(f"  Tables found: {len(custom_tables)}")
    print(f"  Time: {custom_time:.1f} ms")
    for i, table in enumerate(custom_tables):
        if table:
            print(f"  Table {i + 1}: {len(table)} rows x {len(table[0])} cols")

    # --- PyMuPDF text extraction on table PDF (for comparison) ---
    print("\n  --- PyMuPDF: text extraction on tables.pdf ---")
    start = time.perf_counter()
    doc = fitz.open(str(TABLES_PDF))
    mupdf_text = "\n".join(page.get_text() for page in doc)
    doc.close()
    mupdf_time = (time.perf_counter() - start) * 1000

    print(f"  Text extracted: {len(mupdf_text):,} chars")
    print(f"  Time: {mupdf_time:.1f} ms")
    print("  Note: PyMuPDF extracts table content as text but does not")
    print("  detect table structure (rows/columns). Use pdfplumber for that.")

    # Summary table
    print("\n  --- Table Extraction Summary ---")
    summary = [
        {
            "Method": "pdfplumber (default)",
            "Tables Found": len(plumber_tables),
            "Time (ms)": f"{plumber_time:.1f}",
            "Structured": "Yes",
        },
        {
            "Method": "pdfplumber (text strategy)",
            "Tables Found": len(custom_tables),
            "Time (ms)": f"{custom_time:.1f}",
            "Structured": "Yes",
        },
        {
            "Method": "PyMuPDF (text only)",
            "Tables Found": "N/A",
            "Time (ms)": f"{mupdf_time:.1f}",
            "Structured": "No",
        },
    ]
    print(f"\n{tabulate(summary, headers='keys', tablefmt='grid')}")


# ---------------------------------------------------------------------------
# 3. Mixed content comparison
# ---------------------------------------------------------------------------


def compare_mixed_content():
    """Compare methods on mixed_content.pdf (text + tables + bullets)."""
    print("\n" + "=" * 70)
    print("3. MIXED CONTENT COMPARISON - mixed_content.pdf")
    print("=" * 70)

    if not MIXED_CONTENT_PDF.exists():
        print(f"  Skipped: {MIXED_CONTENT_PDF} not found.")
        return

    methods = [
        ("pypdf", extract_pypdf),
        ("pdfplumber", extract_pdfplumber),
        ("PyMuPDF", extract_pymupdf),
    ]

    results = []
    for name, func in methods:
        text, avg_ms = time_extraction(func, MIXED_CONTENT_PDF, runs=5)
        results.append(
            {
                "Method": name,
                "Chars": f"{len(text):,}",
                "Words": f"{len(text.split()):,}",
                "Time (ms)": f"{avg_ms:.1f}",
            }
        )

    print(f"\n{tabulate(results, headers='keys', tablefmt='grid')}")

    # Check if pdfplumber detects tables in mixed content
    with pdfplumber.open(str(MIXED_CONTENT_PDF)) as pdf:
        table_count = sum(len(page.extract_tables()) for page in pdf.pages)
    print(f"\n  pdfplumber detected {table_count} table(s) in mixed_content.pdf")


# ---------------------------------------------------------------------------
# 4. Recommendation summary
# ---------------------------------------------------------------------------


def print_recommendations():
    """Print a summary of when to use each method."""
    print("\n" + "=" * 70)
    print("4. RECOMMENDATION SUMMARY")
    print("=" * 70)

    rec_table = [
        {
            "Use Case": "Simple text extraction",
            "Recommended": "PyMuPDF",
            "Why": "Fastest, reliable text output",
        },
        {
            "Use Case": "Table extraction",
            "Recommended": "pdfplumber",
            "Why": "Best table detection and structure",
        },
        {
            "Use Case": "Layout preservation",
            "Recommended": "pdfplumber (layout) or PyMuPDF (sorted)",
            "Why": "Respects spatial positioning",
        },
        {
            "Use Case": "Font/style analysis",
            "Recommended": "PyMuPDF (dict mode)",
            "Why": "Detailed font info per span",
        },
        {
            "Use Case": "Scanned PDFs",
            "Recommended": "pytesseract + pdf2image",
            "Why": "Only option for image-based PDFs",
        },
        {
            "Use Case": "Minimal dependencies",
            "Recommended": "pypdf",
            "Why": "Pure Python, no C extensions",
        },
        {
            "Use Case": "RAG pipeline (general)",
            "Recommended": "PyMuPDF + pdfplumber",
            "Why": "Fast text + reliable tables",
        },
        {
            "Use Case": "Production at scale",
            "Recommended": "PyMuPDF",
            "Why": "Best performance, low memory",
        },
    ]

    print(f"\n{tabulate(rec_table, headers='keys', tablefmt='grid')}")

    print("""
  Decision tree:
    1. Is the PDF scanned / image-based?
       -> Yes: Use OCR (pytesseract + pdf2image)
       -> No: Continue to step 2

    2. Does the PDF contain tables you need to extract?
       -> Yes: Use pdfplumber for tables
       -> No: Continue to step 3

    3. Do you need the fastest extraction?
       -> Yes: Use PyMuPDF
       -> No: Use pypdf (simplest) or pdfplumber (most features)
""")


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

    compare_text_extraction()
    compare_table_extraction()
    compare_mixed_content()
    print_recommendations()

    print("\n" + "=" * 70)
    print("Done. See individual scripts (01-05) for detailed usage of each method.")
    print("=" * 70)
