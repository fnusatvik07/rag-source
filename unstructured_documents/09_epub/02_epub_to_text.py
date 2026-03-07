"""
EPUB Extraction Method 2: Full Text Extraction with Structure

Demonstrates a complete pipeline for converting an EPUB ebook into
RAG-ready text chunks. Covers:
  - Full book text extraction maintaining chapter order
  - Table of contents generation from chapter headings
  - Markdown-like format conversion
  - Multiple chunking strategies: chapter-per-chunk vs. recursive split
  - Preparing an entire ebook for RAG ingestion

Best for: Bulk ebook processing, RAG pipeline integration, full-text search indexing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

from unstructured_documents.shared.chunking import (
    chunk_by_headings,
    chunk_by_recursive_split,
    chunk_by_sentences,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def load_epub(epub_path: Path) -> epub.EpubBook:
    """Load an EPUB file and return the book object."""
    return epub.read_epub(str(epub_path), options={"ignore_ncx": True})


def get_chapter_items(book: epub.EpubBook) -> list[epub.EpubHtml]:
    """
    Get document items in reading order, skipping navigation files.

    The spine defines reading order in an EPUB. We follow it to maintain
    the correct chapter sequence.
    """
    # Get spine order (list of (item_id, properties) tuples)
    spine_ids = [item_id for item_id, _ in book.spine]

    # Build a map of id -> item for document items
    item_map = {}
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        item_map[item.get_id()] = item

    # Return items in spine order, skipping nav/toc
    ordered = []
    for item_id in spine_ids:
        if item_id in item_map:
            item = item_map[item_id]
            name = item.get_name().lower()
            if "nav" not in name and "toc" not in name:
                ordered.append(item)

    return ordered


def extract_chapter_heading(item: epub.EpubHtml) -> str:
    """Extract the main heading from a chapter's HTML content."""
    soup = BeautifulSoup(item.get_content(), "html.parser")
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    h2 = soup.find("h2")
    if h2:
        return h2.get_text(strip=True)
    title = soup.find("title")
    if title:
        return title.get_text(strip=True)
    return "Untitled"


def extract_clean_text(item: epub.EpubHtml) -> str:
    """Extract clean text from a chapter, preserving paragraph breaks."""
    soup = BeautifulSoup(item.get_content(), "html.parser")

    # Remove script and style elements
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    # Extract text with newline separators
    return soup.get_text(separator="\n", strip=True)


def build_table_of_contents(chapters: list[epub.EpubHtml]) -> list[dict]:
    """
    Build a table of contents from chapter headings.

    Returns a list of dicts with chapter number, title, and file name.
    Useful for providing context about document structure in RAG metadata.
    """
    toc = []
    for i, item in enumerate(chapters, 1):
        heading = extract_chapter_heading(item)
        toc.append(
            {
                "chapter_num": i,
                "title": heading,
                "file": item.get_name(),
            }
        )
    return toc


def epub_to_markdown(book: epub.EpubBook) -> str:
    """
    Convert an entire EPUB to markdown-like format.

    Output format:
      # Chapter Title

      Paragraph text...

      - List item 1
      - List item 2

    This format works well with heading-aware chunking.
    """
    chapters = get_chapter_items(book)
    parts = []

    for item in chapters:
        soup = BeautifulSoup(item.get_content(), "html.parser")

        # Remove scripts and styles
        for tag in soup.find_all(["script", "style"]):
            tag.decompose()

        body = soup.find("body") or soup

        for element in body.children:
            if not hasattr(element, "name") or element.name is None:
                # Text node
                text = element.strip()
                if text:
                    parts.append(text)
                continue

            if element.name == "h1":
                parts.append(f"\n# {element.get_text(strip=True)}\n")
            elif element.name == "h2":
                parts.append(f"\n## {element.get_text(strip=True)}\n")
            elif element.name == "h3":
                parts.append(f"\n### {element.get_text(strip=True)}\n")
            elif element.name == "p":
                text = element.get_text(strip=True)
                if text:
                    parts.append(text + "\n")
            elif element.name in ("ul", "ol"):
                for li in element.find_all("li"):
                    parts.append(f"- {li.get_text(strip=True)}")
                parts.append("")
            elif element.name == "table":
                rows = element.find_all("tr")
                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    parts.append("| " + " | ".join(cells) + " |")
                parts.append("")

    return "\n".join(parts)


def epub_to_full_text(book: epub.EpubBook) -> str:
    """
    Extract the complete book text as a single string.
    Chapters are separated by double newlines with a chapter marker.
    """
    chapters = get_chapter_items(book)
    sections = []

    for item in chapters:
        heading = extract_chapter_heading(item)
        text = extract_clean_text(item)
        sections.append(f"[Chapter: {heading}]\n\n{text}")

    return "\n\n---\n\n".join(sections)


