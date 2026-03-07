"""
LlamaParse + LlamaIndex RAG Pipeline
=======================================
LlamaParse integrates natively with LlamaIndex to create
complete RAG pipelines: parse -> chunk -> embed -> index -> query.

uv pip install llama-parse llama-index
"""

import os
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def llamaindex_rag_pipeline():
    """Build a complete RAG pipeline with LlamaParse + LlamaIndex."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    print("=" * 60)
    print("LLAMAPARSE + LLAMAINDEX RAG PIPELINE")
    print("=" * 60)

    if not api_key:
        print("\nRequires: LLAMA_CLOUD_API_KEY and OPENAI_API_KEY")
        _show_pipeline_code()
        return

    try:
        from llama_index.core import VectorStoreIndex
        from llama_parse import LlamaParse
    except ImportError:
        print("Install: uv pip install llama-parse llama-index")
        _show_pipeline_code()
        return

    # Step 1: Parse documents
    parser = LlamaParse(api_key=api_key, result_type="markdown")
    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "mixed_content.pdf")
    documents = parser.load_data(pdf_path)

    print(f"\nStep 1: Parsed {len(documents)} document(s)")
    for doc in documents:
        print(f"  - {len(doc.text)} chars")

    # Step 2: Create index (requires OpenAI key for embeddings)
    if openai_key:
        index = VectorStoreIndex.from_documents(documents)
        print("Step 2: Created vector index")

        # Step 3: Query
        query_engine = index.as_query_engine()
        response = query_engine.query("What are the main topics in this document?")
        print(f"\nStep 3: Query response:\n{response}")
    else:
        print("Step 2: Skipped (set OPENAI_API_KEY for embedding)")
        print("\nParsed content preview:")
        print(documents[0].text[:500])


def _show_pipeline_code():
    print("""
# Complete RAG pipeline with LlamaParse + LlamaIndex:

from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex

# 1. Parse
parser = LlamaParse(api_key="llx-...", result_type="markdown")
documents = parser.load_data("document.pdf")

# 2. Index (uses OpenAI embeddings by default)
index = VectorStoreIndex.from_documents(documents)

# 3. Query
query_engine = index.as_query_engine()
response = query_engine.query("What is this document about?")
print(response)

# With custom chunking:
from llama_index.core.node_parser import MarkdownNodeParser

parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents)
index = VectorStoreIndex(nodes)
""")


if __name__ == "__main__":
    llamaindex_rag_pipeline()
