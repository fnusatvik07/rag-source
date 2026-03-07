"""
LlamaParse - Basic Document Parsing
======================================
LlamaParse is a cloud-based GenAI-native document parser by LlamaIndex.
It uses multimodal AI models to parse complex documents into clean,
structured formats optimized for RAG systems.

Key features:
- Handles PDF, DOCX, PPTX, XLSX, HTML and 10+ more formats
- AI-powered table extraction and reconstruction
- Image/chart understanding via multimodal models
- Multiple output formats: markdown, text, JSON
- Multiple parsing tiers: fast, agentic, agentic_plus

Requires: LlamaCloud API key (free tier: 1000 pages/day)
Get API key at: https://cloud.llamaindex.ai/

uv pip install llama-parse
# OR newer:
uv pip install llama-cloud>=1.0
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def basic_parse_pdf():
    """Parse a PDF using LlamaParse with default settings."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")

    if not api_key:
        print("=" * 60)
        print("LLAMAPARSE - BASIC PDF PARSING")
        print("=" * 60)
        print("\nRequires LlamaCloud API key:")
        print("  1. Sign up at https://cloud.llamaindex.ai/")
        print("  2. Get API key from dashboard")
        print("  3. export LLAMA_CLOUD_API_KEY='llx-...'")
        print("\nFree tier: 1000 pages/day")
        _show_basic_example()
        return

    try:
        from llama_parse import LlamaParse
    except ImportError:
        print("Install: uv pip install llama-parse")
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",  # "markdown", "text", or "json"
    )

    print("=" * 60)
    print("LLAMAPARSE - BASIC PDF PARSING")
    print("=" * 60)

    documents = parser.load_data(pdf_path)

    for i, doc in enumerate(documents):
        print(f"\n--- Document {i + 1} ---")
        print(f"Text length: {len(doc.text)}")
        print(f"Preview:\n{doc.text[:500]}")


def parse_with_options():
    """Parse with advanced options: language, page selection, etc."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")

    if not api_key:
        print("=" * 60)
        print("LLAMAPARSE - ADVANCED OPTIONS")
        print("=" * 60)
        _show_advanced_example()
        return

    try:
        from llama_parse import LlamaParse
    except ImportError:
        print("Install: uv pip install llama-parse")
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf")

    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",
        language="en",
        parsing_instruction="Extract all text, tables, and lists. Preserve heading hierarchy.",
        skip_diagonal_text=True,
        do_not_unroll_columns=False,
    )

    print("Parsing with custom instructions...")
    documents = parser.load_data(pdf_path)

    for doc in documents:
        print(f"\nParsed ({len(doc.text)} chars):")
        print(doc.text[:600])


def parse_multiple_formats():
    """Parse different file types with LlamaParse."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")

    if not api_key:
        print("=" * 60)
        print("LLAMAPARSE - MULTIPLE FORMATS")
        print("=" * 60)
        print("\nLlamaParse supports: PDF, DOCX, PPTX, XLSX, HTML, CSV, RTF,")
        print("EPUB, XML, and images (PNG, JPG, BMP, TIFF, HEIC)")
        print("\nSet LLAMA_CLOUD_API_KEY to run this demo.")
        return

    try:
        from llama_parse import LlamaParse
    except ImportError:
        print("Install: uv pip install llama-parse")
        return

    parser = LlamaParse(api_key=api_key, result_type="markdown")

    files = [
        ("PDF", SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"),
        ("DOCX", SAMPLES_DIR / "02_docx" / "sample_docs" / "simple_document.docx"),
        ("PPTX", SAMPLES_DIR / "03_pptx" / "sample_docs" / "presentation.pptx"),
    ]

    for label, path in files:
        if not path.exists():
            continue
        print(f"\n{'=' * 60}")
        print(f"PARSING {label}: {path.name}")
        print(f"{'=' * 60}")
        docs = parser.load_data(str(path))
        for doc in docs:
            print(f"  Output: {len(doc.text)} chars")
            print(f"  Preview: {doc.text[:200]}...")


def _show_basic_example():
    print("""
from llama_parse import LlamaParse

parser = LlamaParse(
    api_key="llx-...",
    result_type="markdown",   # "markdown", "text", or "json"
)

# Parse a single file
documents = parser.load_data("document.pdf")
for doc in documents:
    print(doc.text)       # Extracted content
    print(doc.metadata)   # File metadata

# Parse from URL
documents = parser.load_data("https://example.com/paper.pdf")
""")


def _show_advanced_example():
    print("""
parser = LlamaParse(
    api_key="llx-...",
    result_type="markdown",

    # Parsing options
    language="en",                    # Document language
    parsing_instruction="...",        # Custom instructions for the AI
    skip_diagonal_text=True,          # Skip watermarks/diagonal text
    do_not_unroll_columns=False,      # Handle multi-column layouts
    page_separator="\\n---\\n",       # Custom page separator

    # Output options
    show_progress=True,               # Show parsing progress
    invalidate_cache=False,           # Use cached results if available

    # Table options
    # result_type="json" gives structured table data
)
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Basic PDF parsing")
    print("2. Advanced options")
    print("3. Multiple formats")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    {"1": basic_parse_pdf, "2": parse_with_options, "3": parse_multiple_formats}[choice]()
