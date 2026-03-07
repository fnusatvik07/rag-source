"""
Docling - Advanced PDF Processing
===================================
Docling offers fine-grained control over PDF processing through PipelineOptions.
This includes table structure recognition modes, OCR engine selection,
and layout analysis configuration.

Key classes:
- PdfFormatOption: PDF-specific conversion settings
- TableFormerMode: FAST vs ACCURATE table detection
- OcrOptions subclasses: EasyOcrOptions, TesseractOcrOptions, etc.
- PipelineOptions: Master configuration for the processing pipeline

uv pip install docling
uv pip install "docling[tesserocr]"  # for Tesseract OCR
uv pip install "docling[easyocr]"    # for EasyOCR
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def table_extraction_modes():
    """Compare FAST vs ACCURATE table detection on a table-heavy PDF."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling.document_converter import DocumentConverter, PdfFormatOption

    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf"

    for mode_name, mode in [
        ("FAST", TableFormerMode.FAST),
        ("ACCURATE", TableFormerMode.ACCURATE),
    ]:
        print(f"\n{'=' * 60}")
        print(f"TABLE DETECTION MODE: {mode_name}")
        print(f"{'=' * 60}")

        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
            table_structure_options={"mode": mode},
        )

        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        result = converter.convert(str(pdf_path))
        md = result.document.export_to_markdown()
        print(md[:600])
        print(f"\n[Total output: {len(md)} chars]")


def ocr_configuration():
    """Configure OCR settings for scanned documents."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"

    # Enable OCR with default engine
    pipeline_options = PdfPipelineOptions(
        do_ocr=True,
        # OCR options can be set to specific engines:
        # ocr_options=EasyOcrOptions(lang=["en"])
        # ocr_options=TesseractOcrOptions(lang=["eng"])
        # ocr_options=TesseractCliOcrOptions(lang=["eng"])
    )

    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})

    print("=" * 60)
    print("PDF WITH OCR ENABLED")
    print("=" * 60)

    result = converter.convert(str(pdf_path))
    print(result.document.export_to_markdown()[:500])


def image_conversion():
    """Convert an image file using Docling's OCR pipeline."""
    from docling.document_converter import DocumentConverter

    img_path = SAMPLES_DIR / "06_images_ocr" / "sample_docs" / "simple_text.png"

    if not img_path.exists():
        print(f"Image not found: {img_path}")
        return

    converter = DocumentConverter()

    print("=" * 60)
    print("IMAGE TO TEXT VIA DOCLING")
    print("=" * 60)

    result = converter.convert(str(img_path))
    print(result.document.export_to_markdown())


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Table extraction modes (FAST vs ACCURATE)")
    print("2. OCR configuration")
    print("3. Image conversion")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    if choice == "1":
        table_extraction_modes()
    elif choice == "2":
        ocr_configuration()
    elif choice == "3":
        image_conversion()
