"""
PDF extraction using PyMuPDF (fitz).

PyMuPDF is a high-performance Python binding for MuPDF, a lightweight PDF
and XPS viewer. It provides fast text extraction with position information,
layout preservation, and support for images and annotations.

Strengths:  Very fast, excellent layout preservation, block-level extraction
            with coordinates, image extraction, small memory footprint.
Weaknesses: Table extraction is less mature than pdfplumber, C dependency.

Usage:
    uv run python unstructured_documents/01_pdf/03_pymupdf_extraction.py
"""

import sys
from pathlib import Path

import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
SIMPLE_TEXT_PDF = SAMPLE_DIR / "simple_text.pdf"


# ---------------------------------------------------------------------------
# 1. Basic text extraction
# ---------------------------------------------------------------------------


def extract_text_basic(pdf_path: Path) -> list[str]:
    """Extract plain text page by page using get_text()."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text()  # default is "text" mode
        pages.append(text)
    doc.close()
    return pages


def demo_basic_extraction():
    """Show basic text extraction."""
    print("=" * 70)
    print("1. BASIC TEXT EXTRACTION (PyMuPDF)")
    print("=" * 70)

    pages = extract_text_basic(SIMPLE_TEXT_PDF)
    for i, text in enumerate(pages):
        print(f"\n--- Page {i + 1} ({len(text)} chars) ---")
        preview = text[:400].strip()
        if len(text) > 400:
            preview += "..."
        print(preview)

    total = sum(len(p) for p in pages)
    print(f"\nTotal pages: {len(pages)}, Total characters: {total:,}")


# ---------------------------------------------------------------------------
# 2. Layout-preserved extraction using "blocks" mode
# ---------------------------------------------------------------------------


def extract_text_with_layout(pdf_path: Path) -> list[str]:
    """
    Extract text preserving the original page layout.

    The "text" mode with sort=True reorders blocks by position, which
    helps with multi-column layouts. The "blocks" mode gives per-block
    position data.
    """
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        # sort=True reorders text blocks by their position (top-to-bottom,
        # left-to-right), which helps preserve reading order.
        text = page.get_text("text", sort=True)
        pages.append(text)
    doc.close()
    return pages


def demo_layout_extraction():
    """Show layout-preserved extraction."""
    print("\n" + "=" * 70)
    print("2. LAYOUT-PRESERVED EXTRACTION (sort=True)")
    print("=" * 70)

    pages = extract_text_with_layout(SIMPLE_TEXT_PDF)
    # Just show the first page for comparison
    print(f"\n--- Page 1 (layout-preserved, {len(pages[0])} chars) ---")
    preview = pages[0][:500].strip()
    if len(pages[0]) > 500:
        preview += "..."
    print(preview)


# ---------------------------------------------------------------------------
# 3. Block-level extraction with bounding boxes
# ---------------------------------------------------------------------------


def extract_blocks(pdf_path: Path, page_num: int = 0) -> list[dict]:
    """
    Extract text as blocks with position information.

    Each block has:
      - x0, y0, x1, y1: bounding box coordinates
      - text: the text content
      - block_no: block index
      - block_type: 0 = text, 1 = image

    This is useful for understanding document layout and filtering
    headers, footers, or sidebars by position.
    """
    doc = fitz.open(str(pdf_path))
    page = doc[page_num]

    # get_text("dict") returns a detailed structure with blocks, lines, spans
    blocks_raw = page.get_text("blocks", sort=True)

    blocks = []
    for b in blocks_raw:
        # Each block is a tuple: (x0, y0, x1, y1, text_or_img, block_no, block_type)
        block = {
            "x0": round(b[0], 2),
            "y0": round(b[1], 2),
            "x1": round(b[2], 2),
            "y1": round(b[3], 2),
            "text": b[4] if b[6] == 0 else "<image>",
            "block_no": b[5],
            "block_type": "text" if b[6] == 0 else "image",
        }
        blocks.append(block)

    doc.close()
    return blocks


def demo_block_extraction():
    """Show block-level extraction with coordinates."""
    print("\n" + "=" * 70)
    print("3. BLOCK-LEVEL EXTRACTION WITH BOUNDING BOXES")
    print("=" * 70)

    blocks = extract_blocks(SIMPLE_TEXT_PDF, page_num=0)
    print(f"\n  Total blocks on page 1: {len(blocks)}")
    print(f"\n  {'Block':>5s} {'Type':<6s} {'x0':>7s} {'y0':>7s} {'x1':>7s} {'y1':>7s}  Text Preview")
    print(f"  {'-' * 5} {'-' * 6} {'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7}  {'-' * 30}")

    for b in blocks[:10]:
        text_preview = b["text"][:40].replace("\n", " ").strip()
        if len(b["text"]) > 40:
            text_preview += "..."
        print(
            f"  {b['block_no']:>5d} {b['block_type']:<6s} "
            f"{b['x0']:>7.1f} {b['y0']:>7.1f} "
            f"{b['x1']:>7.1f} {b['y1']:>7.1f}  {text_preview}"
        )

    if len(blocks) > 10:
        print(f"\n  ... and {len(blocks) - 10} more blocks")


# ---------------------------------------------------------------------------
# 4. Structured dict extraction (spans with font info)
# ---------------------------------------------------------------------------


def extract_structured_dict(pdf_path: Path, page_num: int = 0) -> dict:
    """
    Extract page content as a structured dictionary with full font info.

    The "dict" mode returns blocks -> lines -> spans, where each span has:
      - text, font, size, color, origin, bbox
    This is the richest extraction mode and enables font-based heading
    detection and style analysis.
    """
    doc = fitz.open(str(pdf_path))
    page = doc[page_num]
    data = page.get_text("dict", sort=True)
    doc.close()
    return data


def demo_structured_extraction():
    """Show structured dict extraction with font details."""
    print("\n" + "=" * 70)
    print("4. STRUCTURED EXTRACTION (dict mode - fonts & spans)")
    print("=" * 70)

    data = extract_structured_dict(SIMPLE_TEXT_PDF, page_num=0)
    print(f"\n  Page dimensions: {data['width']:.0f} x {data['height']:.0f}")
    print(f"  Total blocks: {len(data['blocks'])}")

    # Collect unique fonts and sizes
    fonts_seen = set()
    for block in data["blocks"]:
        if block["type"] == 0:  # text block
            for line in block["lines"]:
                for span in line["spans"]:
                    fonts_seen.add((span["font"], round(span["size"], 1)))

    print("\n  Unique font/size combinations found:")
    for font, size in sorted(fonts_seen, key=lambda x: (-x[1], x[0])):
        print(f"    {font:<35s}  size={size}")

    # Show first few spans with full detail
    print("\n  First 8 text spans with details:")
    print(f"  {'Text':<35s} {'Font':<25s} {'Size':>5s} {'Bold':>5s}")
    print(f"  {'-' * 35} {'-' * 25} {'-' * 5} {'-' * 5}")
    count = 0
    for block in data["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if count >= 8:
                    break
                text = span["text"][:35].strip()
                if not text:
                    continue
                font = span["font"][:25]
                size = span["size"]
                is_bold = "Bold" in span["font"] or "bold" in span["font"].lower()
                print(f"  {text:<35s} {font:<25s} {size:>5.1f} {'yes' if is_bold else 'no':>5s}")
                count += 1
            if count >= 8:
                break
        if count >= 8:
            break


# ---------------------------------------------------------------------------
# 5. Fast batch extraction
# ---------------------------------------------------------------------------


def demo_batch_extraction():
    """Demonstrate fast batch extraction of all pages at once."""
    print("\n" + "=" * 70)
    print("5. FAST BATCH EXTRACTION")
    print("=" * 70)

    import time

    doc = fitz.open(str(SIMPLE_TEXT_PDF))

    # Method A: Page-by-page
    start = time.perf_counter()
    texts_a = []
    for page in doc:
        texts_a.append(page.get_text())
    time_a = time.perf_counter() - start

    # Method B: Using get_text on the whole doc with join
    doc2 = fitz.open(str(SIMPLE_TEXT_PDF))
    start = time.perf_counter()
    # PyMuPDF does not have a whole-doc extract, but we can iterate efficiently
    texts_b = [page.get_text("text", sort=True) for page in doc2]
    time_b = time.perf_counter() - start

    # Method C: Extract as raw text (fastest, minimal processing)
    doc3 = fitz.open(str(SIMPLE_TEXT_PDF))
    start = time.perf_counter()
    texts_c = [page.get_text("rawdict") for page in doc3]
    time_c = time.perf_counter() - start

    print(f"\n  Page-by-page (text mode):      {time_a * 1000:>8.2f} ms  ({sum(len(t) for t in texts_a):,} chars)")
    print(f"  Page-by-page (sorted text):    {time_b * 1000:>8.2f} ms  ({sum(len(t) for t in texts_b):,} chars)")
    print(f"  Page-by-page (rawdict mode):   {time_c * 1000:>8.2f} ms  ({len(texts_c)} page dicts)")

    doc.close()
    doc2.close()
    doc3.close()

    print("\n  Note: PyMuPDF is typically 5-10x faster than pdfplumber.")
    print("  The rawdict mode returns structured data without string assembly,")
    print("  which is useful when you need position info but not formatted text.")


# ---------------------------------------------------------------------------
# 6. Practical: Detect headings by font size
# ---------------------------------------------------------------------------


def detect_headings(pdf_path: Path) -> list[dict]:
    """
    Use font-size analysis to detect headings automatically.

    This is useful for structure-aware chunking in RAG pipelines.
    Blocks with a font size larger than the body text are likely headings.
    """
    doc = fitz.open(str(pdf_path))
    # First pass: find the most common font size (= body text)
    size_counts: dict[float, int] = {}
    for page in doc:
        data = page.get_text("dict")
        for block in data["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    s = round(span["size"], 1)
                    size_counts[s] = size_counts.get(s, 0) + len(span["text"])

    # The most frequent size by character count is the body size
    body_size = max(size_counts, key=size_counts.get)

    # Second pass: extract headings (anything significantly larger than body)
    headings = []
    for page_num, page in enumerate(doc):
        data = page.get_text("dict", sort=True)
        for block in data["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["size"] > body_size + 1 and span["text"].strip():
                        headings.append(
                            {
                                "page": page_num + 1,
                                "text": span["text"].strip(),
                                "font_size": round(span["size"], 1),
                                "font": span["font"],
                                "y_position": round(span["origin"][1], 1),
                            }
                        )

    doc.close()
    return headings


def demo_heading_detection():
    """Show automatic heading detection via font-size analysis."""
    print("\n" + "=" * 70)
    print("6. AUTOMATIC HEADING DETECTION (font-size analysis)")
    print("=" * 70)

    headings = detect_headings(SIMPLE_TEXT_PDF)
    print(f"\n  Headings detected: {len(headings)}")
    print(f"\n  {'Page':>4s}  {'Size':>5s}  Text")
    print(f"  {'-' * 4}  {'-' * 5}  {'-' * 50}")
    for h in headings:
        print(f"  {h['page']:>4d}  {h['font_size']:>5.1f}  {h['text'][:60]}")


if __name__ == "__main__":
    if not SIMPLE_TEXT_PDF.exists():
        print(f"ERROR: {SIMPLE_TEXT_PDF} not found.")
        print("Run generate_samples.py first:")
        print("  uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py")
        sys.exit(1)

    demo_basic_extraction()
    demo_layout_extraction()
    demo_block_extraction()
    demo_structured_extraction()
    demo_batch_extraction()
    demo_heading_detection()

    print("\n" + "=" * 70)
    print("Done. PyMuPDF provides fast, detailed extraction with position data.")
    print("For table-specific extraction, see 04_table_extraction.py")
    print("=" * 70)
