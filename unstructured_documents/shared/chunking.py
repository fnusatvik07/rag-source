"""
Shared chunking utilities for RAG document parsing.

These strategies turn extracted text into chunks suitable for embedding and retrieval.
Every extraction script in this repo can use these to demonstrate RAG-ready output.
"""

import re


def chunk_by_characters(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Fixed-size character chunking with overlap.

    Simplest strategy - splits text into fixed-size windows.
    Good for: uniform-length chunks, predictable token counts.
    Bad for: splits mid-sentence, loses semantic boundaries.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def chunk_by_sentences(text: str, sentences_per_chunk: int = 5, overlap_sentences: int = 1) -> list[str]:
    """
    Sentence-based chunking.

    Splits on sentence boundaries, groups N sentences per chunk.
    Good for: preserves complete sentences, more semantic than character-based.
    Bad for: sentence detection can fail on abbreviations, variable chunk sizes.
    """
    sentence_pattern = r"(?<=[.!?])\s+"
    sentences = re.split(sentence_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk - overlap_sentences):
        chunk_sentences = sentences[i : i + sentences_per_chunk]
        if chunk_sentences:
            chunks.append(" ".join(chunk_sentences))
    return chunks


def chunk_by_recursive_split(
    text: str,
    chunk_size: int = 500,
    separators: list[str] | None = None,
) -> list[str]:
    """
    Recursive character splitting (similar to LangChain's RecursiveCharacterTextSplitter).

    Tries to split on the most meaningful separator first (paragraphs > newlines > sentences > characters).
    Good for: respects document structure, balanced chunks.
    Bad for: more complex, may still split awkwardly on edge cases.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    for sep in separators:
        if sep == "":
            # Base case: hard split by characters
            return chunk_by_characters(text, chunk_size, overlap=0)

        parts = text.split(sep)
        if len(parts) == 1:
            continue

        # Merge parts into chunks that fit within chunk_size
        chunks = []
        current = ""
        for part in parts:
            candidate = current + sep + part if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                current = part
        if current:
            chunks.append(current.strip())

        return [c for c in chunks if c]

    return [text.strip()] if text.strip() else []


def chunk_by_headings(text: str, heading_pattern: str = r"^#+\s+.*$") -> list[dict]:
    """
    Heading-aware chunking for structured documents.

    Splits on headings (markdown-style by default), preserving heading as metadata.
    Good for: documents with clear structure (markdown, converted HTML, DOCX with headings).
    Bad for: documents without headings, inconsistent heading levels.

    Returns list of dicts with 'heading' and 'content' keys.
    """
    lines = text.split("\n")
    chunks = []
    current_heading = "Introduction"
    current_lines = []

    for line in lines:
        if re.match(heading_pattern, line):
            # Save previous chunk
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    chunks.append({"heading": current_heading, "content": content})
            current_heading = line.strip().lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last chunk
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            chunks.append({"heading": current_heading, "content": content})

    return chunks


def preview_chunks(chunks: list, max_preview: int = 3, max_chars: int = 200) -> None:
    """Print a preview of chunks for demonstration purposes."""
    print(f"\n{'=' * 60}")
    print(f"Total chunks: {len(chunks)}")
    print(f"{'=' * 60}")

    for i, chunk in enumerate(chunks[:max_preview]):
        if isinstance(chunk, dict):
            print(f"\n--- Chunk {i + 1} [heading: {chunk.get('heading', 'N/A')}] ---")
            text = chunk.get("content", "")
        else:
            print(f"\n--- Chunk {i + 1} ({len(chunk)} chars) ---")
            text = chunk

        if len(text) > max_chars:
            print(text[:max_chars] + "...")
        else:
            print(text)

    if len(chunks) > max_preview:
        print(f"\n... and {len(chunks) - max_preview} more chunks")


if __name__ == "__main__":
    sample_text = """# Introduction

    This is a sample document about machine learning. It covers several important topics
    that are relevant to modern AI systems.

    # Neural Networks

    Neural networks are computational systems inspired by biological neural networks.
    They consist of layers of interconnected nodes. Each connection has a weight that
    adjusts during training. Deep learning uses neural networks with many layers.

    # Training Process

    Training involves feeding data through the network and adjusting weights.
    The loss function measures how far predictions are from actual values.
    Backpropagation computes gradients for weight updates. Optimizers like Adam
    and SGD use these gradients to update weights efficiently.

    # Applications

    Machine learning is used in image recognition, natural language processing,
    recommendation systems, and autonomous vehicles. Each application requires
    different architectures and training approaches.
    """

    print("=== Character Chunking ===")
    chunks = chunk_by_characters(sample_text, chunk_size=200, overlap=30)
    preview_chunks(chunks)

    print("\n\n=== Sentence Chunking ===")
    chunks = chunk_by_sentences(sample_text, sentences_per_chunk=3)
    preview_chunks(chunks)

    print("\n\n=== Recursive Split ===")
    chunks = chunk_by_recursive_split(sample_text, chunk_size=200)
    preview_chunks(chunks)

    print("\n\n=== Heading-Aware Chunking ===")
    chunks = chunk_by_headings(sample_text)
    preview_chunks(chunks)
