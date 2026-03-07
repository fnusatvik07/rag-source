"""
Dedicated table extraction from PDFs using pdfplumber.

Tables in PDFs are notoriously difficult to extract because PDFs store
text as positioned characters, not as structured table elements. This
script demonstrates robust table extraction and conversion to multiple
output formats, including natural language descriptions suitable for RAG.

Strengths:  Best-in-class table detection, multiple output formats,
            configurable detection strategies.
Weaknesses: Borderless tables may be missed, complex merged cells
            can be misinterpreted.

Usage:
    uv run python unstructured_documents/01_pdf/04_table_extraction.py
"""

import csv
import io
import sys
from pathlib import Path

import pdfplumber

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
TABLES_PDF = SAMPLE_DIR / "tables.pdf"


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------


def extract_all_tables(pdf_path: Path) -> list[dict]:
    """
    Extract every table from every page of a PDF.

    Returns a list of dicts, each containing:
      - page: page number (1-based)
      - table_index: table index on that page (0-based)
      - header: list of column names (first row)
      - rows: list of data rows (each a list of strings)
      - raw: the raw list-of-lists from pdfplumber
    """
    results = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                # Clean cell values: replace None with empty string, strip whitespace
                cleaned = []
                for row in table:
                    cleaned.append([(cell.strip() if cell else "") for cell in row])
                header = cleaned[0]
                rows = cleaned[1:]
                results.append(
                    {
                        "page": page_num + 1,
                        "table_index": table_idx,
                        "header": header,
                        "rows": rows,
                        "raw": table,
                    }
                )
    return results


# ---------------------------------------------------------------------------
# Format converters
# ---------------------------------------------------------------------------


def table_to_list_of_dicts(header: list[str], rows: list[list[str]]) -> list[dict]:
    """Convert a table to a list of dictionaries (one per row)."""
    return [dict(zip(header, row)) for row in rows]


def table_to_markdown(header: list[str], rows: list[list[str]]) -> str:
    """Convert a table to a Markdown-formatted string."""
    # Calculate column widths
    widths = [len(h) for h in header]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    def format_row(cells):
        parts = []
        for i, cell in enumerate(cells):
            w = widths[i] if i < len(widths) else len(cell)
            parts.append(cell.ljust(w))
        return "| " + " | ".join(parts) + " |"

    lines = [format_row(header)]
    lines.append("| " + " | ".join("-" * w for w in widths) + " |")
    for row in rows:
        lines.append(format_row(row))
    return "\n".join(lines)


