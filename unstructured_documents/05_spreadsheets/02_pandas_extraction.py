"""
Spreadsheet Extraction Method 2: pandas

pandas provides high-level dataframe operations for reading spreadsheets.
It's the best choice when you need data analysis or transformation alongside extraction.

Best for: Data analysis, aggregation, filtering, type-aware extraction, large datasets.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from unstructured_documents.shared.chunking import (
    chunk_by_recursive_split,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def extract_all_sheets(xlsx_path: Path) -> dict[str, pd.DataFrame]:
    """Read all sheets into DataFrames."""
    return pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")


def dataframe_to_natural_language(df: pd.DataFrame, sheet_name: str) -> str:
    """
    Convert a DataFrame to natural language for RAG.
    Includes summary statistics and row-by-row descriptions.
    """
    lines = [f"## {sheet_name}\n"]

    # Summary
    lines.append(f"This dataset contains {len(df)} rows and {len(df.columns)} columns.")
    lines.append(f"Columns: {', '.join(df.columns.astype(str))}\n")

    # Add summary stats for numeric columns
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        lines.append("Numeric column statistics:")
        for col in numeric_cols:
            lines.append(f"  - {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}")
        lines.append("")

    # Row descriptions
    lines.append("Records:")
    for _, row in df.iterrows():
        parts = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
        lines.append(f"- {'; '.join(parts)}")

    return "\n".join(lines)


def dataframe_to_row_chunks(df: pd.DataFrame, sheet_name: str, rows_per_chunk: int = 5) -> list[str]:
    """
    Convert DataFrame to chunks, grouping N rows per chunk.
    Each chunk includes column headers for context.
    """
    chunks = []
    headers = list(df.columns)

    for i in range(0, len(df), rows_per_chunk):
        batch = df.iloc[i : i + rows_per_chunk]
        lines = [f"[{sheet_name} - rows {i + 1} to {min(i + rows_per_chunk, len(df))}]"]
        lines.append(f"Columns: {', '.join(str(h) for h in headers)}\n")
        for _, row in batch.iterrows():
            parts = [f"{col}: {val}" for col, val in row.items() if pd.notna(val)]
            lines.append(f"- {'; '.join(parts)}")
        chunks.append("\n".join(lines))

    return chunks


if __name__ == "__main__":
    xlsx_path = SAMPLE_DIR / "multi_sheet.xlsx"
    csv_path = SAMPLE_DIR / "products.csv"

    # --- Read all sheets ---
    print("=" * 60)
    print("1. READ ALL SHEETS AS DATAFRAMES")
    print("=" * 60)
    sheets = extract_all_sheets(xlsx_path)
    for name, df in sheets.items():
        print(f"\nSheet: {name}")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Dtypes:\n{df.dtypes.to_string()}")

    # --- Natural language conversion ---
    print(f"\n{'=' * 60}")
    print("2. NATURAL LANGUAGE CONVERSION")
    print("=" * 60)
    for name, df in sheets.items():
        nl_text = dataframe_to_natural_language(df, name)
        print(f"\n{nl_text[:400]}")
        if len(nl_text) > 400:
            print("...")

    # --- Row-based chunking ---
    print(f"\n{'=' * 60}")
    print("3. ROW-BASED CHUNKING (5 rows per chunk)")
    print("=" * 60)
    emp_df = sheets["Employee Directory"]
    chunks = dataframe_to_row_chunks(emp_df, "Employee Directory", rows_per_chunk=3)
    preview_chunks(chunks)

    # --- CSV reading ---
    print(f"\n{'=' * 60}")
    print("4. CSV READING WITH PANDAS")
    print("=" * 60)
    products_df = pd.read_csv(csv_path)
    print(f"Shape: {products_df.shape}")
    print(f"Columns: {list(products_df.columns)}")
    print("\nFirst 3 rows:")
    print(products_df.head(3).to_string())

    # Convert to natural language
    nl = dataframe_to_natural_language(products_df, "Products")
    chunks = chunk_by_recursive_split(nl, chunk_size=400)
    print(f"\nChunked into {len(chunks)} chunks for RAG")
    preview_chunks(chunks)
