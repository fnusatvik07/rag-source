"""
Azure AI Document Intelligence - Layout Extraction
=====================================================
Azure Document Intelligence (formerly Form Recognizer) is Microsoft's
cloud-based AI service for extracting text, tables, structure, and
key-value pairs from documents.

The "prebuilt-layout" model extracts:
- Text content with reading order
- Tables with row/column structure
- Selection marks (checkboxes)
- Paragraphs with roles (title, sectionHeading, footnote, etc.)
- Figures and their captions
- Barcodes and formulas

Requires: Azure subscription + Document Intelligence resource
uv pip install azure-ai-documentintelligence

Free tier: 500 pages/month
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def layout_extraction():
    """Extract layout from a PDF using prebuilt-layout model."""
    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
    except ImportError:
        print("Install: uv pip install azure-ai-documentintelligence")
        _show_example_code()
        return

    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not endpoint or not key:
        print("=" * 60)
        print("AZURE DOCUMENT INTELLIGENCE - LAYOUT EXTRACTION")
        print("=" * 60)
        print("\nRequires Azure credentials. Set environment variables:")
        print("  export AZURE_DOC_INTELLIGENCE_ENDPOINT='https://<resource>.cognitiveservices.azure.com/'")
        print("  export AZURE_DOC_INTELLIGENCE_KEY='<your-api-key>'")
        print("\nSetup steps:")
        print("  1. Create Azure account (free tier available)")
        print("  2. Create Document Intelligence resource in Azure Portal")
        print("  3. Copy endpoint and key from resource's Keys and Endpoint page")
        print("\nExample code that would run with credentials:")
        _show_example_code()
        return

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf"

    print("=" * 60)
    print("AZURE LAYOUT EXTRACTION")
    print("=" * 60)

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", body=f)
    result = poller.result()

    # Pages
    for page in result.pages:
        print(f"\n--- Page {page.page_number} ---")
        print(f"  Size: {page.width} x {page.height} {page.unit}")
        print(f"  Lines: {len(page.lines or [])}")
        print(f"  Words: {len(page.words or [])}")

        if page.lines:
            for line in page.lines[:5]:
                print(f"  Line: {line.content}")

    # Tables
    if result.tables:
        print(f"\n--- Tables: {len(result.tables)} found ---")
        for i, table in enumerate(result.tables):
            print(f"\n  Table {i + 1}: {table.row_count} rows x {table.column_count} cols")
            for cell in table.cells[:6]:
                print(f"    [{cell.row_index},{cell.column_index}] = {cell.content}")

    # Paragraphs with roles
    if result.paragraphs:
        print(f"\n--- Paragraphs: {len(result.paragraphs)} found ---")
        for para in result.paragraphs[:5]:
            role = para.role if para.role else "body"
            print(f"  [{role}] {para.content[:100]}")


def _show_example_code():
    """Display example code for reference."""
    print("""
# --- Example: Layout Extraction ---
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

client = DocumentIntelligenceClient(
    endpoint="https://<resource>.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<api-key>")
)

with open("document.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-layout", body=f)
result = poller.result()

# Access pages, text lines, tables, paragraphs
for page in result.pages:
    for line in page.lines:
        print(line.content)

for table in result.tables:
    for cell in table.cells:
        print(f"[{cell.row_index},{cell.column_index}] {cell.content}")

for para in result.paragraphs:
    print(f"[{para.role}] {para.content}")
""")


def markdown_output():
    """Get document content as Markdown (Azure's built-in conversion)."""
    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
    except ImportError:
        print("Install: uv pip install azure-ai-documentintelligence")
        return

    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not endpoint or not key:
        print("=" * 60)
        print("AZURE - MARKDOWN OUTPUT")
        print("=" * 60)
        print("\nRequires Azure credentials (see layout_extraction for setup).")
        print("\nExample:")
        print("""
poller = client.begin_analyze_document(
    "prebuilt-layout",
    body=f,
    output_content_format="markdown"  # Request markdown output
)
result = poller.result()
print(result.content)  # Full document as Markdown
""")
        return

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf"

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            body=f,
            output_content_format="markdown",
        )
    result = poller.result()

    print("=" * 60)
    print("MARKDOWN OUTPUT")
    print("=" * 60)
    print(result.content[:1000])


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Layout extraction (pages, tables, paragraphs)")
    print("2. Markdown output format")
    choice = input("Enter 1/2 (default=1): ").strip() or "1"

    if choice == "1":
        layout_extraction()
    else:
        markdown_output()
