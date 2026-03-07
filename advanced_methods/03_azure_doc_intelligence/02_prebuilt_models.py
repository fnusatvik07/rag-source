"""
Azure AI Document Intelligence - Prebuilt Models
===================================================
Azure offers specialized prebuilt models for common document types:

  prebuilt-read      - OCR optimized for text extraction (130+ languages)
  prebuilt-layout    - Text + tables + structure + figures
  prebuilt-document  - General key-value pair extraction
  prebuilt-invoice   - Invoice field extraction (vendor, total, line items)
  prebuilt-receipt   - Receipt field extraction (merchant, total, items)
  prebuilt-idDocument - ID card/passport extraction (name, DOB, etc.)
  prebuilt-businessCard - Business card extraction
  prebuilt-healthInsuranceCard.us - US health insurance cards

Each model returns structured fields specific to the document type.

uv pip install azure-ai-documentintelligence
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def prebuilt_read():
    """Use prebuilt-read for pure text extraction (OCR optimized)."""
    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
    except ImportError:
        print("Install: uv pip install azure-ai-documentintelligence")
        _show_setup_message("PREBUILT-READ MODEL")
        _show_read_example()
        return

    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not endpoint or not key:
        _show_setup_message("PREBUILT-READ MODEL")
        _show_read_example()
        return

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-read", body=f)
    result = poller.result()

    print("=" * 60)
    print("PREBUILT-READ RESULTS")
    print("=" * 60)
    print(f"Content ({len(result.content)} chars):")
    print(result.content[:500])

    if result.languages:
        print(f"\nDetected languages: {[lang.locale for lang in result.languages]}")


def prebuilt_document():
    """Use prebuilt-document for general key-value pair extraction."""
    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not endpoint or not key:
        _show_setup_message("PREBUILT-DOCUMENT MODEL")
        print("""
# prebuilt-document extracts key-value pairs from any document:
poller = client.begin_analyze_document("prebuilt-document", body=f)
result = poller.result()

for kv in result.key_value_pairs:
    key_text = kv.key.content if kv.key else "N/A"
    value_text = kv.value.content if kv.value else "N/A"
    print(f"  {key_text}: {value_text} (confidence: {kv.confidence})")
""")
        return


def prebuilt_invoice():
    """Use prebuilt-invoice for invoice-specific extraction."""
    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not endpoint or not key:
        _show_setup_message("PREBUILT-INVOICE MODEL")
        print("""
# prebuilt-invoice extracts structured invoice fields:
poller = client.begin_analyze_document("prebuilt-invoice", body=f)
result = poller.result()

for doc in result.documents:
    fields = doc.fields
    print(f"Vendor: {fields.get('VendorName', {}).get('content', 'N/A')}")
    print(f"Invoice #: {fields.get('InvoiceId', {}).get('content', 'N/A')}")
    print(f"Date: {fields.get('InvoiceDate', {}).get('content', 'N/A')}")
    print(f"Total: {fields.get('InvoiceTotal', {}).get('content', 'N/A')}")

    # Line items
    items = fields.get('Items', {}).get('value', [])
    for item in items:
        desc = item.get('value', {}).get('Description', {}).get('content', '')
        amount = item.get('value', {}).get('Amount', {}).get('content', '')
        print(f"  - {desc}: {amount}")
""")
        return


def model_comparison():
    """Overview of when to use each prebuilt model."""
    print("=" * 60)
    print("PREBUILT MODEL COMPARISON")
    print("=" * 60)
    print("""
Model               | Use Case                        | Output
--------------------|---------------------------------|---------------------------
prebuilt-read       | Pure text extraction, OCR       | Text, languages, styles
prebuilt-layout     | Full structure analysis         | Text, tables, paragraphs,
                    |                                 | figures, selection marks
prebuilt-document   | General key-value extraction    | Key-value pairs, tables,
                    |                                 | entities
prebuilt-invoice    | Invoice processing              | Vendor, total, line items,
                    |                                 | dates, tax
prebuilt-receipt    | Receipt scanning                | Merchant, items, total,
                    |                                 | date, tip
prebuilt-idDocument | ID cards, passports, licenses   | Name, DOB, address,
                    |                                 | document number
prebuilt-tax.*      | US tax forms (W2, 1098, 1099)   | Tax-specific fields

CHOOSING THE RIGHT MODEL:
- Need just text?           -> prebuilt-read (fastest, cheapest)
- Need tables + structure?  -> prebuilt-layout
- Need field extraction?    -> prebuilt-document
- Processing invoices?      -> prebuilt-invoice (highest accuracy for invoices)
- Processing receipts?      -> prebuilt-receipt
- Processing IDs?           -> prebuilt-idDocument

PRICING (as of 2025):
- Free tier: 500 pages/month
- prebuilt-read: $0.001/page
- prebuilt-layout: $0.01/page
- prebuilt-invoice/receipt: $0.01/page
- Custom models: $0.05/page (training) + $0.015/page (analysis)
""")


def _show_setup_message(model_name):
    print(f"{'=' * 60}")
    print(f"AZURE - {model_name}")
    print(f"{'=' * 60}")
    print("\nRequires Azure credentials:")
    print("  export AZURE_DOC_INTELLIGENCE_ENDPOINT='https://<resource>.cognitiveservices.azure.com/'")
    print("  export AZURE_DOC_INTELLIGENCE_KEY='<your-api-key>'")


def _show_read_example():
    print("""
# prebuilt-read: optimized pure text extraction
poller = client.begin_analyze_document("prebuilt-read", body=f)
result = poller.result()

# Access full text content
print(result.content)

# Access per-page details
for page in result.pages:
    for line in page.lines:
        print(f"Line: {line.content}")
    for word in page.words:
        print(f"Word: {word.content} (confidence: {word.confidence})")
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. prebuilt-read (text extraction)")
    print("2. prebuilt-document (key-value pairs)")
    print("3. prebuilt-invoice (invoice fields)")
    print("4. Model comparison overview")
    choice = input("Enter 1/2/3/4 (default=4): ").strip() or "4"

    {
        "1": prebuilt_read,
        "2": prebuilt_document,
        "3": prebuilt_invoice,
        "4": model_comparison,
    }[choice]()
