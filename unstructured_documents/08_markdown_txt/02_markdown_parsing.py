"""
Markdown Parsing with mistune

Uses the mistune library to parse Markdown into an AST (Abstract Syntax Tree),
then extracts structured components: headings, paragraphs, code blocks, lists,
and tables. Demonstrates heading-aware chunking where each section becomes a
separate chunk -- the recommended approach for markdown documents in RAG.

Best for: Structured markdown documents, technical docs, research papers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import mistune

from unstructured_documents.shared.chunking import (
    chunk_by_headings,
    chunk_by_recursive_split,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


# ---------------------------------------------------------------------------
# AST-based extraction helpers
# ---------------------------------------------------------------------------


def parse_markdown_ast(md_text: str) -> list[dict]:
    """Parse markdown text into a mistune AST (list of token dicts)."""
    markdown_parser = mistune.create_markdown(renderer=None)
    tokens = markdown_parser(md_text)
    return tokens


def extract_headings(tokens: list, depth: int = 0) -> list[dict]:
    """
    Recursively extract all headings from the AST.

    Returns a list of dicts: {"level": int, "text": str}
    """
    headings = []
    for token in tokens:
        if isinstance(token, dict):
            if token.get("type") == "heading":
                # Extract text from children
                text = _collect_text(token.get("children", []))
                headings.append({"level": token.get("attrs", {}).get("level", 1), "text": text})
            # Recurse into children
            for key in ("children", "body"):
                if key in token and isinstance(token[key], list):
                    headings.extend(extract_headings(token[key], depth + 1))
    return headings


def extract_paragraphs(tokens: list) -> list[str]:
    """Extract all paragraph text from the AST."""
    paragraphs = []
    for token in tokens:
        if isinstance(token, dict):
            if token.get("type") == "paragraph":
                text = _collect_text(token.get("children", []))
                if text.strip():
                    paragraphs.append(text.strip())
            for key in ("children", "body"):
                if key in token and isinstance(token[key], list):
                    paragraphs.extend(extract_paragraphs(token[key]))
    return paragraphs


def extract_code_blocks(tokens: list) -> list[dict]:
    """
    Extract fenced code blocks from the AST.

    Returns list of dicts: {"language": str, "code": str}
    """
    blocks = []
    for token in tokens:
        if isinstance(token, dict):
            if token.get("type") == "code":
                attrs = token.get("attrs", {})
                blocks.append(
                    {
                        "language": attrs.get("info", "") or "",
                        "code": token.get("raw", "") or token.get("text", ""),
                    }
                )
            for key in ("children", "body"):
                if key in token and isinstance(token[key], list):
                    blocks.extend(extract_code_blocks(token[key]))
    return blocks


def extract_lists(tokens: list) -> list[dict]:
    """
    Extract lists from the AST.

    Returns list of dicts: {"ordered": bool, "items": list[str]}
    """
    lists = []
    for token in tokens:
        if isinstance(token, dict):
            if token.get("type") == "list":
                attrs = token.get("attrs", {})
                ordered = attrs.get("ordered", False)
                items = []
                for child in token.get("children", []):
                    if isinstance(child, dict) and child.get("type") == "list_item":
                        item_text = _collect_text(child.get("children", []))
                        if item_text.strip():
                            items.append(item_text.strip())
                lists.append({"ordered": ordered, "items": items})
            else:
                for key in ("children", "body"):
                    if key in token and isinstance(token[key], list):
                        lists.extend(extract_lists(token[key]))
    return lists


def extract_tables(tokens: list) -> list[dict]:
    """
    Extract tables from the AST.

    Returns list of dicts: {"headers": list[str], "rows": list[list[str]]}
    """
    tables = []
    for token in tokens:
        if isinstance(token, dict):
            if token.get("type") == "table":
                headers = []
                rows = []
                for child in token.get("children", []):
                    if isinstance(child, dict):
                        if child.get("type") == "table_head":
                            for row_token in child.get("children", []):
                                if isinstance(row_token, dict) and row_token.get("type") == "table_row":
                                    for cell in row_token.get("children", []):
                                        if isinstance(cell, dict) and cell.get("type") == "table_cell":
                                            headers.append(_collect_text(cell.get("children", [])).strip())
                        elif child.get("type") == "table_body":
                            for row_token in child.get("children", []):
                                if isinstance(row_token, dict) and row_token.get("type") == "table_row":
                                    row_cells = []
                                    for cell in row_token.get("children", []):
                                        if isinstance(cell, dict) and cell.get("type") == "table_cell":
                                            row_cells.append(_collect_text(cell.get("children", [])).strip())
                                    rows.append(row_cells)
                tables.append({"headers": headers, "rows": rows})
            else:
                for key in ("children", "body"):
                    if key in token and isinstance(token[key], list):
                        tables.extend(extract_tables(token[key]))
    return tables


def _collect_text(tokens: list) -> str:
    """Recursively collect plain text from AST tokens."""
    parts = []
    for token in tokens:
        if isinstance(token, dict):
            if token.get("type") == "text":
                parts.append(token.get("raw", "") or token.get("text", ""))
            elif token.get("type") == "codespan":
                parts.append(token.get("raw", "") or token.get("text", ""))
            elif token.get("type") == "code":
                parts.append(token.get("raw", "") or token.get("text", ""))
            else:
                # Recurse into children
                for key in ("children", "body"):
                    if key in token and isinstance(token[key], list):
                        parts.append(_collect_text(token[key]))
        elif isinstance(token, str):
            parts.append(token)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Heading-aware chunking for markdown
# ---------------------------------------------------------------------------


def chunk_markdown_by_sections(md_text: str) -> list[dict]:
    """
    Split markdown into chunks where each section (heading + content until
    the next heading) is one chunk.

    Uses the shared heading-aware chunking utility.
    Returns list of dicts with 'heading' and 'content' keys.
    """
    return chunk_by_headings(md_text)


def extract_code_blocks_for_rag(md_text: str) -> list[dict]:
    """
    Extract code blocks as separate RAG-ready chunks.

    Each chunk includes the code and the heading of the section it belongs to.
    This is useful when users might search for specific code examples.
    """
    ast = parse_markdown_ast(md_text)
    code_blocks = extract_code_blocks(ast)

    # Approximate: match code blocks to the nearest preceding heading
    # by finding the heading positions in the raw text
    result = []
    lines = md_text.split("\n")
    heading_positions = []
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            heading_positions.append((i, line.strip().lstrip("#").strip()))

    for block in code_blocks:
        # Find which section this code belongs to
        code_text = block["code"]
        # Find approximate line number of this code in the source
        try:
            code_start = md_text.index(code_text)
            code_line = md_text[:code_start].count("\n")
        except ValueError:
            code_line = 0

        section = "Unknown"
        for pos, heading_text in heading_positions:
            if pos <= code_line:
                section = heading_text
            else:
                break

        result.append(
            {
                "section": section,
                "language": block["language"],
                "code": code_text,
                "rag_text": f"Code example from section '{section}' "
                f"(language: {block['language'] or 'unknown'}):\n\n{code_text}",
            }
        )

    return result


# ---------------------------------------------------------------------------
# Structured section extraction (for research papers)
# ---------------------------------------------------------------------------


def extract_research_sections(md_text: str) -> dict[str, str]:
    """
    Extract named sections from a research paper-style markdown document.

    Returns a dict mapping section names to their content.
    Useful for targeting specific parts of a paper (e.g., Abstract, Methodology).
    """
    chunks = chunk_by_headings(md_text)
    sections = {}
    for chunk in chunks:
        heading = chunk["heading"]
        content = chunk["content"]
        sections[heading] = content
    return sections


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # ===================================================================
    # Part 1: Parse technical_doc.md
    # ===================================================================
    tech_path = SAMPLE_DIR / "technical_doc.md"

    if not tech_path.exists():
        print("technical_doc.md not found. Run generate_samples.py first.")
        sys.exit(1)

    tech_md = tech_path.read_text()
    print("=" * 70)
    print("PART 1: PARSING technical_doc.md")
    print("=" * 70)
    print(f"File size: {len(tech_md)} chars\n")

    # --- Parse AST ---
    ast = parse_markdown_ast(tech_md)

    # --- Extract headings ---
    headings = extract_headings(ast)
    print("--- Headings ---")
    for h in headings:
        indent = "  " * (h["level"] - 1)
        print(f"  {indent}{'#' * h['level']} {h['text']}")

    # --- Extract paragraphs ---
    paragraphs = extract_paragraphs(ast)
    print(f"\n--- Paragraphs ({len(paragraphs)} total) ---")
    for i, p in enumerate(paragraphs[:3]):
        print(f"  [{i + 1}] {p[:100]}...")
    if len(paragraphs) > 3:
        print(f"  ... and {len(paragraphs) - 3} more")

    # --- Extract code blocks ---
    code_blocks = extract_code_blocks(ast)
    print(f"\n--- Code Blocks ({len(code_blocks)} total) ---")
    for i, cb in enumerate(code_blocks):
        preview = cb["code"][:80].replace("\n", "\\n")
        print(f"  [{i + 1}] lang={cb['language'] or 'none'}: {preview}...")

    # --- Extract lists ---
    lists = extract_lists(ast)
    print(f"\n--- Lists ({len(lists)} total) ---")
    for i, lst in enumerate(lists):
        kind = "ordered" if lst["ordered"] else "unordered"
        print(f"  [{i + 1}] {kind}, {len(lst['items'])} items: {lst['items'][0][:60]}...")

    # --- Extract tables ---
    tables = extract_tables(ast)
    print(f"\n--- Tables ({len(tables)} total) ---")
    for i, tbl in enumerate(tables):
        print(f"  [{i + 1}] {len(tbl['headers'])} columns, {len(tbl['rows'])} rows")
        print(f"       Headers: {tbl['headers']}")
        if tbl["rows"]:
            print(f"       First row: {tbl['rows'][0]}")

    # ===================================================================
    # Part 2: Heading-aware chunking
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("PART 2: HEADING-AWARE CHUNKING")
    print("=" * 70)
    print("Each section (heading + content) becomes one chunk.\n")

    section_chunks = chunk_markdown_by_sections(tech_md)
    preview_chunks(section_chunks, max_preview=4, max_chars=200)

    # ===================================================================
    # Part 3: Code block extraction for RAG
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("PART 3: CODE BLOCKS AS RAG CHUNKS")
    print("=" * 70)
    print("Each code block is extracted with section context.\n")

    code_rag_chunks = extract_code_blocks_for_rag(tech_md)
    for i, chunk in enumerate(code_rag_chunks):
        print(f"  [{i + 1}] Section: '{chunk['section']}', Language: {chunk['language'] or 'none'}")
        preview = chunk["code"][:100].replace("\n", "\\n")
        print(f"      Code: {preview}...")

    # ===================================================================
    # Part 4: Research paper section extraction
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("PART 4: RESEARCH PAPER SECTION EXTRACTION")
    print("=" * 70)

    paper_path = SAMPLE_DIR / "research_paper.md"
    if not paper_path.exists():
        print("research_paper.md not found. Run generate_samples.py first.")
        sys.exit(1)

    paper_md = paper_path.read_text()
    sections = extract_research_sections(paper_md)

    print(f"\nFound {len(sections)} sections:\n")
    for name, content in sections.items():
        print(f"  Section: '{name}' ({len(content)} chars)")
        print(f"    Preview: {content[:120]}...")
        print()

    # --- Chunk the abstract and methodology for fine-grained retrieval ---
    print("--- Fine-grained chunking of 'Abstract' section ---")
    if "Abstract" in sections:
        abstract_chunks = chunk_by_recursive_split(sections["Abstract"], chunk_size=300)
        preview_chunks(abstract_chunks, max_preview=3, max_chars=200)

    print("\n--- Fine-grained chunking of 'Methodology' section ---")
    if "Methodology" in sections:
        method_chunks = chunk_by_recursive_split(sections["Methodology"], chunk_size=400)
        preview_chunks(method_chunks, max_preview=3, max_chars=200)
