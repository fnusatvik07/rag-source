# Unstructured Document Parsing for RAG

The definitive guide to extracting text from unstructured documents for Retrieval-Augmented Generation (RAG) systems. Every major document type is covered with multiple parsing methods, working code examples, and generated sample documents.

## Quick Start

```bash
# Install dependencies
uv sync

# Generate all sample documents
uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py
uv run python unstructured_documents/02_docx/sample_docs/generate_samples.py
uv run python unstructured_documents/03_pptx/sample_docs/generate_samples.py
uv run python unstructured_documents/04_html/sample_docs/generate_samples.py
uv run python unstructured_documents/05_spreadsheets/sample_docs/generate_samples.py
uv run python unstructured_documents/06_images_ocr/sample_docs/generate_samples.py
uv run python unstructured_documents/07_email/sample_docs/generate_samples.py
uv run python unstructured_documents/08_markdown_txt/sample_docs/generate_samples.py
uv run python unstructured_documents/09_epub/sample_docs/generate_samples.py
uv run python unstructured_documents/10_video/sample_docs/generate_samples.py

# Run any extraction script
uv run python unstructured_documents/01_pdf/01_pypdf_extraction.py
```

## Document Types Covered

| # | Type | Folder | Methods | Scripts | Key Libraries |
|---|------|--------|---------|---------|---------------|
| 1 | **PDF** | [01_pdf](01_pdf/) | 6 | 6 | pypdf, pdfplumber, PyMuPDF, pytesseract |
| 2 | **Word (DOCX)** | [02_docx](02_docx/) | 3 | 3 | python-docx, mammoth, docx2txt |
| 3 | **PowerPoint (PPTX)** | [03_pptx](03_pptx/) | 2 | 2 | python-pptx |
| 4 | **HTML / Web** | [04_html](04_html/) | 3 | 3 | BeautifulSoup, html2text, trafilatura |
| 5 | **Spreadsheets (XLSX/CSV)** | [05_spreadsheets](05_spreadsheets/) | 3 | 3 | openpyxl, pandas, csv (stdlib) |
| 6 | **Images (OCR)** | [06_images_ocr](06_images_ocr/) | 2 | 2 | pytesseract, EasyOCR |
| 7 | **Email (EML)** | [07_email](07_email/) | 2 | 2 | email (stdlib) |
| 8 | **Markdown / Text** | [08_markdown_txt](08_markdown_txt/) | 3 | 3 | mistune, csv (stdlib) |
| 9 | **EPUB (Ebooks)** | [09_epub](09_epub/) | 2 | 2 | ebooklib, BeautifulSoup |
| 10 | **Video** | [10_video](10_video/) | 2 | 2 | openai-whisper, OpenCV |

## Decision Matrix: Which Parser for Which Situation?

### "I have a PDF..."
| Situation | Recommended Method | Why |
|-----------|-------------------|-----|
| Simple text extraction | **pypdf** or **PyMuPDF** | Fast, lightweight, good for text-heavy PDFs |
| Tables in the PDF | **pdfplumber** | Best table detection and extraction |
| Scanned PDF (images) | **pytesseract + pdf2image** | OCR is the only option for image-based PDFs |
| Need speed at scale | **PyMuPDF** | Fastest library, C-based engine |
| Complex layouts | **pdfplumber** (layout mode) | Preserves spatial positioning |

### "I have a Word document..."
| Situation | Recommended Method | Why |
|-----------|-------------------|-----|
| Need heading structure | **python-docx** | Direct access to styles and heading levels |
| Quick text dump | **docx2txt** | One-line extraction, no frills |
| Want markdown output | **mammoth** | Native markdown conversion |

### "I have a web page..."
| Situation | Recommended Method | Why |
|-----------|-------------------|-----|
| Article/blog extraction | **trafilatura** | Automatic boilerplate removal |
| Fine-grained control | **BeautifulSoup** | DOM traversal, custom selectors |
| Quick markdown conversion | **html2text** | Fast, heading-aware output |

