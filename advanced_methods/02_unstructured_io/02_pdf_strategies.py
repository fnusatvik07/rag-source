"""
Unstructured.io - PDF Processing Strategies
=============================================
Unstructured offers three strategies for PDF processing:

1. "fast"     - Direct text extraction (no ML models). Fastest but may
                miss layout structure. Best for text-heavy PDFs.
2. "hi_res"   - Uses layout detection models (detectron2/YOLOX) for
                accurate structure recognition. Best quality but slower.
3. "ocr_only" - Forces OCR on the entire document. For scanned PDFs
                where text layer is missing or unreliable.

uv pip install "unstructured[pdf]"
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def compare_strategies():
    """Compare fast, hi_res, and ocr_only on the same PDF."""
    import time
    from collections import Counter

    from unstructured.partition.pdf import partition_pdf

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    strategies = ["fast", "hi_res", "ocr_only"]

    for strategy in strategies:
        print(f"\n{'=' * 60}")
        print(f"STRATEGY: {strategy.upper()}")
        print(f"{'=' * 60}")

        try:
            start = time.time()
            elements = partition_pdf(
                filename=pdf_path,
                strategy=strategy,
            )
            elapsed = time.time() - start

            type_counts = Counter(type(el).__name__ for el in elements)
            print(f"  Time: {elapsed:.2f}s")
            print(f"  Elements: {len(elements)}")
            print(f"  Types: {dict(type_counts)}")

            # Show first few elements
            for el in elements[:3]:
                print(f"  [{type(el).__name__}] {str(el)[:120]}")
        except Exception as e:
            print(f"  Error: {e}")
            print('  (hi_res requires: uv pip install "unstructured[pdf]" and model downloads)')


def hi_res_with_options():
    """Advanced hi_res configuration with specific model and languages."""
    from unstructured.partition.pdf import partition_pdf

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    print("=" * 60)
    print("HI-RES WITH ADVANCED OPTIONS")
    print("=" * 60)

    try:
        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            infer_table_structure=True,  # Extract table HTML
            include_page_breaks=True,  # Insert PageBreak elements
            languages=["eng"],  # OCR language hints
        )

        for el in elements:
            if type(el).__name__ == "Table":
                print("\n--- Table Found ---")
                print(f"Text: {str(el)[:200]}")
                if hasattr(el.metadata, "text_as_html") and el.metadata.text_as_html:
                    print(f"HTML: {el.metadata.text_as_html[:300]}")
                break
        else:
            print("No tables detected in this document.")

    except Exception as e:
        print(f"Error: {e}")
        print("hi_res requires layout detection models. Install with:")
        print('  uv pip install "unstructured[pdf]"')


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Compare all strategies")
    print("2. Hi-res with advanced options")
    choice = input("Enter 1/2 (default=1): ").strip() or "1"

    if choice == "1":
        compare_strategies()
    else:
        hi_res_with_options()
