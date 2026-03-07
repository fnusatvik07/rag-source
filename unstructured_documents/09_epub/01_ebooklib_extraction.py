"""
EPUB Extraction Method 1: ebooklib

ebooklib is the standard Python library for reading and writing EPUB files.
Combined with BeautifulSoup for HTML parsing, it provides clean text extraction.

EPUB files are ZIP archives containing XHTML documents, CSS, images, and metadata.
ebooklib gives structured access to all of these components.

Best for: Chapter-by-chapter extraction, metadata access, structured ebook processing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

from unstructured_documents.shared.chunking import chunk_by_headings, preview_chunks

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def extract_metadata(book: epub.EpubBook) -> dict:
    """
    Extract all available metadata from an EPUB.

    EPUB metadata follows the Dublin Core standard and can include:
    title, author, language, identifier, publisher, date, description, etc.
    """
    metadata = {
        "title": book.get_metadata("DC", "title"),
        "creator": book.get_metadata("DC", "creator"),
        "language": book.get_metadata("DC", "language"),
        "identifier": book.get_metadata("DC", "identifier"),
        "description": book.get_metadata("DC", "description"),
        "publisher": book.get_metadata("DC", "publisher"),
    }

    # Flatten metadata tuples: each entry is (value, attributes_dict)
    cleaned = {}
    for key, values in metadata.items():
        if values:
            cleaned[key] = [v[0] for v in values]
        else:
            cleaned[key] = []

    return cleaned


def list_items(book: epub.EpubBook) -> list[dict]:
    """
    List all document items in the EPUB.

    An EPUB can contain many types of items: XHTML documents, images,
    stylesheets, fonts, etc. We focus on ITEM_DOCUMENT (the text content).
    """
    items = []
    for item in book.get_items():
        items.append(
            {
                "id": item.get_id(),
                "name": item.get_name(),
                "type": item.get_type(),
                "is_document": item.get_type() == ITEM_DOCUMENT,
            }
        )
    return items


def extract_chapter_text(item: epub.EpubHtml) -> dict:
    """
    Extract clean text from a single EPUB chapter/document.

    EPUB chapters are XHTML files. We use BeautifulSoup to parse the HTML
    and extract readable text, headings, paragraphs, lists, and tables.
    """
    soup = BeautifulSoup(item.get_content(), "html.parser")

    # Extract the chapter title from <h1> or <title>
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    elif soup.find("title"):
        title = soup.find("title").get_text(strip=True)

    # Extract paragraphs
    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)

    # Extract lists
    lists = []
    for ul in soup.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            lists.append(items)

    # Extract tables
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)

    # Full clean text
    full_text = soup.get_text(separator="\n", strip=True)

    return {
        "title": title,
        "file_name": item.get_name(),
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": tables,
        "full_text": full_text,
    }


def extract_all_chapters(book: epub.EpubBook) -> list[dict]:
    """
    Extract text from all document items (chapters) in the EPUB.

    Filters to only ITEM_DOCUMENT types and skips navigation documents.
    Returns one dict per chapter with structured content.
    """
    chapters = []
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        # Skip navigation/TOC files
        name = item.get_name().lower()
        if "nav" in name or "toc" in name:
            continue

        chapter_data = extract_chapter_text(item)
        # Only include chapters that have actual content
        if chapter_data["full_text"].strip():
            chapters.append(chapter_data)

    return chapters


def chapters_to_markdown(chapters: list[dict]) -> str:
    """
    Convert extracted chapters into a markdown-like format for heading-aware chunking.

    This produces text like:
      # Chapter Title
      Paragraph 1...
      Paragraph 2...
    """
    parts = []
    for chapter in chapters:
        title = chapter["title"] or "Untitled"
        parts.append(f"# {title}")
        parts.append("")  # blank line after heading

        for para in chapter["paragraphs"]:
            parts.append(para)
            parts.append("")  # blank line between paragraphs

        for lst in chapter["lists"]:
            for item in lst:
                parts.append(f"- {item}")
            parts.append("")

        for table in chapter["tables"]:
            for row in table:
                parts.append(" | ".join(row))
            parts.append("")

    return "\n".join(parts)


if __name__ == "__main__":
    epub_path = SAMPLE_DIR / "sample_book.epub"

    if not epub_path.exists():
        print("Sample EPUB not found. Generating it first...")
        print("Run: uv run python unstructured_documents/09_epub/sample_docs/generate_samples.py")
        sys.exit(1)

    # Load the EPUB
    book = epub.read_epub(str(epub_path), options={"ignore_ncx": True})

    # --- 1. Metadata extraction ---
    print("=" * 60)
    print("1. EPUB METADATA")
    print("=" * 60)
    meta = extract_metadata(book)
    for key, values in meta.items():
        if values:
            print(f"  {key}: {', '.join(str(v) for v in values)}")

    # --- 2. List all items ---
    print(f"\n{'=' * 60}")
    print("2. EPUB ITEMS (all files in the archive)")
    print("=" * 60)
    items = list_items(book)
    for item in items:
        doc_marker = " [DOCUMENT]" if item["is_document"] else ""
        print(f"  {item['name']} (type: {item['type']}){doc_marker}")

    # --- 3. Chapter-by-chapter extraction ---
    print(f"\n{'=' * 60}")
    print("3. CHAPTER-BY-CHAPTER EXTRACTION")
    print("=" * 60)
    chapters = extract_all_chapters(book)
    print(f"\nExtracted {len(chapters)} chapters:\n")

    for i, ch in enumerate(chapters, 1):
        print(f"  Chapter {i}: {ch['title']}")
        print(f"    File: {ch['file_name']}")
        print(f"    Paragraphs: {len(ch['paragraphs'])}")
        print(f"    Lists: {len(ch['lists'])}")
        print(f"    Tables: {len(ch['tables'])}")
        print(f"    Text length: {len(ch['full_text'])} chars")
        print(f"    Preview: {ch['full_text'][:100]}...")
        print()

    # --- 4. One chunk per chapter ---
    print(f"{'=' * 60}")
    print("4. CHAPTER-PER-CHUNK (simplest chunking for ebooks)")
    print("=" * 60)
    for i, ch in enumerate(chapters, 1):
        print(f"\n--- Chunk {i} [chapter: {ch['title']}] ({len(ch['full_text'])} chars) ---")
        print(ch["full_text"][:200] + "...")

    # --- 5. Heading-aware chunking ---
    print(f"\n{'=' * 60}")
    print("5. HEADING-AWARE CHUNKING (markdown conversion)")
    print("=" * 60)
    md_text = chapters_to_markdown(chapters)
    chunks = chunk_by_headings(md_text)
    preview_chunks(chunks)
