"""
Image OCR Method 1: Tesseract via pytesseract

Tesseract is the most widely used open-source OCR engine.
pytesseract is a Python wrapper that makes it easy to call from Python.

Requirements:
  - System: Tesseract OCR engine must be installed on the OS
    macOS:   brew install tesseract
    Ubuntu:  sudo apt-get install tesseract-ocr
    Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Python:  pip install pytesseract Pillow

Best for: Scanned documents, image-based PDFs, printed text recognition.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import chunk_by_sentences, preview_chunks

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def check_tesseract_available() -> bool:
    """Check if pytesseract and Tesseract engine are available."""
    try:
        import pytesseract  # noqa: F401

        # Also verify the Tesseract binary is reachable
        pytesseract.get_tesseract_version()
        return True
    except ImportError:
        print("=" * 60)
        print("pytesseract is NOT installed.")
        print("=" * 60)
        print()
        print("Install it with:")
        print("  uv pip install pytesseract")
        print()
        print("You also need the Tesseract OCR engine on your system:")
        print("  macOS:   brew install tesseract")
        print("  Ubuntu:  sudo apt-get install tesseract-ocr")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        return False
    except Exception as e:
        print("=" * 60)
        print(f"pytesseract is installed but Tesseract engine not found: {e}")
        print("=" * 60)
        print()
        print("Install the Tesseract OCR engine:")
        print("  macOS:   brew install tesseract")
        print("  Ubuntu:  sudo apt-get install tesseract-ocr")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        return False


def basic_ocr(image_path: Path) -> str:
    """
    Basic OCR: load an image and extract text using default settings.
    This is the simplest way to use Tesseract.
    """
    import pytesseract
    from PIL import Image

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()


def ocr_with_preprocessing(image_path: Path) -> str:
    """
    OCR with image preprocessing for better accuracy.

    Common preprocessing steps:
    1. Convert to grayscale (removes color noise)
    2. Apply threshold (makes text pure black, background pure white)
    3. Optionally resize for very small text

    These steps significantly improve OCR accuracy on noisy scans.
    """
    import pytesseract
    from PIL import Image, ImageFilter

    img = Image.open(image_path)

    # Step 1: Convert to grayscale
    gray = img.convert("L")

    # Step 2: Apply binary threshold to sharpen text
    # Pixels above 150 become white (255), below become black (0)
    threshold = 150
    bw = gray.point(lambda x: 255 if x > threshold else 0, mode="1")

    # Step 3: Slight blur then re-threshold to smooth edges (optional)
    smoothed = bw.convert("L").filter(ImageFilter.MedianFilter(size=3))
    final = smoothed.point(lambda x: 255 if x > 128 else 0, mode="1")

    text = pytesseract.image_to_string(final)
    return text.strip()


def ocr_with_config(image_path: Path, psm: int = 3, oem: int = 3) -> str:
    """
    OCR with custom Tesseract configuration.

    Page Segmentation Modes (PSM) - tells Tesseract about image layout:
      0  = Orientation and script detection only
      1  = Automatic with OSD
      3  = Fully automatic (default) - best for full pages
      4  = Assume single column of variable-size text
      6  = Assume a single uniform block of text
      7  = Treat image as a single line of text
      8  = Treat image as a single word
      13 = Treat image as a single text line (raw)

    OCR Engine Modes (OEM):
      0 = Legacy engine only
      1 = LSTM neural net only
      2 = Legacy + LSTM
      3 = Default (auto-select based on available models)
    """
    import pytesseract
    from PIL import Image

    img = Image.open(image_path)
    config = f"--psm {psm} --oem {oem}"
    text = pytesseract.image_to_string(img, config=config)
    return text.strip()


def ocr_with_details(image_path: Path) -> list[dict]:
    """
    Get detailed OCR output including word-level bounding boxes and confidence.
    Useful for understanding where text is located in the image.
    """
    import pytesseract
    from PIL import Image

    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    results = []
    for i in range(len(data["text"])):
        word = data["text"][i].strip()
        conf = int(data["conf"][i])
        if word and conf > 0:
            results.append(
                {
                    "text": word,
                    "confidence": conf,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                    "block": data["block_num"][i],
                    "paragraph": data["par_num"][i],
                    "line": data["line_num"][i],
                }
            )
    return results


if __name__ == "__main__":
    if not check_tesseract_available():
        print("Skipping Tesseract demos (not available).")
        print("The other scripts in this module may still work.")
        sys.exit(0)

    # Verify sample images exist
    simple_img = SAMPLE_DIR / "simple_text.png"
    multi_img = SAMPLE_DIR / "multi_paragraph.png"
    noisy_img = SAMPLE_DIR / "noisy_text.png"

    if not simple_img.exists():
        print("Sample images not found. Generating them first...")
        print("Run: uv run python unstructured_documents/06_images_ocr/sample_docs/generate_samples.py")
        sys.exit(1)

    # --- 1. Basic OCR on clean image ---
    print("=" * 60)
    print("1. BASIC OCR - Clean Image (simple_text.png)")
    print("=" * 60)
    text = basic_ocr(simple_img)
    print(f"Extracted text ({len(text)} chars):")
    print(text)

    # --- 2. OCR on multi-paragraph document ---
    print(f"\n{'=' * 60}")
    print("2. MULTI-PARAGRAPH DOCUMENT (multi_paragraph.png)")
    print("=" * 60)
    text = basic_ocr(multi_img)
    print(f"Extracted text ({len(text)} chars):")
    print(text)

    # --- 3. OCR on noisy image (before preprocessing) ---
    print(f"\n{'=' * 60}")
    print("3. NOISY IMAGE - Without Preprocessing (noisy_text.png)")
    print("=" * 60)
    text_raw = basic_ocr(noisy_img)
    print(f"Extracted text ({len(text_raw)} chars):")
    print(text_raw)

    # --- 4. OCR on noisy image (with preprocessing) ---
    print(f"\n{'=' * 60}")
    print("4. NOISY IMAGE - With Preprocessing (noisy_text.png)")
    print("=" * 60)
    text_clean = ocr_with_preprocessing(noisy_img)
    print(f"Extracted text ({len(text_clean)} chars):")
    print(text_clean)
    print(f"\nImprovement: {len(text_raw)} -> {len(text_clean)} chars")

    # --- 5. Detailed OCR with bounding boxes ---
    print(f"\n{'=' * 60}")
    print("5. DETAILED OCR - Word-Level Bounding Boxes (simple_text.png)")
    print("=" * 60)
    details = ocr_with_details(simple_img)
    print(f"Detected {len(details)} words")
    print("\nFirst 10 words with confidence:")
    for word in details[:10]:
        print(f"  '{word['text']}' (conf: {word['confidence']}%, pos: x={word['left']}, y={word['top']})")

    avg_conf = sum(w["confidence"] for w in details) / len(details) if details else 0
    print(f"\nAverage confidence: {avg_conf:.1f}%")

    # --- 6. Configuration options ---
    print(f"\n{'=' * 60}")
    print("6. PSM MODE COMPARISON (simple_text.png)")
    print("=" * 60)
    for psm in [3, 4, 6]:
        text = ocr_with_config(simple_img, psm=psm)
        print(f"\n  PSM {psm}: {len(text)} chars extracted")
        print(f"  First 80 chars: {text[:80]}...")

    # --- 7. Sentence-based chunking on OCR output ---
    print(f"\n{'=' * 60}")
    print("7. SENTENCE-BASED CHUNKING ON OCR OUTPUT")
    print("=" * 60)
    full_text = basic_ocr(multi_img)
    chunks = chunk_by_sentences(full_text, sentences_per_chunk=3, overlap_sentences=1)
    preview_chunks(chunks)
