"""
Marker - Basic PDF to Markdown Conversion
============================================
Marker converts PDF (and other formats) to clean Markdown, JSON, or HTML.
It uses a pipeline of AI models:
  1. Layout detection (identifies text blocks, tables, figures, equations)
  2. OCR (for scanned content)
  3. Table recognition
  4. Equation detection (LaTeX output)
  5. Post-processing (header/footer removal, reading order)

Supports: PDF, images, PPTX, DOCX, XLSX, HTML, EPUB
Output: Markdown, JSON, HTML, chunks

uv pip install marker-pdf
uv pip install marker-pdf[full]  # for DOCX, PPTX, XLSX support
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def basic_pdf_to_markdown():
    """Convert a PDF to Markdown using Marker's default pipeline."""
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
    except ImportError:
        print("=" * 60)
        print("MARKER - PDF TO MARKDOWN")
        print("=" * 60)
        print("\nInstall: uv pip install marker-pdf")
        print("Requires PyTorch (CPU or GPU)")
        _show_basic_example()
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    print("=" * 60)
    print("MARKER - PDF TO MARKDOWN")
    print("=" * 60)
    print("Loading models (first run downloads ~1.5GB)...")

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(pdf_path)
    text, metadata, images = text_from_rendered(rendered)

    print(f"\n--- Markdown Output ({len(text)} chars) ---")
    print(text[:800])

    print("\n--- Metadata ---")
    for key, val in metadata.items():
        print(f"  {key}: {val}")

    if images:
        print(f"\n--- Images: {len(images)} extracted ---")


def convert_with_config():
    """Convert with custom configuration: output format, page range, etc."""
    try:
        from marker.config.parser import ConfigParser
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
    except ImportError:
        print("Install: uv pip install marker-pdf")
        _show_config_example()
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf")

    # Custom configuration
    config = {
        "output_format": "markdown",
        "page_range": "0-2",  # First 3 pages only
        "force_ocr": False,
        "disable_image_extraction": True,
    }
    config_parser = ConfigParser(config)

    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
    )

    print("=" * 60)
    print("MARKER - CUSTOM CONFIGURATION")
    print("=" * 60)

    rendered = converter(pdf_path)
    text, metadata, images = text_from_rendered(rendered)
    print(f"Output ({len(text)} chars):")
    print(text[:600])


def _show_basic_example():
    print("""
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Load models (cached after first download)
converter = PdfConverter(artifact_dict=create_model_dict())

# Convert PDF
rendered = converter("document.pdf")
text, metadata, images = text_from_rendered(rendered)

print(text)       # Clean Markdown
print(metadata)   # Page stats, block counts, TOC
print(images)     # Dict of image_name -> PIL.Image
""")


def _show_config_example():
    print("""
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

config = {
    "output_format": "json",         # "markdown", "json", "html", "chunks"
    "page_range": "0,5-10,20",       # Specific pages
    "force_ocr": True,               # Force OCR on entire document
    "disable_image_extraction": False,
    "use_llm": True,                 # Use LLM for enhanced accuracy
}

config_parser = ConfigParser(config)
converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service(),
)
rendered = converter("document.pdf")
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Basic PDF to Markdown")
    print("2. Custom configuration")
    choice = input("Enter 1/2 (default=1): ").strip() or "1"

    if choice == "1":
        basic_pdf_to_markdown()
    else:
        convert_with_config()
