"""
Unstructured.io - Auto Partition
==================================
The partition() function from unstructured.partition.auto automatically
detects the file type and routes to the correct parser.

It returns a list of Element objects (Title, NarrativeText, Table,
ListItem, Image, etc.) that represent the document's structure.

uv pip install "unstructured[all-docs]"
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def auto_partition_pdf():
    """Partition a PDF using auto-detection."""
    from unstructured.partition.auto import partition

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf")
    elements = partition(filename=pdf_path)

    print("=" * 60)
    print(f"AUTO PARTITION PDF - {len(elements)} elements")
    print("=" * 60)

    for el in elements:
        print(f"\n[{type(el).__name__}]")
        print(f"  Text: {str(el)[:150]}")
        if hasattr(el, "metadata"):
            if el.metadata.page_number:
                print(f"  Page: {el.metadata.page_number}")


def auto_partition_multiple():
    """Partition multiple file types using the same function."""
    from unstructured.partition.auto import partition

    files = [
        ("PDF", SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"),
        ("DOCX", SAMPLES_DIR / "02_docx" / "sample_docs" / "simple_document.docx"),
        ("HTML", SAMPLES_DIR / "04_html" / "sample_docs" / "article_page.html"),
        ("PPTX", SAMPLES_DIR / "03_pptx" / "sample_docs" / "presentation.pptx"),
        ("Email", SAMPLES_DIR / "07_email" / "sample_docs" / "plain_text.eml"),
        (
            "Markdown",
            SAMPLES_DIR / "08_markdown_txt" / "sample_docs" / "technical_doc.md",
        ),
        ("EPUB", SAMPLES_DIR / "09_epub" / "sample_docs" / "sample_book.epub"),
    ]

    for label, path in files:
        if not path.exists():
            print(f"[SKIP] {label}: not found")
            continue
        elements = partition(filename=str(path))
        print(f"\n{'=' * 60}")
        print(f"{label}: {path.name} -> {len(elements)} elements")
        print(f"{'=' * 60}")

        # Show element type distribution
        from collections import Counter

        type_counts = Counter(type(el).__name__ for el in elements)
        for etype, count in type_counts.most_common():
            print(f"  {etype}: {count}")

        # Show first 3 elements
        for el in elements[:3]:
            print(f"  [{type(el).__name__}] {str(el)[:100]}")


def element_types_overview():
    """Show all element types that Unstructured can produce."""
    from unstructured.partition.auto import partition

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf")
    elements = partition(filename=pdf_path)

    print("=" * 60)
    print("ELEMENT TYPES OVERVIEW")
    print("=" * 60)
    print("""
Unstructured returns typed Element objects:

  Title          - Document headings and titles
  NarrativeText  - Body paragraphs and flowing text
  Table          - Tabular data (with .metadata.text_as_html)
  ListItem       - Bulleted or numbered list items
  Image          - Image descriptions or OCR'd text from images
  Header         - Page headers
  Footer         - Page footers
  PageBreak      - Page boundary markers
  Address        - Postal/email addresses
  EmailAddress   - Email addresses specifically
  FigureCaption  - Captions for figures
  Formula        - Mathematical formulas
  UncategorizedText - Text that doesn't fit other categories
""")

    from collections import Counter

    type_counts = Counter(type(el).__name__ for el in elements)
    print(f"Found in this document ({len(elements)} elements):")
    for etype, count in type_counts.most_common():
        print(f"  {etype}: {count}")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Auto partition PDF")
    print("2. Auto partition multiple formats")
    print("3. Element types overview")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    {
        "1": auto_partition_pdf,
        "2": auto_partition_multiple,
        "3": element_types_overview,
    }[choice]()