def prepare_for_rag(book: epub.EpubBook, strategy: str = "chapter") -> list[dict]:
    """
    Prepare an entire ebook for RAG ingestion.

    Returns a list of chunk dicts with text and metadata, ready for
    embedding and storage in a vector database.

    Strategies:
      - "chapter":   One chunk per chapter (simple, preserves structure)
      - "recursive":  Recursive split for uniform chunk sizes
      - "heading":    Split on headings (best for structured ebooks)
    """
    chapters = get_chapter_items(book)
    toc = build_table_of_contents(chapters)

    # Extract metadata once
    title_meta = book.get_metadata("DC", "title")
    author_meta = book.get_metadata("DC", "creator")
    book_title = title_meta[0][0] if title_meta else "Unknown"
    book_author = author_meta[0][0] if author_meta else "Unknown"

    rag_chunks = []

    if strategy == "chapter":
        # One chunk per chapter
        for i, item in enumerate(chapters):
            text = extract_clean_text(item)
            rag_chunks.append(
                {
                    "text": text,
                    "metadata": {
                        "source": "epub",
                        "book_title": book_title,
                        "author": book_author,
                        "chapter": toc[i]["title"],
                        "chapter_num": toc[i]["chapter_num"],
                        "chunk_strategy": "chapter",
                    },
                }
            )

    elif strategy == "recursive":
        # Recursive split across entire book for uniform chunk sizes
        full_text = epub_to_full_text(book)
        text_chunks = chunk_by_recursive_split(full_text, chunk_size=500)
        for j, chunk_text in enumerate(text_chunks):
            rag_chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source": "epub",
                        "book_title": book_title,
                        "author": book_author,
                        "chunk_index": j,
                        "chunk_strategy": "recursive_split",
                    },
                }
            )

    elif strategy == "heading":
        # Heading-aware chunking using markdown conversion
        md_text = epub_to_markdown(book)
        heading_chunks = chunk_by_headings(md_text)
        for chunk in heading_chunks:
            rag_chunks.append(
                {
                    "text": chunk["content"],
                    "metadata": {
                        "source": "epub",
                        "book_title": book_title,
                        "author": book_author,
                        "section_heading": chunk["heading"],
                        "chunk_strategy": "heading_aware",
                    },
                }
            )

    return rag_chunks


if __name__ == "__main__":
    epub_path = SAMPLE_DIR / "sample_book.epub"

    if not epub_path.exists():
        print("Sample EPUB not found. Generating it first...")
        print("Run: uv run python unstructured_documents/09_epub/sample_docs/generate_samples.py")
        sys.exit(1)

    book = load_epub(epub_path)

    # --- 1. Table of Contents ---
    print("=" * 60)
    print("1. TABLE OF CONTENTS")
    print("=" * 60)
    chapters = get_chapter_items(book)
    toc = build_table_of_contents(chapters)
    for entry in toc:
        print(f"  Chapter {entry['chapter_num']}: {entry['title']} ({entry['file']})")

    # --- 2. Full text extraction ---
    print(f"\n{'=' * 60}")
    print("2. FULL TEXT EXTRACTION")
    print("=" * 60)
    full_text = epub_to_full_text(book)
    print(f"Total text length: {len(full_text)} characters")
    print("\nFirst 500 chars:")
    print(full_text[:500])
    print("...")

    # --- 3. Markdown conversion ---
    print(f"\n{'=' * 60}")
    print("3. MARKDOWN-LIKE CONVERSION")
    print("=" * 60)
    md_text = epub_to_markdown(book)
    print(f"Markdown length: {len(md_text)} characters")
    print("\nFirst 500 chars:")
    print(md_text[:500])
    print("...")

    # --- 4. Chunking Strategy Comparison ---
    print(f"\n{'=' * 60}")
    print("4. CHUNKING STRATEGY COMPARISON")
    print("=" * 60)

    # Strategy A: Chapter-per-chunk
    print("\n--- Strategy A: Chapter-Per-Chunk ---")
    chapter_chunks = prepare_for_rag(book, strategy="chapter")
    print(f"Chunks: {len(chapter_chunks)}")
    for chunk in chapter_chunks:
        meta = chunk["metadata"]
        print(f"  [{meta['chapter_num']}] {meta['chapter']} ({len(chunk['text'])} chars)")

    # Strategy B: Recursive split
    print("\n--- Strategy B: Recursive Split (500 chars) ---")
    recursive_chunks = prepare_for_rag(book, strategy="recursive")
    print(f"Chunks: {len(recursive_chunks)}")
    for chunk in recursive_chunks[:5]:
        print(f"  Chunk {chunk['metadata']['chunk_index']}: {len(chunk['text'])} chars - {chunk['text'][:80]}...")
    if len(recursive_chunks) > 5:
        print(f"  ... and {len(recursive_chunks) - 5} more chunks")

    # Strategy C: Heading-aware
    print("\n--- Strategy C: Heading-Aware ---")
    heading_chunks = prepare_for_rag(book, strategy="heading")
    print(f"Chunks: {len(heading_chunks)}")
    for chunk in heading_chunks:
        meta = chunk["metadata"]
        print(f"  [{meta['section_heading']}] {len(chunk['text'])} chars")

    # --- 5. Sentence-based chunking for comparison ---
    print(f"\n{'=' * 60}")
    print("5. SENTENCE-BASED CHUNKING (alternative)")
    print("=" * 60)
    sentence_chunks = chunk_by_sentences(full_text, sentences_per_chunk=5, overlap_sentences=1)
    preview_chunks(sentence_chunks)

    # --- 6. RAG-ready output sample ---
    print(f"\n{'=' * 60}")
    print("6. RAG-READY OUTPUT SAMPLE (heading-aware)")
    print("=" * 60)
    print("\nEach chunk includes text + metadata for vector DB storage:\n")
    if heading_chunks:
        sample = heading_chunks[0]
        print(f'  text: "{sample["text"][:150]}..."')
        print("  metadata:")
        for key, value in sample["metadata"].items():
            print(f"    {key}: {value}")
