"""
LlamaParse - Parsing Tiers Comparison
=======================================
LlamaParse offers different parsing tiers with varying capabilities:

  fast         - Spatial text output only. Fastest, lowest cost.
  agentic      - Handles images and diagrams with AI understanding.
  agentic_plus - Complex layouts, tables, and advanced structure.

Higher tiers use more advanced AI models for better accuracy on
complex documents but consume more credits.

uv pip install llama-parse
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def compare_tiers():
    """Compare parsing tiers on the same document."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")

    print("=" * 60)
    print("LLAMAPARSE - PARSING TIERS")
    print("=" * 60)

    if not api_key:
        print("""
Parsing Tier Comparison:

Tier           | Speed  | Accuracy | Best For
---------------|--------|----------|----------------------------------
fast           | Fast   | Basic    | Simple text documents, quick preview
agentic        | Medium | High     | Documents with images, charts
agentic_plus   | Slow   | Highest  | Complex tables, multi-column layouts

Usage:
  # Legacy API (llama-parse package)
  parser = LlamaParse(api_key="...", result_type="markdown")

  # New API (llama-cloud package)
  from llama_cloud import AsyncLlamaCloud
  client = AsyncLlamaCloud(api_key="llx-...")
  result = await client.parsing.parse(
      file_id=file_obj.id,
      tier="agentic",        # "fast", "agentic", "agentic_plus"
      version="latest",
  )

Free tier: 1000 pages/day across all tiers.
""")
        return

    try:
        from llama_parse import LlamaParse
    except ImportError:
        print("Install: uv pip install llama-parse")
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    for result_type in ["text", "markdown"]:
        parser = LlamaParse(
            api_key=api_key,
            result_type=result_type,
        )
        docs = parser.load_data(pdf_path)

        print(f"\n--- result_type='{result_type}' ---")
        for doc in docs:
            print(f"  Length: {len(doc.text)} chars")
            print(f"  Preview: {doc.text[:200]}...")


if __name__ == "__main__":
    compare_tiers()
