"""
MegaParse Vision - Multimodal AI Document Parsing
====================================================
MegaParseVision uses multimodal LLMs (GPT-4o, Claude 3.5/4) to
understand documents visually. Pages are rendered as images and
sent to a vision model for interpretation.

This approach excels at:
- Complex layouts that rule-based parsers miss
- Handwritten content
- Mixed text/image documents
- Charts and diagrams

Requires: OpenAI or Anthropic API key for the multimodal model.

uv pip install megaparse langchain-openai
# OR
uv pip install megaparse langchain-anthropic
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def vision_parse_openai():
    """Parse a PDF using GPT-4o vision model."""
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("=" * 60)
        print("MEGAPARSE VISION (GPT-4o)")
        print("=" * 60)
        print("\nRequires: export OPENAI_API_KEY='sk-...'")
        _show_vision_example()
        return

    try:
        from langchain_openai import ChatOpenAI
        from megaparse.parser.megaparse_vision import MegaParseVision
    except ImportError:
        print("Install: uv pip install megaparse langchain-openai")
        return

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")

    model = ChatOpenAI(model="gpt-4o", api_key=api_key)
    parser = MegaParseVision(model=model)

    print("=" * 60)
    print("MEGAPARSE VISION - GPT-4o")
    print("=" * 60)
    print("Processing (sending page images to GPT-4o)...")

    response = parser.convert(pdf_path)
    print(f"\nOutput ({len(response)} chars):")
    print(response[:800])


def vision_parse_anthropic():
    """Parse using Claude vision model (alternative to GPT-4o)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    print("=" * 60)
    print("MEGAPARSE VISION (Claude)")
    print("=" * 60)

    if not api_key:
        print("\nRequires: export ANTHROPIC_API_KEY='sk-ant-...'")

    print("""
# Using Claude as the vision model:

from megaparse.parser.megaparse_vision import MegaParseVision
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
parser = MegaParseVision(model=model)
response = parser.convert("complex_document.pdf")
print(response)
""")


def compare_standard_vs_vision():
    """Compare standard MegaParse vs MegaParseVision output."""
    print("=" * 60)
    print("STANDARD vs VISION PARSING")
    print("=" * 60)
    print("""
Approach       | Speed   | Cost     | Accuracy | Best For
---------------|---------|----------|----------|------------------------
MegaParse()    | Fast    | Free     | Good     | Text-heavy documents,
               |         | (local)  |          | standard layouts
MegaParseVision| Slow    | API cost | Excellent| Complex layouts, charts,
               | (API)   | per page |          | handwriting, diagrams

Benchmark (similarity to original):
  megaparse_vision:                0.87
  unstructured_with_check_table:   0.77
  unstructured (standard):         0.59
  llama_parser:                    0.33

How MegaParseVision works:
  1. Each page is rendered as an image (via poppler/pdf2image)
  2. The image is sent to a multimodal LLM (GPT-4o or Claude)
  3. The LLM interprets the visual layout and outputs Markdown
  4. Results from all pages are combined

Trade-off:
  - Standard: Fast, free, good for simple documents
  - Vision: Slow, costs money, but handles complex layouts perfectly
""")


def _show_vision_example():
    print("""
from megaparse.parser.megaparse_vision import MegaParseVision
from langchain_openai import ChatOpenAI

# Initialize with a multimodal model
model = ChatOpenAI(model="gpt-4o", api_key="sk-...")
parser = MegaParseVision(model=model)

# Parse a document (each page sent as image to the model)
response = parser.convert("document.pdf")
print(response)  # High-quality Markdown output

# Supported multimodal models:
# - GPT-4o, GPT-4 Turbo (OpenAI)
# - Claude 3.5 Sonnet, Claude 4 Opus/Sonnet (Anthropic)
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Vision parsing (GPT-4o)")
    print("2. Vision parsing (Claude)")
    print("3. Standard vs Vision comparison")
    choice = input("Enter 1/2/3 (default=3): ").strip() or "3"

    {
        "1": vision_parse_openai,
        "2": vision_parse_anthropic,
        "3": compare_standard_vs_vision,
    }[choice]()
