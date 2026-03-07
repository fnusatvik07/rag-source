# RAG Source

The definitive single-repository guide for parsing and preparing documents for Retrieval-Augmented Generation (RAG). Contains working code examples, generated sample documents, and comprehensive guides for every major document type.

## What's Inside

### [Unstructured Documents](unstructured_documents/)

10 document types, 28+ extraction methods, all with working Python code and sample documents:

| Type | Methods | Key Libraries |
|------|---------|---------------|
| PDF | pypdf, pdfplumber, PyMuPDF, OCR, table extraction, comparison | pypdf, pdfplumber, pymupdf, pytesseract |
| Word (DOCX) | python-docx, mammoth, docx2txt | python-docx, mammoth |
| PowerPoint (PPTX) | Basic extraction, structured slide parsing | python-pptx |
| HTML / Web | BeautifulSoup, html2text, trafilatura | bs4, html2text, trafilatura |
| Spreadsheets | openpyxl, pandas, csv stdlib | openpyxl, pandas |
| Images (OCR) | Tesseract, EasyOCR | pytesseract, easyocr |
| Email (EML) | stdlib email parsing, structured extraction | email (stdlib) |
| Markdown / Text | Chunking strategies, AST parsing, semantic chunking | mistune |
| EPUB | ebooklib extraction, full text pipeline | ebooklib |
| Video | Whisper transcription, keyframe extraction | openai-whisper, opencv |

### [Advanced Methods](advanced_methods/)

Production-grade parsing libraries with AI-powered extraction:

| Library | Type | Key Strength | License |
|---------|------|-------------|---------|
| [Docling](advanced_methods/01_docling/) (IBM) | Local | Multi-format, built-in chunking, TableFormer | MIT |
| [Unstructured.io](advanced_methods/02_unstructured_io/) | Local/Cloud | Widest format support, typed elements | Apache 2.0 |
| [Azure Doc Intelligence](advanced_methods/03_azure_doc_intelligence/) | Cloud | Highest accuracy, prebuilt models (invoice, receipt, ID) | Proprietary |
| [LlamaParse](advanced_methods/04_llamaparse/) | Cloud | GenAI-native parsing, LlamaIndex integration | Proprietary |
| [Marker](advanced_methods/05_marker/) | Local | Best PDF-to-Markdown, equation support | GPL |
| [MegaParse](advanced_methods/06_megaparse/) (Quivr) | Local/API | Simplest API, vision mode with GPT-4o/Claude | Apache 2.0 |

## Getting Started

```bash
# Install dependencies
uv sync

# Install optional OCR dependencies
uv sync --extra ocr

# Install optional video dependencies (Whisper + OpenCV)
uv sync --extra video

# Install advanced parsing libraries (pick what you need)
uv sync --extra docling        # IBM Docling
uv sync --extra unstructured   # Unstructured.io
uv sync --extra azure          # Azure Document Intelligence
uv sync --extra llamaparse     # LlamaParse
uv sync --extra marker         # Marker PDF-to-Markdown

# Generate all sample documents
for f in unstructured_documents/*/sample_docs/generate_samples.py; do
  uv run python "$f"
done

# Run any extraction script
uv run python unstructured_documents/01_pdf/01_pypdf_extraction.py
```

## Focus

This repo focuses on **document parsing and extraction strategies** — how to get text out of various file formats and prepare it for RAG. It does not implement RAG pipelines, vector databases, or embedding models. The goal is to be the only guide you need for the "parse and chunk" phase of any RAG system.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