### "I have tabular data..."
| Situation | Recommended Method | Why |
|-----------|-------------------|-----|
| Need data analysis too | **pandas** | DataFrames, stats, filtering |
| Cell-level control | **openpyxl** | Formatting, merged cells, formulas |
| Simple CSV, no deps | **csv (stdlib)** | Zero dependencies, streaming |

### "I have other formats..."
| Format | Go-to Method |
|--------|-------------|
| PowerPoint | python-pptx (slide-by-slide extraction) |
| Images/Scans | pytesseract or EasyOCR |
| Email (.eml) | Python email module (stdlib) |
| Markdown | mistune AST parsing + heading-aware chunking |
| Plain text | Recursive character splitting |
| EPUB | ebooklib + BeautifulSoup |
| Video | Whisper transcription + OpenCV frame extraction |

## Shared Utilities

The [shared/chunking.py](shared/chunking.py) module provides 4 chunking strategies used across all extraction scripts:

| Strategy | Best For | Description |
|----------|----------|-------------|
| **Character chunking** | Uniform chunk sizes | Fixed-size windows with overlap |
| **Sentence chunking** | Preserving sentences | Groups N sentences per chunk |
| **Recursive splitting** | General purpose | Splits on paragraphs > newlines > sentences > characters |
| **Heading-aware chunking** | Structured documents | Splits on headings, preserves document hierarchy |

## The RAG Document Parsing Pipeline

Regardless of document type, the extraction pipeline for RAG follows the same pattern:

```
Source Document → Parse/Extract → Clean → Chunk → Embed → Store
     ↓                ↓            ↓        ↓        ↓       ↓
  PDF/DOCX/...    Raw text    Remove     Split    Vector   Vector
                  + tables    noise     into     embed    DB
                  + metadata  + format  chunks   each     (Pinecone,
                              normalize          chunk    Chroma, etc.)
```

**This repo focuses on steps 1-4**: parsing, extracting, cleaning, and chunking. The embedding and storage steps depend on your chosen vector database and embedding model.

## Key Principles for RAG Document Parsing

1. **Structure preservation matters** - Headings, sections, and tables carry semantic meaning. Preserve them for better retrieval.
2. **Tables need special handling** - Convert tables to natural language or structured text, not raw cell dumps.
3. **Metadata is valuable** - Document title, author, date, section headings make excellent filters for retrieval.
4. **Chunk size depends on your embedding model** - Most models work best with 200-500 token chunks. Measure, don't guess.
5. **Overlap prevents information loss** - 10-20% overlap between chunks ensures important context isn't split.
6. **Test with real queries** - The best parsing strategy depends on how users will search, not just the document structure.

## Repository Structure

```
unstructured_documents/
├── README.md                          ← You are here
├── shared/
│   └── chunking.py                    # 4 chunking strategies used by all scripts
│
├── 01_pdf/                            # PDF parsing (6 methods)
├── 02_docx/                           # Word document parsing (3 methods)
├── 03_pptx/                           # PowerPoint parsing (2 methods)
├── 04_html/                           # HTML/web parsing (3 methods)
├── 05_spreadsheets/                   # XLSX/CSV parsing (3 methods)
├── 06_images_ocr/                     # OCR for images (2 methods)
├── 07_email/                          # Email parsing (2 methods)
├── 08_markdown_txt/                   # Markdown/text parsing (3 methods)
├── 09_epub/                           # EPUB ebook parsing (2 methods)
└── 10_video/                          # Video parsing (2 methods)

Each folder contains:
├── README.md                          # Comprehensive guide for that document type
├── sample_docs/
│   └── generate_samples.py            # Generate test documents
├── 01_method_extraction.py            # Extraction scripts (numbered)
├── 02_method_extraction.py
└── ...
```
