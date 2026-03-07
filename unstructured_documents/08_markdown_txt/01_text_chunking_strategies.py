"""
Text Chunking Strategies Comparison

Demonstrates and compares various chunking strategies on a plain text document.
Chunking is the primary challenge when working with plain text for RAG, since
there is no markup or structural metadata to guide the splitting.

This script uses the shared chunking utilities and also implements
paragraph-based chunking to compare approaches side by side.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import (
    chunk_by_characters,
    chunk_by_recursive_split,
    chunk_by_sentences,
    preview_chunks,
)

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


# ---------------------------------------------------------------------------
# Additional chunking strategy: paragraph-based
# ---------------------------------------------------------------------------


def chunk_by_paragraphs(text: str, min_paragraph_length: int = 50) -> list[str]:
    """
    Split text into chunks at paragraph boundaries (double newlines).

    Short paragraphs (below min_paragraph_length) are merged with the next
    paragraph to avoid tiny chunks.
    """
    raw_paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]

    # Merge short paragraphs with the following one
    merged = []
    buffer = ""
    for para in paragraphs:
        if buffer:
            buffer = buffer + "\n\n" + para
        else:
            buffer = para

        if len(buffer) >= min_paragraph_length:
            merged.append(buffer)
            buffer = ""

    if buffer:
        if merged:
            merged[-1] = merged[-1] + "\n\n" + buffer
        else:
            merged.append(buffer)

    return merged


# ---------------------------------------------------------------------------
# Comparison utilities
# ---------------------------------------------------------------------------


def compute_stats(chunks: list[str]) -> dict:
    """Compute summary statistics for a list of text chunks."""
    if not chunks:
        return {"count": 0, "avg_chars": 0, "min_chars": 0, "max_chars": 0}

    lengths = [len(c) for c in chunks]
    return {
        "count": len(chunks),
        "avg_chars": sum(lengths) // len(lengths),
        "min_chars": min(lengths),
        "max_chars": max(lengths),
    }


def print_stats(label: str, stats: dict):
    """Pretty-print chunk statistics."""
    print(
        f"  {label:30s}  "
        f"chunks={stats['count']:>3}  "
        f"avg={stats['avg_chars']:>5} chars  "
        f"min={stats['min_chars']:>4}  "
        f"max={stats['max_chars']:>5}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    text_path = SAMPLE_DIR / "plain_text.txt"

    if not text_path.exists():
        print("plain_text.txt not found. Run generate_samples.py first.")
        sys.exit(1)

    text = text_path.read_text()
    print(f"Loaded: {text_path.name} ({len(text)} chars, ~{len(text.split())} words)\n")

    # ===================================================================
    # Strategy 1: Fixed character chunking at different sizes
    # ===================================================================
    print("=" * 70)
    print("STRATEGY 1: FIXED CHARACTER CHUNKING")
    print("=" * 70)
    print("Splits text at exact character boundaries with overlap.")
    print("Simple but may break mid-word or mid-sentence.\n")

    for size in (200, 500, 1000):
        overlap = size // 10  # 10% overlap
        chunks = chunk_by_characters(text, chunk_size=size, overlap=overlap)
        stats = compute_stats(chunks)
        print_stats(f"chunk_size={size}, overlap={overlap}", stats)

    # Show a sample chunk from the 500-char strategy
    chunks_500 = chunk_by_characters(text, chunk_size=500, overlap=50)
    print("\n  Sample chunk (500 chars, chunk #2):")
    if len(chunks_500) >= 2:
        sample = chunks_500[1]
        print(f'    "{sample[:150]}..."')

    # ===================================================================
    # Strategy 2: Sentence-based chunking
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("STRATEGY 2: SENTENCE-BASED CHUNKING")
    print("=" * 70)
    print("Groups sentences together. Preserves sentence boundaries.")
    print("Better semantic coherence than character-based.\n")

    for spc in (3, 5, 8):
        chunks = chunk_by_sentences(text, sentences_per_chunk=spc, overlap_sentences=1)
        stats = compute_stats(chunks)
        print_stats(f"sentences_per_chunk={spc}", stats)

    chunks_sent = chunk_by_sentences(text, sentences_per_chunk=5, overlap_sentences=1)
    print("\n  Sample chunk (5 sentences, chunk #1):")
    if chunks_sent:
        sample = chunks_sent[0]
        print(f'    "{sample[:200]}..."')

    # ===================================================================
    # Strategy 3: Paragraph-based chunking
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("STRATEGY 3: PARAGRAPH-BASED CHUNKING")
    print("=" * 70)
    print("Splits on double newlines (paragraph breaks).")
    print("Preserves natural topic boundaries within the text.\n")

    chunks_para = chunk_by_paragraphs(text, min_paragraph_length=50)
    stats = compute_stats(chunks_para)
    print_stats("paragraph-based", stats)

    print("\n  Sample chunk (paragraph #1):")
    if chunks_para:
        sample = chunks_para[0]
        print(f'    "{sample[:200]}..."')

    # ===================================================================
    # Strategy 4: Recursive splitting
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("STRATEGY 4: RECURSIVE SPLITTING")
    print("=" * 70)
    print("Tries separators in order: paragraphs > newlines > sentences > chars.")
    print("Balances chunk size with structural boundaries.\n")

    for size in (300, 500, 800):
        chunks = chunk_by_recursive_split(text, chunk_size=size)
        stats = compute_stats(chunks)
        print_stats(f"chunk_size={size}", stats)

    chunks_rec = chunk_by_recursive_split(text, chunk_size=500)
    print("\n  Sample chunk (recursive, 500 chars, chunk #1):")
    if chunks_rec:
        sample = chunks_rec[0]
        print(f'    "{sample[:200]}..."')

    # ===================================================================
    # Summary comparison
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("SUMMARY COMPARISON (all at ~500 char target)")
    print("=" * 70)

    strategies = [
        ("Fixed char (500, overlap=50)", chunk_by_characters(text, 500, 50)),
        ("Sentence (5 per chunk)", chunk_by_sentences(text, 5, 1)),
        ("Paragraph-based", chunk_by_paragraphs(text, 50)),
        ("Recursive (500)", chunk_by_recursive_split(text, 500)),
    ]

    print(f"\n  {'Strategy':35s} {'Chunks':>6}  {'Avg':>6}  {'Min':>5}  {'Max':>5}")
    print(f"  {'-' * 35} {'-' * 6}  {'-' * 6}  {'-' * 5}  {'-' * 5}")

    for label, chunks in strategies:
        s = compute_stats(chunks)
        print(f"  {label:35s} {s['count']:>6}  {s['avg_chars']:>6}  {s['min_chars']:>5}  {s['max_chars']:>5}")

    # ===================================================================
    # Preview each strategy
    # ===================================================================
    print(f"\n{'=' * 70}")
    print("DETAILED PREVIEWS")
    print("=" * 70)

    for label, chunks in strategies:
        print(f"\n--- {label} ---")
        preview_chunks(chunks, max_preview=2, max_chars=150)
