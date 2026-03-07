"""
HTML Extraction Method 1: BeautifulSoup

BeautifulSoup is the most popular HTML parsing library in Python.
It creates a parse tree from HTML that can be navigated, searched, and modified.

Best for: Fine-grained control over which elements to extract, handling messy HTML.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup

from unstructured_documents.shared.chunking import chunk_by_headings, preview_chunks

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


def extract_text_basic(html_path: Path) -> str:
    """Extract all visible text from HTML, stripping tags."""
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    return soup.get_text(separator="\n", strip=True)


def extract_article_content(html_path: Path) -> dict:
    """
    Extract structured content from an article page.
    Targets the <article> or <main> tag, skipping nav/sidebar/footer boilerplate.
    This is the most common RAG-friendly approach for web content.
    """
    soup = BeautifulSoup(html_path.read_text(), "html.parser")

    # Remove boilerplate elements
    for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()

    # Try to find the main content container
    content = soup.find("article") or soup.find("main") or soup.find("body")

    result = {
        "title": "",
        "meta": {},
        "headings": [],
        "paragraphs": [],
        "lists": [],
        "tables": [],
        "full_text": "",
    }

    # Extract title
    title_tag = soup.find("title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    # Extract meta tags
    for meta in soup.find_all("meta"):
        name = meta.get("name", "")
        if name and meta.get("content"):
            result["meta"][name] = meta["content"]

    # Extract headings
    for heading in content.find_all(["h1", "h2", "h3", "h4"]):
        result["headings"].append(
            {
                "level": heading.name,
                "text": heading.get_text(strip=True),
            }
        )

    # Extract paragraphs
    for p in content.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            result["paragraphs"].append(text)

    # Extract lists
    for ul in content.find_all(["ul", "ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            result["lists"].append(items)

    # Extract tables
    for table in content.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            result["tables"].append(rows)

    # Full text for chunking
    result["full_text"] = content.get_text(separator="\n", strip=True)

    return result


def extract_tables_only(html_path: Path) -> list[list[list[str]]]:
    """Extract all tables from HTML as lists of rows."""
    soup = BeautifulSoup(html_path.read_text(), "html.parser")
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        tables.append(rows)
    return tables


def html_to_markdown_like(html_path: Path) -> str:
    """
    Convert HTML to a markdown-like format for heading-aware chunking.
    This manual approach gives control over the conversion.
    """
    soup = BeautifulSoup(html_path.read_text(), "html.parser")

    # Remove boilerplate
    for tag in soup.find_all(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()

    content = soup.find("article") or soup.find("main") or soup.find("body")
    lines = []

    for element in content.descendants:
        if element.name in ["h1", "h2", "h3", "h4"]:
            level = int(element.name[1])
            lines.append(f"\n{'#' * level} {element.get_text(strip=True)}\n")
        elif element.name == "p" and element.string != element.parent.string:
            text = element.get_text(strip=True)
            if text:
                lines.append(text)
        elif element.name == "li":
            lines.append(f"- {element.get_text(strip=True)}")
        elif element.name == "blockquote":
            lines.append(f"> {element.get_text(strip=True)}")

    return "\n".join(lines)


if __name__ == "__main__":
    article_path = SAMPLE_DIR / "article_page.html"
    table_path = SAMPLE_DIR / "table_heavy_page.html"

    # --- Basic text extraction ---
    print("=" * 60)
    print("1. BASIC TEXT EXTRACTION (article_page.html)")
    print("=" * 60)
    raw_text = extract_text_basic(article_path)
    print(f"Extracted {len(raw_text)} characters")
    print(f"First 300 chars:\n{raw_text[:300]}")

    # --- Structured article extraction ---
    print(f"\n{'=' * 60}")
    print("2. STRUCTURED ARTICLE EXTRACTION")
    print("=" * 60)
    article = extract_article_content(article_path)
    print(f"Title: {article['title']}")
    print(f"Meta: {article['meta']}")
    print(f"Headings: {[h['text'] for h in article['headings']]}")
    print(f"Paragraphs: {len(article['paragraphs'])}")
    print(f"Lists: {len(article['lists'])}")
    print(f"Tables: {len(article['tables'])}")

    # --- Table extraction ---
    print(f"\n{'=' * 60}")
    print("3. TABLE EXTRACTION (table_heavy_page.html)")
    print("=" * 60)
    tables = extract_tables_only(table_path)
    for i, table in enumerate(tables):
        print(f"\nTable {i + 1} ({len(table)} rows):")
        for row in table[:3]:
            print(f"  {row}")
        if len(table) > 3:
            print(f"  ... and {len(table) - 3} more rows")

    # --- Markdown conversion + heading-aware chunking ---
    print(f"\n{'=' * 60}")
    print("4. MARKDOWN CONVERSION + HEADING-AWARE CHUNKING")
    print("=" * 60)
    md_text = html_to_markdown_like(article_path)
    chunks = chunk_by_headings(md_text)
    preview_chunks(chunks)
