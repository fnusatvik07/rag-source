"""
Marker - Specialized Converters
==================================
Besides the default PdfConverter, Marker provides specialized converters:

1. TableConverter - Extract only tables from documents
2. OCRConverter   - Force full OCR processing
3. ExtractionConverter - Structured data extraction with Pydantic schemas

uv pip install marker-pdf
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def table_converter_demo():
    """Extract only tables from a document."""
    try:
        from marker.converters.table import TableConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
    except ImportError:
        print("=" * 60)
        print("MARKER - TABLE CONVERTER")
        print("=" * 60)
        print("\nInstall: uv pip install marker-pdf")
        _show_table_example()
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    converter = TableConverter(artifact_dict=create_model_dict())
    rendered = converter(pdf_path)
    text, metadata, images = text_from_rendered(rendered)

    print("=" * 60)
    print("TABLE CONVERTER OUTPUT")
    print("=" * 60)
    print(text[:600])


def ocr_converter_demo():
    """Force OCR on entire document (for scanned PDFs)."""
    try:
        from marker.converters.ocr import OCRConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
    except ImportError:
        print("=" * 60)
        print("MARKER - OCR CONVERTER")
        print("=" * 60)
        print("\nInstall: uv pip install marker-pdf")
        print("""
from marker.converters.ocr import OCRConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = OCRConverter(artifact_dict=create_model_dict())
rendered = converter("scanned_document.pdf")
text, metadata, images = text_from_rendered(rendered)
print(text)  # OCR'd text as Markdown
""")
        return

    img_path = str(SAMPLES_DIR / "06_images_ocr" / "sample_docs" / "simple_text.png")

    converter = OCRConverter(artifact_dict=create_model_dict())
    rendered = converter(img_path)
    text, metadata, images = text_from_rendered(rendered)

    print("=" * 60)
    print("OCR CONVERTER OUTPUT")
    print("=" * 60)
    print(text)


def extraction_converter_demo():
    """Structured extraction with a Pydantic schema."""
    print("=" * 60)
    print("MARKER - STRUCTURED EXTRACTION")
    print("=" * 60)
    print("""
The ExtractionConverter lets you define a Pydantic schema and
extract structured data from documents using an LLM:

from marker.converters.extraction import ExtractionConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from pydantic import BaseModel

# Define what to extract
class InvoiceData(BaseModel):
    vendor_name: str
    invoice_number: str
    total_amount: float
    line_items: list[dict]

schema = InvoiceData.model_json_schema()
config_parser = ConfigParser({"page_schema": schema})

converter = ExtractionConverter(
    artifact_dict=create_model_dict(),
    config=config_parser.generate_config_dict(),
    llm_service=config_parser.get_llm_service(),  # Requires LLM config
)
rendered = converter("invoice.pdf")
# Returns structured JSON matching your schema
""")


def _show_table_example():
    print("""
from marker.converters.table import TableConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = TableConverter(artifact_dict=create_model_dict())
rendered = converter("document_with_tables.pdf")
text, metadata, images = text_from_rendered(rendered)

# Output contains ONLY the tables found in the document
print(text)
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Table converter")
    print("2. OCR converter")
    print("3. Structured extraction")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    {
        "1": table_converter_demo,
        "2": ocr_converter_demo,
        "3": extraction_converter_demo,
    }[choice]()