def table_to_csv_string(header: list[str], rows: list[list[str]]) -> str:
    """Convert a table to a CSV-formatted string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()


def table_to_natural_language(
    header: list[str],
    rows: list[list[str]],
    table_title: str = "Table",
) -> str:
    """
    Convert a table to natural language descriptions for RAG.

    Tables embedded in vector stores as raw grids are hard for retrieval
    to match against natural language queries. Converting each row to a
    sentence improves semantic search recall.

    Example output:
      "Product PRD-001 (Wireless Mouse) is in the Electronics category,
       with a quantity of 1,250 at a unit price of $29.99, stored in
       Warehouse A."
    """
    descriptions = [f"{table_title} contains {len(rows)} records.\n"]

    for row in rows:
        # Build a sentence from column-value pairs
        parts = []
        for col, val in zip(header, row):
            if val:
                parts.append(f"{col}: {val}")
        sentence = "; ".join(parts) + "."
        descriptions.append(sentence)

    return "\n".join(descriptions)


# ---------------------------------------------------------------------------
# Demonstrations
# ---------------------------------------------------------------------------


def demo_extract_tables():
    """Extract and display all tables."""
    print("=" * 70)
    print("1. EXTRACT ALL TABLES FROM tables.pdf")
    print("=" * 70)

    tables = extract_all_tables(TABLES_PDF)
    print(f"\n  Total tables extracted: {len(tables)}")

    for t in tables:
        print(f"\n  --- Page {t['page']}, Table {t['table_index'] + 1} ---")
        print(f"  Columns: {t['header']}")
        print(f"  Rows: {len(t['rows'])}")
        # Show first 3 rows
        for row in t["rows"][:3]:
            print(f"    {row}")
        if len(t["rows"]) > 3:
            print(f"    ... ({len(t['rows']) - 3} more rows)")


def demo_format_conversions():
    """Show different output formats for the same table."""
    print("\n" + "=" * 70)
    print("2. TABLE FORMAT CONVERSIONS")
    print("=" * 70)

    tables = extract_all_tables(TABLES_PDF)
    if not tables:
        print("  No tables found!")
        return

    # Use the first table (Product Inventory) for demonstrations
    t = tables[0]
    header = t["header"]
    rows = t["rows"]

    # --- List of dicts ---
    print("\n  --- Format: List of Dictionaries ---")
    dicts = table_to_list_of_dicts(header, rows)
    for d in dicts[:3]:
        print(f"    {d}")
    if len(dicts) > 3:
        print(f"    ... ({len(dicts) - 3} more)")

    # --- Markdown ---
    print("\n  --- Format: Markdown ---")
    md = table_to_markdown(header, rows[:5])
    for line in md.split("\n"):
        print(f"    {line}")
    if len(rows) > 5:
        print(f"    ... ({len(rows) - 5} more rows)")

    # --- CSV string ---
    print("\n  --- Format: CSV ---")
    csv_str = table_to_csv_string(header, rows[:5])
    for line in csv_str.strip().split("\n"):
        print(f"    {line}")
    if len(rows) > 5:
        print(f"    ... ({len(rows) - 5} more rows)")


def demo_natural_language():
    """Show table-to-natural-language conversion for RAG."""
    print("\n" + "=" * 70)
    print("3. TABLES AS NATURAL LANGUAGE (for RAG embeddings)")
    print("=" * 70)

    tables = extract_all_tables(TABLES_PDF)

    # Table titles (we know them from the PDF structure)
    titles = [
        "Product Inventory",
        "Quarterly Revenue by Region",
        "Employee Directory",
        "Project Status Overview",
    ]

    for i, t in enumerate(tables):
        title = titles[i] if i < len(titles) else f"Table {i + 1}"
        nl = table_to_natural_language(t["header"], t["rows"], table_title=title)

        print(f"\n  --- {title} ---")
        # Show first 5 lines
        lines = nl.split("\n")
        for line in lines[:6]:
            print(f"    {line}")
        if len(lines) > 6:
            print(f"    ... ({len(lines) - 6} more lines)")

    print("\n  Why natural language?")
    print("  - Vector search matches queries like 'What products are in Warehouse A?'")
    print("    better against sentences than against raw table grids.")
    print("  - Each row becomes a retrievable passage with full context.")
    print("  - Column names provide schema context within each sentence.")


def demo_rag_preparation():
    """Show full pipeline: extract -> convert -> chunk for RAG."""
    print("\n" + "=" * 70)
    print("4. FULL RAG PREPARATION PIPELINE")
    print("=" * 70)

    tables = extract_all_tables(TABLES_PDF)
    if not tables:
        print("  No tables found!")
        return

    # Combine all tables into RAG-ready passages
    all_passages = []
    titles = [
        "Product Inventory",
        "Quarterly Revenue by Region",
        "Employee Directory",
        "Project Status Overview",
    ]

    for i, t in enumerate(tables):
        title = titles[i] if i < len(titles) else f"Table {i + 1}"

        # Strategy 1: One passage per table (markdown format)
        md_passage = f"## {title}\n\n" + table_to_markdown(t["header"], t["rows"])
        all_passages.append(
            {
                "type": "table_markdown",
                "source": f"tables.pdf, page {t['page']}",
                "title": title,
                "content": md_passage,
            }
        )

        # Strategy 2: One passage per row (natural language)
        for row_idx, row in enumerate(t["rows"]):
            parts = []
            for col, val in zip(t["header"], row):
                if val:
                    parts.append(f"{col} is {val}")
            sentence = f"In the {title} table: " + ", ".join(parts) + "."
            all_passages.append(
                {
                    "type": "table_row_nl",
                    "source": f"tables.pdf, page {t['page']}, row {row_idx + 1}",
                    "title": title,
                    "content": sentence,
                }
            )

    print(f"\n  Total RAG passages generated: {len(all_passages)}")

    # Count by type
    by_type = {}
    for p in all_passages:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    for ptype, count in by_type.items():
        print(f"    {ptype}: {count} passages")

    # Show a few examples
    print("\n  --- Example: Markdown table passage ---")
    md_example = [p for p in all_passages if p["type"] == "table_markdown"][0]
    preview = md_example["content"][:300]
    for line in preview.split("\n")[:8]:
        print(f"    {line}")
    print("    ...")

    print("\n  --- Example: Natural language row passages ---")
    nl_examples = [p for p in all_passages if p["type"] == "table_row_nl"][:3]
    for p in nl_examples:
        print(f"    [{p['source']}]")
        print(f"    {p['content'][:100]}")


if __name__ == "__main__":
    if not TABLES_PDF.exists():
        print(f"ERROR: {TABLES_PDF} not found.")
        print("Run generate_samples.py first:")
        print("  uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py")
        sys.exit(1)

    demo_extract_tables()
    demo_format_conversions()
    demo_natural_language()
    demo_rag_preparation()

    print("\n" + "=" * 70)
    print("Done. Table extraction is critical for RAG on data-heavy documents.")
    print("Key insight: converting tables to natural language improves retrieval.")
    print("=" * 70)
