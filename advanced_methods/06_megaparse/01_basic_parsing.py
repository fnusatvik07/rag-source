"""
MegaParse - Basic Document Parsing
=====================================
MegaParse (by Quivr) is an open-source document parser optimized for
LLM ingestion with minimal information loss. It converts PDF, DOCX,
PPTX, XLSX, CSV, and text files into clean Markdown.

Key design goals:
- Zero information loss during parsing
- Speed and efficiency
- Simple API: load() -> markdown string

Supported formats: PDF, DOCX, PPTX, XLSX, CSV, TXT
Output: Markdown text (optimized for LLM consumption)

Requirements: Python >= 3.11, poppler, tesseract-ocr
uv pip install megaparse
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def basic_parse():
    """Parse a PDF using MegaParse's simple API."""
    try:
        from megaparse import MegaParse
    except ImportError:
        print("=" * 60)
        print("MEGAPARSE - BASIC DOCUMENT PARSING")
        print("=" * 60)
        print("\nInstall: uv pip install megaparse")
        print("System deps: poppler, tesseract-ocr, libmagic")
        print("  macOS: brew install poppler tesseract libmagic")
        print("  Ubuntu: apt install poppler-utils tesseract-ocr libmagic-dev")
        _show_basic_example()
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    print("=" * 60)
    print("MEGAPARSE - BASIC PDF PARSING")
    print("=" * 60)

    megaparse = MegaParse()
    response = megaparse.load(pdf_path)

    print(f"\nOutput ({len(response)} chars):")
    print(response[:800])


def parse_multiple_formats():
    """Parse different file types with MegaParse."""
    try:
        from megaparse import MegaParse
    except ImportError:
        print("Install: uv pip install megaparse")
        print("\nMegaParse supports: PDF, DOCX, PPTX, XLSX, CSV, TXT")
        print("All use the same simple API: megaparse.load(filepath)")
        return

    megaparse = MegaParse()

    files = [
        ("PDF", SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"),
        ("DOCX", SAMPLES_DIR / "02_docx" / "sample_docs" / "simple_document.docx"),
        ("PPTX", SAMPLES_DIR / "03_pptx" / "sample_docs" / "presentation.pptx"),
        ("XLSX", SAMPLES_DIR / "05_spreadsheets" / "sample_docs" / "multi_sheet.xlsx"),
    ]

    for label, path in files:
        if not path.exists():
            print(f"[SKIP] {label}: {path.name} not found")
            continue
        print(f"\n{'=' * 60}")
        print(f"PARSING {label}: {path.name}")
        print(f"{'=' * 60}")
        try:
            response = megaparse.load(str(path))
            print(f"Output: {len(response)} chars")
            print(response[:300] + "..." if len(response) > 300 else response)
        except Exception as e:
            print(f"Error: {e}")


def _show_basic_example():
    print("""
# MegaParse has the simplest API of any document parser:

from megaparse import MegaParse

megaparse = MegaParse()

# Parse any supported file type
response = megaparse.load("document.pdf")
print(response)  # Clean Markdown output

# Works with DOCX, PPTX, XLSX too
response = megaparse.load("presentation.pptx")
print(response)

# The output is Markdown optimized for LLM consumption:
# - Tables preserved as Markdown tables
# - Headers/footers handled
# - Images described
# - Table of contents extracted
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Basic PDF parsing")
    print("2. Multiple formats")
    choice = input("Enter 1/2 (default=1): ").strip() or "1"

    if choice == "1":
        basic_parse()
    else:
        parse_multiple_formats()
