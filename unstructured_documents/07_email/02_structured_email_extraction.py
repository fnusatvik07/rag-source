"""
RAG-Optimized Email Extraction

Transforms parsed email data into structured representations suitable for
retrieval-augmented generation. Combines email metadata and body into
unified text blocks, and demonstrates different chunking strategies for
email content.

Best for: Building RAG pipelines over email archives, knowledge bases from email threads.
"""

import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Re-use parsing utilities from the companion script.
# Directory/file names start with digits, so we import via importlib.
import importlib.util

from unstructured_documents.shared.chunking import (
    chunk_by_recursive_split,
    chunk_by_sentences,
    preview_chunks,
)

_parsing_spec = importlib.util.spec_from_file_location(
    "email_parsing",
    Path(__file__).parent / "01_email_parsing.py",
)
_parsing_mod = importlib.util.module_from_spec(_parsing_spec)
_parsing_spec.loader.exec_module(_parsing_mod)

extract_headers = _parsing_mod.extract_headers
extract_body = _parsing_mod.extract_body
extract_attachments = _parsing_mod.extract_attachments
strip_html_tags = _parsing_mod.strip_html_tags

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


# ---------------------------------------------------------------------------
# Structured email representation
# ---------------------------------------------------------------------------


def build_email_record(eml_path: Path) -> dict:
    """
    Parse an .eml file into a structured record optimised for RAG.

    Keys returned:
        subject, from, to, cc, date, message_id,
        body_text, attachments_text, attachment_names
    """
    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    headers = extract_headers(msg)
    body = extract_body(msg)
    attachments = extract_attachments(msg)

    # Prefer plain text body; fall back to HTML-stripped text
    body_text = body["plain"] or body["plain_from_html"] or ""

    # Collect text from text-based attachments
    attachments_text_parts = []
    attachment_names = []
    for att in attachments:
        attachment_names.append(att["filename"])
        content = att.get("content", "")
        if content and not content.startswith("[Binary"):
            attachments_text_parts.append(f"--- Attachment: {att['filename']} ---\n{content}")

    return {
        "subject": headers.get("Subject", ""),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "cc": headers.get("CC", ""),
        "date": headers.get("Date", ""),
        "message_id": headers.get("Message-ID", ""),
        "body_text": body_text.strip(),
        "attachments_text": "\n\n".join(attachments_text_parts),
        "attachment_names": attachment_names,
    }


# ---------------------------------------------------------------------------
# RAG-ready text block construction
# ---------------------------------------------------------------------------


def email_to_rag_text(record: dict, include_attachments: bool = True) -> str:
    """
    Combine email metadata and body into a single RAG-ready text block.

    Format:
        Email from <sender> to <recipient> on <date>.
        Subject: <subject>

        Body:
        <body text>

        Attachments:
        <attachment text>
    """
    parts = [
        f"Email from {record['from']} to {record['to']} on {record['date']}.",
    ]
    if record["cc"]:
        parts.append(f"CC: {record['cc']}.")
    parts.append(f"Subject: {record['subject']}.")
    parts.append("")
    parts.append("Body:")
    parts.append(record["body_text"])

    if include_attachments and record["attachments_text"]:
        parts.append("")
        parts.append("Attachments:")
        parts.append(record["attachments_text"])

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Chunking strategies for emails
# ---------------------------------------------------------------------------


def chunk_per_email(records: list[dict]) -> list[str]:
    """
    Strategy 1: One chunk per email.

    Each email becomes a single chunk containing metadata + body.
    Good for: Short emails, search-style retrieval, preserving full context.
    Bad for: Very long emails that exceed embedding model token limits.
    """
    return [email_to_rag_text(r) for r in records]


def chunk_email_body_only(records: list[dict], chunk_size: int = 500) -> list[dict]:
    """
    Strategy 2: Chunk the body of each email separately, keeping metadata.

    Each chunk includes the email metadata as a prefix for context,
    followed by a portion of the body text.
    Good for: Long emails, fine-grained retrieval within a single message.
    """
    all_chunks = []
    for record in records:
        metadata_prefix = (
            f"Email from {record['from']} to {record['to']} on {record['date']}. Subject: {record['subject']}.\n\n"
        )
        body_chunks = chunk_by_recursive_split(record["body_text"], chunk_size=chunk_size)
        for i, chunk_text in enumerate(body_chunks):
            all_chunks.append(
                {
                    "text": metadata_prefix + chunk_text,
                    "source_email": record["subject"],
                    "chunk_index": i,
                    "total_chunks": len(body_chunks),
                }
            )

        # Attachment text as separate chunks
        if record["attachments_text"]:
            att_chunks = chunk_by_recursive_split(record["attachments_text"], chunk_size=chunk_size)
            for j, att_chunk in enumerate(att_chunks):
                all_chunks.append(
                    {
                        "text": metadata_prefix + f"[Attachment content]\n{att_chunk}",
                        "source_email": record["subject"],
                        "chunk_index": len(body_chunks) + j,
                        "total_chunks": len(body_chunks) + len(att_chunks),
                    }
                )

    return all_chunks


