"""
Azure AI Document Intelligence - RAG Pipeline Preparation
============================================================
End-to-end example showing how to use Azure Document Intelligence
to prepare documents for a RAG system:

1. Analyze document with prebuilt-layout
2. Extract text with reading order
3. Extract tables and convert to text
4. Create semantic chunks
5. Output ready for embedding

This script works with or without Azure credentials (shows example output).

uv pip install azure-ai-documentintelligence
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def rag_pipeline():
    """Full RAG preparation pipeline with Azure Document Intelligence."""
    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    print("=" * 60)
    print("RAG PIPELINE WITH AZURE DOCUMENT INTELLIGENCE")
    print("=" * 60)

    if not endpoint or not key:
        print("\n[Demo mode - showing pipeline steps with example output]")
        print("\nStep 1: Analyze document with prebuilt-layout")
        print("  client.begin_analyze_document('prebuilt-layout', body=file)")
        print("\nStep 2: Extract paragraphs with roles")
        print("  for para in result.paragraphs:")
        print("      role = para.role  # title, sectionHeading, footnote, etc.")
        print("      text = para.content")
        print("\nStep 3: Extract and convert tables")
        print("  for table in result.tables:")
        print("      markdown_table = table_to_markdown(table)")
        print("\nStep 4: Build semantic chunks")
        print("  Split by headings, merge small sections, respect table boundaries")
        print("\nStep 5: Output chunks for embedding")
        print("  Each chunk includes: text, metadata (page, section, type)")

        _show_pipeline_code()
        return

    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf"

    # Step 1: Analyze
    print("\nStep 1: Analyzing document...")
    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            body=f,
            output_content_format="markdown",
        )
    result = poller.result()

    # Step 2: Get markdown content
    print(f"Step 2: Extracted {len(result.content)} chars of markdown")

    # Step 3: Simple heading-based chunking
    chunks = []
    current_chunk = {"text": "", "metadata": {"page": 1, "section": "intro"}}

    for line in result.content.split("\n"):
        if line.startswith("# ") or line.startswith("## "):
            if current_chunk["text"].strip():
                chunks.append(current_chunk.copy())
            current_chunk = {
                "text": line + "\n",
                "metadata": {"section": line.strip("# ")},
            }
        else:
            current_chunk["text"] += line + "\n"

    if current_chunk["text"].strip():
        chunks.append(current_chunk)

    print(f"Step 3: Created {len(chunks)} semantic chunks")

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n  Chunk {i + 1} ({len(chunk['text'])} chars):")
        print(f"  Section: {chunk['metadata']['section']}")
        print(f"  Preview: {chunk['text'][:150].strip()}...")


def _show_pipeline_code():
    print("""
# --- Complete RAG Pipeline Code ---

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

# 1. Analyze with markdown output
with open("document.pdf", "rb") as f:
    poller = client.begin_analyze_document(
        "prebuilt-layout",
        body=f,
        output_content_format="markdown"
    )
result = poller.result()

# 2. The result.content is now clean Markdown
markdown_text = result.content

# 3. Chunk by headings
import re
sections = re.split(r'(?=^#{1,3} )', markdown_text, flags=re.MULTILINE)

# 4. Create chunks with metadata
chunks = []
for section in sections:
    if section.strip():
        chunks.append({
            "text": section.strip(),
            "metadata": {
                "source": "document.pdf",
                "tables": len(result.tables or []),
                "pages": len(result.pages),
            }
        })

# 5. Ready for embedding!
for chunk in chunks:
    embedding = embed_model.encode(chunk["text"])  # Your embedding model
    vector_store.upsert(embedding, chunk["metadata"])
""")


if __name__ == "__main__":
    rag_pipeline()
