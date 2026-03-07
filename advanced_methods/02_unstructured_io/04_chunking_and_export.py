"""
Unstructured.io - Chunking & Export
=====================================
Unstructured provides chunking strategies to split elements into
RAG-ready chunks, plus export to various formats.

Chunking strategies:
- chunk_by_title: Groups elements under their nearest title/heading.
  Respects document structure for semantic chunking.

Export options:
- elements_to_json(): Serialize to JSON
- elements_to_text(): Plain text concatenation
- convert_to_dataframe(): Pandas DataFrame
- elements_to_dicts(): List of dictionaries

uv pip install "unstructured[all-docs]"
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def chunk_by_title_demo():
    """Chunk elements by title for semantic RAG chunks."""
    from unstructured.chunking.title import chunk_by_title
    from unstructured.partition.auto import partition

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf")
    elements = partition(filename=pdf_path)

    # Chunk by title with size constraints
    chunks = chunk_by_title(
        elements,
        max_characters=1000,  # Max chunk size
        new_after_n_chars=500,  # Soft limit to start new chunk
        combine_text_under_n_chars=200,  # Merge small chunks
    )

    print("=" * 60)
    print(f"CHUNK BY TITLE: {len(elements)} elements -> {len(chunks)} chunks")
    print("=" * 60)

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i + 1} [{type(chunk).__name__}] ---")
        text = str(chunk)
        print(f"  Length: {len(text)} chars")
        print(f"  Text: {text[:200]}...")


def export_formats_demo():
    """Show different export formats for partitioned elements."""
    from unstructured.partition.auto import partition

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf")
    elements = partition(filename=pdf_path)

    print("=" * 60)
    print("EXPORT FORMATS")
    print("=" * 60)

    # 1. Plain text
    text = "\n\n".join([str(el) for el in elements])
    print(f"\n--- Plain Text ({len(text)} chars) ---")
    print(text[:300])

    # 2. JSON
    import json

    from unstructured.staging.base import elements_to_json

    json_str = elements_to_json(elements)
    print(f"\n--- JSON ({len(json_str)} chars) ---")
    parsed = json.loads(json_str)
    print(json.dumps(parsed[:2], indent=2)[:400])

    # 3. Dict list
    from unstructured.staging.base import elements_to_dicts

    dicts = elements_to_dicts(elements)
    print(f"\n--- Dicts ({len(dicts)} items) ---")
    if dicts:
        print(f"  Keys: {list(dicts[0].keys())}")
        print(f"  First: type={dicts[0].get('type')}, text={dicts[0].get('text', '')[:100]}")

    # 4. DataFrame
    try:
        from unstructured.staging.base import convert_to_dataframe

        df = convert_to_dataframe(elements)
        print(f"\n--- DataFrame ({len(df)} rows) ---")
        print(df[["type", "text"]].head().to_string())
    except Exception as e:
        print(f"\n--- DataFrame: {e} ---")


def metadata_exploration():
    """Explore the rich metadata attached to each element."""
    from unstructured.partition.auto import partition

    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "tables.pdf")
    elements = partition(filename=pdf_path)

    print("=" * 60)
    print("ELEMENT METADATA")
    print("=" * 60)

    for el in elements[:5]:
        print(f"\n[{type(el).__name__}] {str(el)[:80]}")
        meta = el.metadata
        attrs = [
            "filename",
            "file_directory",
            "page_number",
            "coordinates",
            "text_as_html",
            "languages",
            "detection_class_prob",
        ]
        for attr in attrs:
            val = getattr(meta, attr, None)
            if val is not None:
                val_str = str(val)[:100]
                print(f"  .metadata.{attr} = {val_str}")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Chunk by title")
    print("2. Export formats")
    print("3. Metadata exploration")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    {"1": chunk_by_title_demo, "2": export_formats_demo, "3": metadata_exploration}[choice]()
