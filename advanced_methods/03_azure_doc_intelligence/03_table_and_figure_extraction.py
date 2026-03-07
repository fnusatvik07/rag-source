"""
Azure AI Document Intelligence - Table & Figure Extraction
=============================================================
Azure excels at extracting structured tables and detecting figures.
Tables are returned with full row/column structure, spanning cells,
and optional HTML output. Figures include bounding regions and captions.

uv pip install azure-ai-documentintelligence
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def table_extraction():
    """Extract tables with full structure from PDF."""
    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
    except ImportError:
        print("Install: uv pip install azure-ai-documentintelligence")
        _show_table_example()
        return

    endpoint = os.environ.get("AZURE_DOC_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("AZURE_DOC_INTELLIGENCE_KEY")

    if not endpoint or not key:
        print("=" * 60)
        print("TABLE EXTRACTION (requires Azure credentials)")
        print("=" * 60)
        _show_table_example()
        return

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf"

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", body=f)
    result = poller.result()

    print("=" * 60)
    print("TABLE EXTRACTION RESULTS")
    print("=" * 60)

    if not result.tables:
        print("No tables found.")
        return

    for i, table in enumerate(result.tables):
        print(f"\n--- Table {i + 1} ---")
        print(f"  Rows: {table.row_count}, Columns: {table.column_count}")
        print(f"  Page: {table.bounding_regions[0].page_number if table.bounding_regions else 'N/A'}")

        # Build a 2D grid
        grid = {}
        for cell in table.cells:
            grid[(cell.row_index, cell.column_index)] = cell.content

        # Print as formatted table
        for row in range(min(table.row_count, 5)):
            row_data = []
            for col in range(table.column_count):
                row_data.append(grid.get((row, col), ""))
            print(f"  | {' | '.join(row_data)} |")

        if table.row_count > 5:
            print(f"  ... ({table.row_count - 5} more rows)")


def convert_table_to_markdown():
    """Convert extracted tables to Markdown format for RAG."""
    print("=" * 60)
    print("TABLE TO MARKDOWN FOR RAG")
    print("=" * 60)
    print("""
# After extracting tables with Azure, convert to text for RAG:

def table_to_markdown(table):
    grid = {}
    for cell in table.cells:
        grid[(cell.row_index, cell.column_index)] = cell.content

    lines = []
    for row in range(table.row_count):
        cells = [grid.get((row, col), "") for col in range(table.column_count)]
        lines.append("| " + " | ".join(cells) + " |")
        if row == 0:
            lines.append("| " + " | ".join(["---"] * table.column_count) + " |")

    return "\\n".join(lines)

# Alternative: Convert to natural language for better RAG retrieval
def table_to_natural_language(table):
    grid = {}
    for cell in table.cells:
        grid[(cell.row_index, cell.column_index)] = cell.content

    headers = [grid.get((0, col), f"Col{col}") for col in range(table.column_count)]
    sentences = []
    for row in range(1, table.row_count):
        parts = []
        for col in range(table.column_count):
            val = grid.get((row, col), "")
            if val:
                parts.append(f"{headers[col]}: {val}")
        sentences.append(", ".join(parts))

    return ". ".join(sentences) + "."
""")


def _show_table_example():
    print("""
# Table extraction returns structured data:
result = poller.result()

for table in result.tables:
    print(f"Table: {table.row_count}x{table.column_count}")

    for cell in table.cells:
        print(f"  [{cell.row_index},{cell.column_index}] "
              f"kind={cell.kind} content='{cell.content}'")
        # cell.kind: 'columnHeader', 'rowHeader', 'content', 'stubHead'
        # cell.column_span / cell.row_span for merged cells
        # cell.bounding_regions for coordinates

# Figure detection:
if result.figures:
    for fig in result.figures:
        print(f"Figure on page {fig.bounding_regions[0].page_number}")
        if fig.caption:
            print(f"  Caption: {fig.caption.content}")
""")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Table extraction")
    print("2. Table to Markdown/Natural Language conversion")
    choice = input("Enter 1/2 (default=1): ").strip() or "1"

    if choice == "1":
        table_extraction()
    else:
        convert_table_to_markdown()
