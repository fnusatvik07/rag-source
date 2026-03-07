"""
Spreadsheet Extraction Method 3: csv module (stdlib)

Python's built-in csv module is lightweight with zero dependencies.
Use this when you don't need pandas overhead or for simple CSV processing.

Best for: Simple CSV files, minimal dependencies, streaming large files.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import (
    chunk_by_recursive_split,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def extract_csv_basic(csv_path: Path) -> tuple[list[str], list[list[str]]]:
    """Extract CSV as headers and rows."""
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows


def extract_csv_as_dicts(csv_path: Path) -> list[dict]:
    """Extract CSV as list of dictionaries (each row is a dict)."""
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def csv_to_natural_language(csv_path: Path) -> str:
    """Convert CSV to natural language description for RAG."""
    records = extract_csv_as_dicts(csv_path)
    if not records:
        return ""

    headers = list(records[0].keys())
    lines = [
        f"This dataset contains {len(records)} records.",
        f"Fields: {', '.join(headers)}\n",
    ]

    for record in records:
        parts = [f"{k}: {v}" for k, v in record.items() if v]
        lines.append(f"- {'; '.join(parts)}")

    return "\n".join(lines)


def csv_row_to_sentence(headers: list[str], row: list[str]) -> str:
    """Convert a single CSV row to a descriptive sentence."""
    parts = []
    for header, value in zip(headers, row):
        if value:
            parts.append(f"the {header.lower().replace('_', ' ')} is {value}")
    return ". ".join(parts).capitalize() + "."


if __name__ == "__main__":
    csv_path = SAMPLE_DIR / "simple_data.csv"
    products_path = SAMPLE_DIR / "products.csv"

    # --- Basic extraction ---
    print("=" * 60)
    print("1. BASIC CSV EXTRACTION (simple_data.csv)")
    print("=" * 60)
    headers, rows = extract_csv_basic(csv_path)
    print(f"Headers: {headers}")
    print(f"Rows: {len(rows)}")
    for row in rows[:3]:
        print(f"  {row}")

    # --- Dict extraction ---
    print(f"\n{'=' * 60}")
    print("2. DICT-BASED EXTRACTION")
    print("=" * 60)
    records = extract_csv_as_dicts(csv_path)
    for rec in records[:3]:
        print(f"  {rec}")

    # --- Natural language conversion ---
    print(f"\n{'=' * 60}")
    print("3. NATURAL LANGUAGE CONVERSION (products.csv)")
    print("=" * 60)
    nl_text = csv_to_natural_language(products_path)
    print(nl_text[:500])

    # --- Row-to-sentence conversion ---
    print(f"\n{'=' * 60}")
    print("4. ROW-TO-SENTENCE CONVERSION")
    print("=" * 60)
    headers, rows = extract_csv_basic(csv_path)
    for row in rows[:4]:
        sentence = csv_row_to_sentence(headers, row)
        print(f"  {sentence}")

    # --- Chunking ---
    print(f"\n{'=' * 60}")
    print("5. CHUNKED OUTPUT FOR RAG")
    print("=" * 60)
    nl_text = csv_to_natural_language(products_path)
    chunks = chunk_by_recursive_split(nl_text, chunk_size=300)
    preview_chunks(chunks)
