"""
Docling - Framework Integrations
==================================
Docling integrates with popular RAG frameworks:
- LlamaIndex: via DoclingReader and DoclingNodeParser
- LangChain: via DoclingLoader

These integrations let you use Docling's parsing directly in your
RAG pipeline with minimal code.

uv pip install docling
uv pip install llama-index-readers-docling  # for LlamaIndex
uv pip install langchain-docling            # for LangChain
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def llamaindex_integration():
    """Use Docling with LlamaIndex via DoclingReader."""
    try:
        from llama_index.readers.docling import DoclingReader
    except ImportError:
        print("Install: uv pip install llama-index-readers-docling")
        print("\nExample code (not runnable without install):")
        print("""
from llama_index.readers.docling import DoclingReader

reader = DoclingReader()
documents = reader.load_data(
    file_path="path/to/document.pdf"
)

# Each document has .text and .metadata
for doc in documents:
    print(f"Text length: {len(doc.text)}")
    print(f"Metadata: {doc.metadata}")
""")
        return

    reader = DoclingReader()
    pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf")
    documents = reader.load_data(file_path=pdf_path)

    print("=" * 60)
    print("DOCLING + LLAMAINDEX")
    print("=" * 60)
    for i, doc in enumerate(documents):
        print(f"\nDocument {i + 1}:")
        print(f"  Text length: {len(doc.text)}")
        print(f"  Preview: {doc.text[:200]}...")


def langchain_integration():
    """Use Docling with LangChain via DoclingLoader."""
    try:
        from langchain_docling import DoclingLoader
    except ImportError:
        print("Install: uv pip install langchain-docling")
        print("\nExample code (not runnable without install):")
        print("""
from langchain_docling import DoclingLoader

loader = DoclingLoader(
    file_path="path/to/document.pdf",
    export_type="markdown",  # or "text"
)
documents = loader.load()

for doc in documents:
    print(f"Content: {doc.page_content[:200]}")
    print(f"Metadata: {doc.metadata}")
""")
        return

    loader = DoclingLoader(
        file_path=str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf"),
        export_type="markdown",
    )
    documents = loader.load()

    print("=" * 60)
    print("DOCLING + LANGCHAIN")
    print("=" * 60)
    for i, doc in enumerate(documents):
        print(f"\nDocument {i + 1}:")
        print(f"  Content: {doc.page_content[:200]}...")
        print(f"  Metadata: {doc.metadata}")


if __name__ == "__main__":
    print("Choose demo:")
    print("1. LlamaIndex integration")
    print("2. LangChain integration")
    choice = input("Enter 1/2 (default=1): ").strip() or "1"

    if choice == "1":
        llamaindex_integration()
    elif choice == "2":
        langchain_integration()
