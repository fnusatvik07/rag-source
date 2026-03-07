"""
Image OCR Method 2: EasyOCR

EasyOCR is a deep learning-based OCR engine that supports 80+ languages.
It uses CRAFT for text detection and CRNN for text recognition.

Requirements:
  - Python: pip install easyocr
  - First run downloads model files (~100MB for English)

Best for: Multi-language OCR, scene text (signs, labels), when Tesseract
          struggles with unusual fonts or complex layouts.

Comparison with Tesseract:
  - EasyOCR: Better on scene text, multi-language, GPU-accelerated
  - Tesseract: Faster for standard documents, lighter weight, no GPU needed
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import chunk_by_sentences, preview_chunks

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def check_easyocr_available() -> bool:
    """Check if EasyOCR is installed."""
    try:
        import easyocr  # noqa: F401

        return True
    except ImportError:
        print("=" * 60)
        print("EasyOCR is NOT installed.")
        print("=" * 60)
        print()
        print("Install it with:")
        print("  uv pip install easyocr")
        print()
        print("Note: EasyOCR requires PyTorch. The install may take a while")
        print("and download ~1-2GB of dependencies. On first use, it also")
        print("downloads language-specific model files (~100MB for English).")
        print()
        print("For GPU acceleration (optional):")
        print("  pip install easyocr torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print()
        return False


def extract_text_basic(image_path: Path, languages: list[str] | None = None) -> list[tuple]:
    """
    Basic text extraction with EasyOCR.

    Returns a list of (bounding_box, text, confidence) tuples.
    Each tuple represents a detected text region in the image.
    """
    import easyocr

    if languages is None:
        languages = ["en"]

    # gpu=False for compatibility; set gpu=True if CUDA is available
    reader = easyocr.Reader(languages, gpu=False)
    results = reader.readtext(str(image_path))

    # results format: [([bbox_points], text, confidence), ...]
    return results


def extract_with_confidence(image_path: Path, min_confidence: float = 0.5) -> list[dict]:
    """
    Extract text regions with structured output and confidence filtering.

    Filters out low-confidence detections to improve quality.
    """
    import easyocr

    reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(str(image_path))

    extracted = []
    for bbox, text, confidence in results:
        if confidence >= min_confidence:
            # bbox is a list of 4 points: [top-left, top-right, bottom-right, bottom-left]
            top_left = bbox[0]
            bottom_right = bbox[2]
            extracted.append(
                {
                    "text": text,
                    "confidence": round(confidence, 3),
                    "x_min": int(top_left[0]),
                    "y_min": int(top_left[1]),
                    "x_max": int(bottom_right[0]),
                    "y_max": int(bottom_right[1]),
                }
            )

    return extracted


def combine_into_paragraphs(
    regions: list[dict],
    line_gap_threshold: int = 20,
) -> list[str]:
    """
    Combine individual text regions into coherent paragraphs.

    EasyOCR returns individual text blocks (often single lines or phrases).
    This function groups them by vertical proximity to reconstruct paragraphs.

    Args:
        regions: List of dicts from extract_with_confidence()
        line_gap_threshold: Max vertical gap (pixels) to consider same paragraph
    """
    if not regions:
        return []

    # Sort regions top-to-bottom, then left-to-right
    sorted_regions = sorted(regions, key=lambda r: (r["y_min"], r["x_min"]))

    paragraphs = []
    current_paragraph_lines = [sorted_regions[0]["text"]]
    prev_y_max = sorted_regions[0]["y_max"]

    for region in sorted_regions[1:]:
        gap = region["y_min"] - prev_y_max

        if gap > line_gap_threshold:
            # Big gap = new paragraph
            paragraphs.append(" ".join(current_paragraph_lines))
            current_paragraph_lines = [region["text"]]
        else:
            # Small gap = same paragraph (continuation or next line)
            current_paragraph_lines.append(region["text"])

        prev_y_max = region["y_max"]

    # Don't forget the last paragraph
    if current_paragraph_lines:
        paragraphs.append(" ".join(current_paragraph_lines))

    return paragraphs


if __name__ == "__main__":
    if not check_easyocr_available():
        print("Skipping EasyOCR demos (not available).")
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

    # --- 1. Basic extraction with bounding boxes ---
    print("=" * 60)
    print("1. BASIC EASYOCR EXTRACTION (simple_text.png)")
    print("=" * 60)
    print("(First run may download model files...)")
    results = extract_text_basic(simple_img)
    print(f"\nDetected {len(results)} text regions:\n")
    for bbox, text, conf in results:
        print(f"  [{conf:.2f}] {text}")

    # --- 2. Confidence-filtered extraction ---
    print(f"\n{'=' * 60}")
    print("2. CONFIDENCE-FILTERED EXTRACTION (simple_text.png)")
    print("=" * 60)
    regions = extract_with_confidence(simple_img, min_confidence=0.3)
    print(f"\nRegions with confidence >= 0.3: {len(regions)}\n")
    for r in regions:
        print(f"  [{r['confidence']:.3f}] '{r['text']}' (bbox: {r['x_min']},{r['y_min']} -> {r['x_max']},{r['y_max']})")

    # --- 3. Multi-paragraph document ---
    print(f"\n{'=' * 60}")
    print("3. MULTI-PARAGRAPH EXTRACTION (multi_paragraph.png)")
    print("=" * 60)
    regions = extract_with_confidence(multi_img, min_confidence=0.3)
    print(f"\nDetected {len(regions)} text regions")

    # Combine into paragraphs
    paragraphs = combine_into_paragraphs(regions)
    print(f"Combined into {len(paragraphs)} paragraphs:\n")
    for i, para in enumerate(paragraphs, 1):
        print(f"  Paragraph {i}: {para[:100]}{'...' if len(para) > 100 else ''}")

    # --- 4. Noisy image handling ---
    print(f"\n{'=' * 60}")
    print("4. NOISY IMAGE EXTRACTION (noisy_text.png)")
    print("=" * 60)
    regions_noisy = extract_with_confidence(noisy_img, min_confidence=0.3)
    print(f"\nDetected {len(regions_noisy)} text regions from noisy image:\n")
    for r in regions_noisy[:8]:
        print(f"  [{r['confidence']:.3f}] '{r['text']}'")
    if len(regions_noisy) > 8:
        print(f"  ... and {len(regions_noisy) - 8} more regions")

    # --- 5. Full text with chunking ---
    print(f"\n{'=' * 60}")
    print("5. SENTENCE-BASED CHUNKING ON EASYOCR OUTPUT")
    print("=" * 60)
    regions = extract_with_confidence(multi_img, min_confidence=0.3)
    paragraphs = combine_into_paragraphs(regions)
    full_text = "\n\n".join(paragraphs)
    print(f"\nFull extracted text ({len(full_text)} chars):")
    print(full_text[:300])
    print("...")

    chunks = chunk_by_sentences(full_text, sentences_per_chunk=3, overlap_sentences=1)
    preview_chunks(chunks)
