"""
Docling - Chunking for RAG
============================
Docling provides built-in chunkers that leverage the document's structure
(headings, sections, tables) to create semantically meaningful chunks
for RAG systems.

Key chunkers:
- HierarchicalChunker: Splits by document structure (headings, sections)
- HybridChunker: Combines hierarchical structure with token-based limits
  using a tokenizer (e.g., from a specific embedding model)

These chunkers preserve context by including heading hierarchies in each chunk.

uv pip install docling docling-core
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def hierarchical_chunking():
    """Use HierarchicalChunker for structure-aware splitting."""
    from docling.document_converter import DocumentConverter
    from docling_core.transforms.chunker import HierarchicalChunker

    converter = DocumentConverter()
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf"
    result = converter.convert(str(pdf_path))

    chunker = HierarchicalChunker()
    chunks = list(chunker.chunk(result.document))

    print("=" * 60)
    print(f"HIERARCHICAL CHUNKING - {len(chunks)} chunks")
    print("=" * 60)

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Text: {chunk.text[:200]}...")
        if hasattr(chunk, "meta") and chunk.meta:
            print(f"Metadata: {chunk.meta}")
        print()


def hybrid_chunking():
    """Use HybridChunker with token limits for embedding models."""
    from docling.document_converter import DocumentConverter
    from docling_core.transforms.chunker import HybridChunker

    converter = DocumentConverter()
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf"
    result = converter.convert(str(pdf_path))

    # HybridChunker respects both structure AND token limits
    chunker = HybridChunker(
        tokenizer="sentence-transformers/all-MiniLM-L6-v2",  # or any HF tokenizer
        max_tokens=512,
        merge_peers=True,
    )
    chunks = list(chunker.chunk(result.document))

    print("=" * 60)
    print(f"HYBRID CHUNKING (max 512 tokens) - {len(chunks)} chunks")
    print("=" * 60)

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Text: {chunk.text[:200]}...")
        if hasattr(chunk, "meta") and chunk.meta:
            print(f"Metadata: {chunk.meta}")


def compare_chunking_strategies():
    """Compare hierarchical vs hybrid chunking on the same document."""
    from docling.document_converter import DocumentConverter
    from docling_core.transforms.chunker import HierarchicalChunker, HybridChunker

    converter = DocumentConverter()
    pdf_path = SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf"
    result = converter.convert(str(pdf_path))

    hier_chunks = list(HierarchicalChunker().chunk(result.document))

    hybrid_chunks = list(
        HybridChunker(
            tokenizer="sentence-transformers/all-MiniLM-L6-v2",
            max_tokens=256,
        ).chunk(result.document)
    )

    print("=" * 60)
    print("CHUNKING STRATEGY COMPARISON")
    print("=" * 60)
    print(f"\nHierarchical: {len(hier_chunks)} chunks")
    for i, c in enumerate(hier_chunks[:3]):
        print(f"  [{i + 1}] {len(c.text)} chars: {c.text[:80]}...")

    print(f"\nHybrid (256 tokens): {len(hybrid_chunks)} chunks")
    for i, c in enumerate(hybrid_chunks[:3]):
        print(f"  [{i + 1}] {len(c.text)} chars: {c.text[:80]}...")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. Hierarchical chunking")
    print("2. Hybrid chunking (token-limited)")
    print("3. Compare strategies")
    choice = input("Enter 1/2/3 (default=1): ").strip() or "1"

    if choice == "1":
        hierarchical_chunking()
    elif choice == "2":
        hybrid_chunking()
    elif choice == "3":
        compare_chunking_strategies()
