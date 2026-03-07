"""
Semantic Chunking Approaches

Demonstrates chunking strategies that attempt to preserve semantic meaning
within chunks. Unlike fixed-size or sentence-based splitting, semantic chunking
considers the meaning and topic coherence of the resulting chunks.

This script compares:
1. Sentence tokenization (basic splitting)
2. Sliding window chunking (overlapping sentence groups)
3. Paragraph-based semantic chunking (topic-aware)
4. Quality comparison across approaches

Best for: Understanding how different chunking strategies affect semantic
coherence, choosing the right approach for your RAG pipeline.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import (
    chunk_by_recursive_split,
    chunk_by_sentences,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


# ---------------------------------------------------------------------------
# Sentence tokenization
# ---------------------------------------------------------------------------


def tokenize_sentences(text: str) -> list[str]:
    """
    Split text into individual sentences.

    Uses regex to split on sentence-ending punctuation followed by whitespace.
    This is a simple approach; production systems may use spaCy or NLTK for
    better accuracy with abbreviations, decimal numbers, etc.
    """
    # Split on .!? followed by whitespace, but not inside common abbreviations
    pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# Sliding window chunking
# ---------------------------------------------------------------------------


def chunk_sliding_window(
    text: str,
    window_size: int = 5,
    stride: int = 2,
) -> list[str]:
    """
    Sliding window chunking with overlapping sentence groups.

    Creates chunks of `window_size` sentences, advancing by `stride` sentences
    each step. The overlap (window_size - stride) ensures that context near
    chunk boundaries is preserved in multiple chunks.

    This is one of the most effective simple strategies for RAG because:
    - It preserves sentence boundaries (no mid-sentence breaks)
    - Overlap ensures information at boundaries appears in multiple chunks
    - Consistent chunk sizes lead to predictable embedding behavior
    """
    sentences = tokenize_sentences(text)

    if len(sentences) <= window_size:
        return [" ".join(sentences)]

    chunks = []
    for i in range(0, len(sentences) - window_size + 1, stride):
        window = sentences[i : i + window_size]
        chunks.append(" ".join(window))

    # Ensure we capture the last sentences if they were not fully covered
    last_window = sentences[-window_size:]
    last_chunk = " ".join(last_window)
    if chunks and last_chunk != chunks[-1]:
        chunks.append(last_chunk)

    return chunks


# ---------------------------------------------------------------------------
# Paragraph-based semantic chunking
# ---------------------------------------------------------------------------


def chunk_by_topic_paragraphs(text: str, max_chunk_size: int = 800) -> list[str]:
    """
    Paragraph-based chunking that groups related paragraphs together.

    Strategy:
    1. Split on paragraph boundaries (double newlines)
    2. Group consecutive paragraphs that fit within max_chunk_size
    3. Never split a paragraph across chunks

    This preserves the author's natural topic boundaries while keeping
    chunks within a manageable size for embedding models.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # If adding this paragraph would exceed the limit, start a new chunk
        if current_chunk and len(current_chunk) + len(para) + 2 > max_chunk_size:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ---------------------------------------------------------------------------
# Semantic coherence analysis
# ---------------------------------------------------------------------------


def analyze_chunk_coherence(chunks: list[str]) -> list[dict]:
    """
    Analyze the semantic coherence of each chunk using simple heuristics.

    Checks for:
    - Sentence completeness (does the chunk start/end with complete sentences?)
    - Topic consistency (rough measure based on sentence similarity)
    - Chunk boundaries (does the chunk break in awkward places?)

    Note: In production, you would use sentence embeddings and cosine similarity
    for real semantic coherence measurement.
    """
    results = []
    for i, chunk in enumerate(chunks):
        sentences = tokenize_sentences(chunk)

        # Check if chunk starts with a capital letter (likely sentence start)
        starts_complete = chunk[0].isupper() if chunk else False

        # Check if chunk ends with sentence-ending punctuation
        ends_complete = chunk.rstrip()[-1] in ".!?" if chunk.rstrip() else False

        # Count unique "topic words" (non-stopword words with 4+ chars)
        words = re.findall(r"\b[a-zA-Z]{4,}\b", chunk.lower())
        unique_words = set(words)
        # Higher ratio = more diverse vocabulary = potentially less focused
        vocab_diversity = len(unique_words) / len(words) if words else 0

        results.append(
            {
                "chunk_index": i,
                "length": len(chunk),
                "sentence_count": len(sentences),
                "starts_complete": starts_complete,
                "ends_complete": ends_complete,
                "vocab_diversity": round(vocab_diversity, 3),
            }
        )

    return results