def chunk_email_sentences(records: list[dict], sentences_per_chunk: int = 5) -> list[str]:
    """
    Strategy 3: Sentence-based chunking on the combined RAG text.

    Splits the full email text (metadata + body) into sentence-based chunks.
    Good for: Consistent chunk sizes, sentence-boundary preservation.
    """
    all_chunks = []
    for record in records:
        full_text = email_to_rag_text(record)
        chunks = chunk_by_sentences(full_text, sentences_per_chunk=sentences_per_chunk)
        all_chunks.extend(chunks)
    return all_chunks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    eml_files = sorted(SAMPLE_DIR.glob("*.eml"))

    if not eml_files:
        print("No .eml files found. Run generate_samples.py first.")
        sys.exit(1)

    # --- Step 1: Build structured records ---
    print("=" * 70)
    print("STEP 1: BUILD STRUCTURED EMAIL RECORDS")
    print("=" * 70)

    records = []
    for eml_path in eml_files:
        record = build_email_record(eml_path)
        records.append(record)
        print(f"\n  File: {eml_path.name}")
        print(f"  Subject: {record['subject']}")
        print(f"  From: {record['from']}")
        print(f"  To: {record['to']}")
        print(f"  Date: {record['date']}")
        print(f"  Body length: {len(record['body_text'])} chars")
        print(f"  Attachments: {record['attachment_names'] or 'None'}")

    # --- Step 2: RAG-ready text blocks ---
    print(f"\n{'=' * 70}")
    print("STEP 2: RAG-READY TEXT BLOCKS")
    print("=" * 70)

    for record in records:
        rag_text = email_to_rag_text(record)
        print(f"\n--- {record['subject']} ({len(rag_text)} chars) ---")
        # Show first 400 chars
        preview = rag_text[:400]
        print(preview)
        if len(rag_text) > 400:
            print(f"... ({len(rag_text) - 400} more chars)")

    # --- Step 3: Chunking strategy comparison ---
    print(f"\n{'=' * 70}")
    print("STEP 3: CHUNKING STRATEGY COMPARISON")
    print("=" * 70)

    # Strategy 1: One chunk per email
    print("\n--- Strategy 1: One chunk per email ---")
    per_email_chunks = chunk_per_email(records)
    print(f"Total chunks: {len(per_email_chunks)}")
    for i, chunk in enumerate(per_email_chunks):
        print(f"  Chunk {i + 1}: {len(chunk)} chars")

    # Strategy 2: Body chunking with metadata prefix
    print("\n--- Strategy 2: Body chunking (500 char chunks) ---")
    body_chunks = chunk_email_body_only(records, chunk_size=500)
    print(f"Total chunks: {len(body_chunks)}")
    for chunk_info in body_chunks[:5]:
        print(
            f"  [{chunk_info['source_email']}] chunk {chunk_info['chunk_index'] + 1}/"
            f"{chunk_info['total_chunks']} ({len(chunk_info['text'])} chars)"
        )
    if len(body_chunks) > 5:
        print(f"  ... and {len(body_chunks) - 5} more chunks")

    # Strategy 3: Sentence-based chunking
    print("\n--- Strategy 3: Sentence-based chunking (5 sentences/chunk) ---")
    sentence_chunks = chunk_email_sentences(records, sentences_per_chunk=5)
    print(f"Total chunks: {len(sentence_chunks)}")
    preview_chunks(sentence_chunks, max_preview=3, max_chars=200)

    # --- Summary ---
    print(f"\n{'=' * 70}")
    print("CHUNKING STRATEGY SUMMARY")
    print("=" * 70)
    print(
        f"  Per-email:      {len(per_email_chunks):>3} chunks | "
        f"avg {sum(len(c) for c in per_email_chunks) // len(per_email_chunks):>5} chars/chunk"
    )
    body_texts = [c["text"] for c in body_chunks]
    print(
        f"  Body-chunked:   {len(body_chunks):>3} chunks | "
        f"avg {sum(len(c) for c in body_texts) // len(body_texts):>5} chars/chunk"
    )
    print(
        f"  Sentence-based: {len(sentence_chunks):>3} chunks | "
        f"avg {sum(len(c) for c in sentence_chunks) // len(sentence_chunks):>5} chars/chunk"
    )
