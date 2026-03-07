"""
Docling - Basic Document Conversion
====================================
Docling (by IBM) provides a unified interface to convert documents of various
formats into a structured DoclingDocument representation, then export to
Markdown, JSON, HTML, or plain text.

Key concept: DocumentConverter accepts file paths or URLs and returns a
ConversionResult containing a DoclingDocument with full structure preserved.

uv pip install docling
"""

from pathlib import Path

# Reference sample docs from the documents folder
SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def convert_single_document():
    """Convert a single PDF to markdown using default settings."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"

    result = converter.convert(str(pdf_path))

    print("=" * 60)
    print("DOCLING: Basic PDF to Markdown")
    print("=" * 60)
    print(f"Status: {result.status}")
    print("\n--- Markdown Output ---\n")
    print(result.document.export_to_markdown())


def convert_multiple_formats():
    """Convert multiple document types showing Docling's format support."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()

    files = [
        ("PDF", SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf"),
        ("DOCX", SAMPLES_DIR / "02_docx" / "sample_docs" / "simple_document.docx"),
        ("PPTX", SAMPLES_DIR / "03_pptx" / "sample_docs" / "presentation.pptx"),
        ("HTML", SAMPLES_DIR / "04_html" / "sample_docs" / "article_page.html"),
    ]

    for label, path in files:
        if not path.exists():
            print(f"[SKIP] {label}: {path.name} not found")
            continue
        print(f"\n{'=' * 60}")
        print(f"CONVERTING {label}: {path.name}")
        print(f"{'=' * 60}")
        result = converter.convert(str(path))
        md = result.document.export_to_markdown()
        # Show first 500 chars
        preview = md[:500] + "..." if len(md) > 500 else md
        print(preview)


def export_formats():
    """Demonstrate all export formats: Markdown, JSON, text, HTML, DocTags."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"
    result = converter.convert(str(pdf_path))
    doc = result.document

    print("=" * 60)
    print("EXPORT FORMAT COMPARISON")
    print("=" * 60)

    # Markdown
    md = doc.export_to_markdown()
    print(f"\n--- Markdown ({len(md)} chars) ---")
    print(md[:300])

    # Plain text
    text = doc.export_to_text()
    print(f"\n--- Plain Text ({len(text)} chars) ---")
    print(text[:300])

    # JSON (lossless serialization)
    json_str = doc.model_dump_json(indent=2)
    print(f"\n--- JSON ({len(json_str)} chars) ---")
    print(json_str[:400] + "...")

    # Document tags
    try:
        doctags = doc.export_to_document_tokens()
        print(f"\n--- DocTags ({len(doctags)} chars) ---")
        print(doctags[:300])
    except Exception as e:
        print(f"\n--- DocTags: {e} ---")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Single PDF conversion")
    print("2. Multiple format conversion")
    print("3. Export format comparison")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    if choice == "1":
        convert_single_document()
    elif choice == "2":
        convert_multiple_formats()
    elif choice == "3":
        export_formats()