def print_coherence_report(label: str, chunks: list[str]):
    """Print a coherence analysis report for a set of chunks."""
    analysis = analyze_chunk_coherence(chunks)

    complete_starts = sum(1 for a in analysis if a["starts_complete"])
    complete_ends = sum(1 for a in analysis if a["ends_complete"])
    avg_diversity = sum(a["vocab_diversity"] for a in analysis) / len(analysis) if analysis else 0

    print(f"\n  {label}:")
    print(f"    Total chunks: {len(chunks)}")
    print(f"    Complete sentence starts: {complete_starts}/{len(chunks)} ({100 * complete_starts // len(chunks)}%)")
    print(f"    Complete sentence ends:   {complete_ends}/{len(chunks)} ({100 * complete_ends // len(chunks)}%)")
    print(f"    Avg vocab diversity:      {avg_diversity:.3f} (lower = more focused)")
    avg_len = sum(len(c) for c in chunks) // len(chunks) if chunks else 0
    print(f"    Avg chunk length:         {avg_len} chars")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    text_path = SAMPLE_DIR / "plain_text.txt"

    if not text_path.exists():
        print("plain_text.txt not found. Run generate_samples.py first.")
        sys.exit(1)

    text = text_path.read_text()
    print(f"Loaded: {text_path.name} ({len(text)} chars)\n")

    # ===================================================================
    # 1. Sentence tokenization
    # ===================================================================
    print("=" * 70)
    print("1. SENTENCE TOKENIZATION")
    print("=" * 70)
    print("Split text into individual sentences.\n")

    sentences = tokenize_sentences(text)
    print(f"  Total sentences: {len(sentences)}")
    print(f"  Avg sentence length: {sum(len(s) for s in sentences) // len(sentences)} chars")
    print("\n  First 5 sentences:")
    for i, sent in enumerate(sentences[:5]):
        print(f"    [{i + 1}] {sent[:100]}{'...' if len(sent) > 100 else ''}")

    # ===================================================================
    # 2. Sliding window chunking
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("2. SLIDING WINDOW CHUNKING")
    print("=" * 70)
    print("Overlapping windows of sentences.\n")

    # Compare different window sizes and strides
    configs = [
        (3, 1, "window=3, stride=1 (high overlap)"),
        (5, 2, "window=5, stride=2 (moderate overlap)"),
        (5, 4, "window=5, stride=4 (low overlap)"),
        (8, 3, "window=8, stride=3 (large window)"),
    ]

    for window, stride, label in configs:
        chunks = chunk_sliding_window(text, window_size=window, stride=stride)
        avg_len = sum(len(c) for c in chunks) // len(chunks) if chunks else 0
        print(f"  {label:45s} -> {len(chunks):>3} chunks, avg {avg_len:>4} chars")

    # Show a few chunks from the recommended config
    print("\n  Preview (window=5, stride=2):")
    recommended = chunk_sliding_window(text, window_size=5, stride=2)
    preview_chunks(recommended, max_preview=2, max_chars=200)

    # ===================================================================
    # 3. Paragraph-based semantic chunking
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("3. PARAGRAPH-BASED SEMANTIC CHUNKING")
    print("=" * 70)
    print("Groups paragraphs together up to a maximum size.\n")

    for max_size in (500, 800, 1200):
        chunks = chunk_by_topic_paragraphs(text, max_chunk_size=max_size)
        avg_len = sum(len(c) for c in chunks) // len(chunks) if chunks else 0
        print(f"  max_chunk_size={max_size:>5} -> {len(chunks):>3} chunks, avg {avg_len:>4} chars")

    print("\n  Preview (max_chunk_size=800):")
    para_chunks = chunk_by_topic_paragraphs(text, max_chunk_size=800)
    preview_chunks(para_chunks, max_preview=2, max_chars=200)

    # ===================================================================
    # 4. Quality comparison
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("4. SEMANTIC QUALITY COMPARISON")
    print("=" * 70)
    print("Analyzing chunk coherence across strategies.\n")

    all_strategies = {
        "Sentence-based (5/chunk)": chunk_by_sentences(text, 5, 1),
        "Sliding window (5, stride=2)": chunk_sliding_window(text, 5, 2),
        "Paragraph-based (800)": chunk_by_topic_paragraphs(text, 800),
        "Recursive split (500)": chunk_by_recursive_split(text, 500),
    }

    for label, chunks in all_strategies.items():
        print_coherence_report(label, chunks)

    # ===================================================================
    # 5. Demonstrating semantic meaning preservation
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("5. SEMANTIC MEANING PRESERVATION")
    print("=" * 70)
    print("Showing how different approaches handle a specific passage.\n")

    # Find a passage that spans a paragraph boundary
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paragraphs) >= 3:
        # Show the 3rd paragraph and check how each strategy handles it
        target_para = paragraphs[2]
        target_start = target_para[:50]
        print("  Target passage (paragraph 3, starts with):")
        print(f'    "{target_start}..."\n')

        for label, chunks in all_strategies.items():
            # Find which chunk(s) contain the start of this paragraph
            matching = [(i, c) for i, c in enumerate(chunks) if target_start in c]
            if matching:
                idx, chunk = matching[0]
                # Check if the full paragraph is in this chunk
                full_match = target_para in chunk
                print(f"  {label}:")
                print(
                    f"    Found in chunk {idx + 1}/{len(chunks)}, "
                    f"full paragraph preserved: {'Yes' if full_match else 'No'}"
                )
                print(f'    Chunk preview: "{chunk[:100]}..."')
            else:
                print(f"  {label}:")
                print("    Target paragraph split across chunks (partial match)")
            print()
