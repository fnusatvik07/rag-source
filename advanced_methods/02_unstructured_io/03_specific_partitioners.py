"""
Unstructured.io - Format-Specific Partitioners
================================================
Besides the universal partition(), Unstructured provides dedicated
partitioners for each format with type-specific parameters:

  partition_pdf()   - PDF with strategy selection
  partition_docx()  - Word documents
  partition_pptx()  - PowerPoint presentations
  partition_html()  - HTML pages
  partition_xlsx()  - Excel spreadsheets
  partition_email() - .eml email files
  partition_epub()  - EPUB ebooks
  partition_md()    - Markdown files
  partition_image() - Images (PNG, JPG, TIFF)
  partition_csv()   - CSV files

uv pip install "unstructured[all-docs]"
"""

from collections import Counter
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def show_elements(label, elements, max_show=5):
    """Helper to display partition results."""
    print(f"\n{'=' * 60}")
    print(f"{label} -> {len(elements)} elements")
    print(f"{'=' * 60}")
    types = Counter(type(el).__name__ for el in elements)
    print(f"Types: {dict(types)}")
    for el in elements[:max_show]:
        print(f"  [{type(el).__name__}] {str(el)[:120]}")


def partition_docx_demo():
    """Parse Word documents preserving headings, lists, and tables."""
    from unstructured.partition.docx import partition_docx

    path = str(SAMPLES_DIR / "02_docx" / "sample_docs" / "tables_document.docx")
    elements = partition_docx(filename=path)
    show_elements("DOCX (tables_document.docx)", elements)


def partition_pptx_demo():
    """Parse PowerPoint extracting text from all slides."""
    from unstructured.partition.pptx import partition_pptx

    path = str(SAMPLES_DIR / "03_pptx" / "sample_docs" / "presentation.pptx")
    elements = partition_pptx(filename=path)
    show_elements("PPTX (presentation.pptx)", elements)


def partition_html_demo():
    """Parse HTML with automatic boilerplate removal."""
    from unstructured.partition.html import partition_html

    path = str(SAMPLES_DIR / "04_html" / "sample_docs" / "article_page.html")
    elements = partition_html(filename=path)
    show_elements("HTML (article_page.html)", elements)


def partition_xlsx_demo():
    """Parse Excel spreadsheets with sheet-aware extraction."""
    from unstructured.partition.xlsx import partition_xlsx

    path = str(SAMPLES_DIR / "05_spreadsheets" / "sample_docs" / "multi_sheet.xlsx")
    elements = partition_xlsx(filename=path)
    show_elements("XLSX (multi_sheet.xlsx)", elements)


def partition_email_demo():
    """Parse email .eml files extracting headers, body, and attachments."""
    from unstructured.partition.email import partition_email

    path = str(SAMPLES_DIR / "07_email" / "sample_docs" / "html_email.eml")
    elements = partition_email(filename=path)
    show_elements("EMAIL (html_email.eml)", elements)

    # Show email-specific metadata
    for el in elements[:1]:
        meta = el.metadata
        if hasattr(meta, "sent_from") and meta.sent_from:
            print(f"  From: {meta.sent_from}")
        if hasattr(meta, "sent_to") and meta.sent_to:
            print(f"  To: {meta.sent_to}")
        if hasattr(meta, "subject") and meta.subject:
            print(f"  Subject: {meta.subject}")


def partition_epub_demo():
    """Parse EPUB ebooks with chapter-aware extraction."""
    from unstructured.partition.epub import partition_epub

    path = str(SAMPLES_DIR / "09_epub" / "sample_docs" / "sample_book.epub")
    elements = partition_epub(filename=path)
    show_elements("EPUB (sample_book.epub)", elements)


def partition_image_demo():
    """Parse images using OCR."""
    from unstructured.partition.image import partition_image

    path = str(SAMPLES_DIR / "06_images_ocr" / "sample_docs" / "simple_text.png")
    elements = partition_image(filename=path)
    show_elements("IMAGE (simple_text.png)", elements)


if __name__ == "__main__":
    demos = {
        "1": ("DOCX", partition_docx_demo),
        "2": ("PPTX", partition_pptx_demo),
        "3": ("HTML", partition_html_demo),
        "4": ("XLSX", partition_xlsx_demo),
        "5": ("Email", partition_email_demo),
        "6": ("EPUB", partition_epub_demo),
        "7": ("Image", partition_image_demo),
    }

    print("Choose partitioner:")
    for k, (label, _) in demos.items():
        print(f"  {k}. {label}")
    choice = input("Enter 1-7 (default=1): ").strip() or "1"
    demos.get(choice, demos["1"])[1]()
