"""
OCR-based PDF extraction using pytesseract and pdf2image.

This approach is essential for scanned PDFs that contain images of text
rather than embedded text data. It converts each PDF page to an image,
then runs Optical Character Recognition (OCR) to extract text.

IMPORTANT: This script requires OPTIONAL dependencies:
  Python packages:  pytesseract, pdf2image, Pillow
  System tools:     tesseract-ocr, poppler-utils (poppler)

Install with:
  uv pip install pytesseract pdf2image Pillow
  brew install tesseract poppler          # macOS
  sudo apt install tesseract-ocr poppler-utils  # Ubuntu/Debian

If the dependencies are not installed, the script will print helpful
installation instructions instead of crashing.

Usage:
    uv run python unstructured_documents/01_pdf/05_ocr_extraction.py
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
SIMPLE_TEXT_PDF = SAMPLE_DIR / "simple_text.pdf"


def check_dependencies() -> tuple[bool, list[str]]:
    """
    Check whether OCR dependencies are available.
    Returns (all_ok, list_of_missing).
    """
    missing = []

    # Check pytesseract
    try:
        import pytesseract  # noqa: F401
    except ImportError:
        missing.append("pytesseract (pip install pytesseract)")

    # Check pdf2image
    try:
        import pdf2image  # noqa: F401
    except ImportError:
        missing.append("pdf2image (pip install pdf2image)")

    # Check Pillow
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        missing.append("Pillow (pip install Pillow)")

    # Check tesseract binary
    if "pytesseract" not in [m.split()[0] for m in missing]:
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
        except Exception:
            missing.append("tesseract-ocr system binary (brew install tesseract / apt install tesseract-ocr)")

    # Check poppler (needed by pdf2image)
    if "pdf2image" not in [m.split()[0] for m in missing]:
        try:
            pass
            # Try a quick conversion to check poppler is available
            # We do not actually convert here; just check the import path
        except Exception:
            missing.append("poppler-utils system binary (brew install poppler / apt install poppler-utils)")

    return len(missing) == 0, missing


def print_installation_guide(missing: list[str]):
    """Print helpful installation instructions."""
    print("=" * 70)
    print("OCR EXTRACTION - DEPENDENCY CHECK")
    print("=" * 70)
    print("\n  This script requires optional OCR dependencies that are not")
    print("  currently installed.\n")
    print("  Missing components:")
    for m in missing:
        print(f"    - {m}")
    print("\n  Installation (macOS):")
    print("    brew install tesseract poppler")
    print("    uv pip install pytesseract pdf2image Pillow")
    print("\n  Installation (Ubuntu/Debian):")
    print("    sudo apt install tesseract-ocr poppler-utils")
    print("    uv pip install pytesseract pdf2image Pillow")
    print("\n  Installation (Windows):")
    print("    Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki")
    print("    Download Poppler from https://github.com/oschwartz10612/poppler-windows")
    print("    pip install pytesseract pdf2image Pillow")
    print("\n  After installing, re-run this script.")


# ---------------------------------------------------------------------------
# OCR extraction functions
# ---------------------------------------------------------------------------


def ocr_extract_text(pdf_path: Path, dpi: int = 300) -> list[dict]:
    """
    Extract text from a PDF using OCR.

    Steps:
      1. Convert each PDF page to a PIL Image using pdf2image
      2. Run Tesseract OCR on each image
      3. Return extracted text with confidence info

    Parameters:
      pdf_path: Path to the PDF file
      dpi: Resolution for page-to-image conversion (higher = better accuracy
           but slower). 300 DPI is a good default.
    """
    import pytesseract
    from pdf2image import convert_from_path

    # Convert PDF pages to images
    images = convert_from_path(str(pdf_path), dpi=dpi)

    results = []
    for i, image in enumerate(images):
        # Basic text extraction
        text = pytesseract.image_to_string(image)

        # Get detailed data with confidence scores
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Calculate average confidence (excluding empty/low-confidence entries)
        confidences = [int(c) for c, t in zip(data["conf"], data["text"]) if int(c) > 0 and t.strip()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        results.append(
            {
                "page": i + 1,
                "text": text,
                "image_size": image.size,
                "avg_confidence": round(avg_confidence, 1),
                "word_count": len([t for t in data["text"] if t.strip()]),
            }
        )

    return results


def ocr_extract_with_preprocessing(pdf_path: Path, dpi: int = 300) -> list[dict]:
    """
    Extract text with image preprocessing to improve OCR accuracy.

    Common preprocessing steps:
      - Convert to grayscale
      - Apply thresholding (binarization)
      - Remove noise
      - Deskew

    These steps are especially helpful for low-quality scans.
    """
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import ImageFilter

    images = convert_from_path(str(pdf_path), dpi=dpi)

    results = []
    for i, image in enumerate(images):
        # Preprocessing pipeline
        # Step 1: Convert to grayscale
        gray = image.convert("L")

        # Step 2: Apply slight sharpening
        sharpened = gray.filter(ImageFilter.SHARPEN)

        # Step 3: Apply thresholding (binarization)
        # This converts the image to pure black and white
        threshold = 150
        binarized = sharpened.point(lambda x: 255 if x > threshold else 0, "1")

        # Extract text from preprocessed image
        text = pytesseract.image_to_string(binarized)

        results.append(
            {
                "page": i + 1,
                "text": text,
                "preprocessing": "grayscale -> sharpen -> binarize",
            }
        )

    return results


def ocr_extract_layout(pdf_path: Path, dpi: int = 300) -> list[dict]:
    """
    Extract text with layout/position information using hOCR format.

    hOCR is an HTML-based format that includes bounding boxes for each
    word, line, and paragraph. This is useful for preserving document
    layout from scanned PDFs.
    """
    import pytesseract
    from pdf2image import convert_from_path

    images = convert_from_path(str(pdf_path), dpi=dpi)

    results = []
    for i, image in enumerate(images):
        # Get hOCR output (HTML with bounding boxes)
        hocr = pytesseract.image_to_pdf_or_hocr(image, extension="hocr")

        # Get structured word-level data
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Group words into lines based on line_num
        lines = {}
        for j in range(len(data["text"])):
            if data["text"][j].strip():
                line_key = (
                    data["block_num"][j],
                    data["par_num"][j],
                    data["line_num"][j],
                )
                if line_key not in lines:
                    lines[line_key] = {
                        "words": [],
                        "left": data["left"][j],
                        "top": data["top"][j],
                    }
                lines[line_key]["words"].append(data["text"][j])

        results.append(
            {
                "page": i + 1,
                "num_lines": len(lines),
                "lines": [
                    {
                        "text": " ".join(line["words"]),
                        "position": {"left": line["left"], "top": line["top"]},
                    }
                    for line in lines.values()
                ],
                "hocr_size": len(hocr),
            }
        )

    return results


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------


def demo_basic_ocr():
    """Demonstrate basic OCR extraction."""
    print("\n" + "=" * 70)
    print("1. BASIC OCR EXTRACTION")
    print("=" * 70)

    results = ocr_extract_text(SIMPLE_TEXT_PDF, dpi=200)

    for r in results:
        print(f"\n  --- Page {r['page']} ---")
        print(f"  Image size: {r['image_size']}")
        print(f"  Words detected: {r['word_count']}")
        print(f"  Average confidence: {r['avg_confidence']}%")
        print(f"  Text preview ({len(r['text'])} chars):")
        preview = r["text"][:300].strip()
        for line in preview.split("\n")[:6]:
            print(f"    {line}")
        if len(r["text"]) > 300:
            print("    ...")


def demo_preprocessed_ocr():
    """Demonstrate OCR with image preprocessing."""
    print("\n" + "=" * 70)
    print("2. OCR WITH PREPROCESSING")
    print("=" * 70)

    results = ocr_extract_with_preprocessing(SIMPLE_TEXT_PDF, dpi=200)

    for r in results[:2]:  # Show first 2 pages
        print(f"\n  --- Page {r['page']} (preprocessing: {r['preprocessing']}) ---")
        preview = r["text"][:300].strip()
        for line in preview.split("\n")[:6]:
            print(f"    {line}")
        if len(r["text"]) > 300:
            print("    ...")


def demo_layout_ocr():
    """Demonstrate layout-aware OCR extraction."""
    print("\n" + "=" * 70)
    print("3. LAYOUT-AWARE OCR (with position data)")
    print("=" * 70)

    results = ocr_extract_layout(SIMPLE_TEXT_PDF, dpi=200)

    for r in results[:1]:  # Show first page only
        print(f"\n  --- Page {r['page']} ---")
        print(f"  Lines detected: {r['num_lines']}")
        print(f"  hOCR output size: {r['hocr_size']:,} bytes")
        print("\n  First 10 lines with positions:")
        for line in r["lines"][:10]:
            pos = line["position"]
            print(f"    [{pos['left']:>4d}, {pos['top']:>4d}] {line['text'][:60]}")
        if len(r["lines"]) > 10:
            print(f"    ... ({len(r['lines']) - 10} more lines)")


def demo_ocr_vs_text():
    """Compare OCR output with direct text extraction."""
    print("\n" + "=" * 70)
    print("4. OCR vs DIRECT TEXT EXTRACTION (comparison)")
    print("=" * 70)

    # OCR extraction
    ocr_results = ocr_extract_text(SIMPLE_TEXT_PDF, dpi=200)
    ocr_text = "\n".join(r["text"] for r in ocr_results)

    # Direct extraction with PyMuPDF
    try:
        import fitz

        doc = fitz.open(str(SIMPLE_TEXT_PDF))
        direct_text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except ImportError:
        direct_text = "(PyMuPDF not available for comparison)"

    print(f"\n  OCR text length:    {len(ocr_text):,} chars")
    print(f"  Direct text length: {len(direct_text):,} chars")
    if isinstance(direct_text, str) and len(direct_text) > 10:
        # Simple similarity: count common words
        ocr_words = set(ocr_text.lower().split())
        direct_words = set(direct_text.lower().split())
        common = ocr_words & direct_words
        all_words = ocr_words | direct_words
        similarity = len(common) / len(all_words) * 100 if all_words else 0
        print(f"  Word overlap:       {similarity:.1f}%")

    print("\n  Note: For born-digital PDFs, direct extraction is always")
    print("  preferred. OCR is only needed for scanned/image-based PDFs.")
    print("  OCR may introduce errors and is significantly slower.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not SIMPLE_TEXT_PDF.exists():
        print(f"ERROR: {SIMPLE_TEXT_PDF} not found.")
        print("Run generate_samples.py first:")
        print("  uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py")
        sys.exit(1)

    # Check dependencies first
    all_ok, missing = check_dependencies()

    if not all_ok:
        print_installation_guide(missing)
        print("\n" + "=" * 70)
        print("SHOWING CODE STRUCTURE (without running)")
        print("=" * 70)
        print("""
  The OCR extraction pipeline consists of these key functions:

  1. ocr_extract_text(pdf_path, dpi=300)
     - Converts PDF pages to images at the specified DPI
     - Runs Tesseract OCR on each image
     - Returns text with confidence scores

  2. ocr_extract_with_preprocessing(pdf_path, dpi=300)
     - Adds image preprocessing: grayscale, sharpen, binarize
     - Improves accuracy on low-quality scans

  3. ocr_extract_layout(pdf_path, dpi=300)
     - Uses hOCR format for position-aware extraction
     - Groups words into lines with bounding boxes
     - Useful for preserving document layout

  4. When to use OCR:
     - Scanned paper documents digitized as image PDFs
     - PDFs with embedded images containing text
     - Faxed or photographed documents
     - PDFs where direct text extraction returns empty/garbage

  5. When NOT to use OCR:
     - Born-digital PDFs (created by software, not scanners)
     - PDFs where pypdf/pdfplumber/PyMuPDF extract clean text
     - When speed is critical (OCR is 10-100x slower)
""")
        sys.exit(0)

    # Dependencies available - run demos
    try:
        demo_basic_ocr()
        demo_preprocessed_ocr()
        demo_layout_ocr()
        demo_ocr_vs_text()
    except Exception as e:
        print(f"\n  ERROR during OCR processing: {e}")
        print("  This may indicate a system-level dependency issue.")
        print("  Ensure tesseract and poppler are properly installed.")

    print("\n" + "=" * 70)
    print("Done. OCR is essential for scanned PDFs but adds latency and errors.")
    print("Always prefer direct text extraction when available.")
    print("=" * 70)
