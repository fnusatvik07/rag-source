"""
Email Parsing with Python's Built-in email Module

The email module in Python's standard library provides full support for parsing
MIME-formatted email messages (.eml files). It can handle multipart messages,
attachments, various encodings, and all standard email headers.

Best for: Parsing .eml files, extracting headers/body/attachments, handling MIME structure.
"""

import re
import sys
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

SAMPLE_DIR = Path(__file__).parent / "sample_docs"


# ---------------------------------------------------------------------------
# HTML tag stripper using Python's built-in html.parser
# ---------------------------------------------------------------------------


class HTMLTextExtractor(HTMLParser):
    """Strip HTML tags and return plain text content."""

    def __init__(self):
        super().__init__()
        self._result = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        # Skip content inside <style> and <script> tags
        if tag in ("style", "script"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip = False
        # Add newlines after block-level elements
        if tag in ("p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"):
            self._result.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._result.append(data)

    def get_text(self) -> str:
        raw = "".join(self._result)
        # Collapse excessive whitespace while preserving paragraph breaks
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def strip_html_tags(html: str) -> str:
    """Convert HTML to plain text by stripping tags."""
    extractor = HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


# ---------------------------------------------------------------------------
# Email parsing functions
# ---------------------------------------------------------------------------


def load_email(eml_path: Path):
    """Load and parse an .eml file into an email.message.EmailMessage object."""
    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    return msg


def extract_headers(msg) -> dict:
    """Extract common email headers into a dictionary."""
    headers = {}
    for header_name in ("From", "To", "CC", "Subject", "Date", "Message-ID"):
        value = msg.get(header_name, "")
        headers[header_name] = str(value) if value else ""
    return headers


def extract_body(msg) -> dict:
    """
    Extract the email body, handling both plain text and HTML parts.

    Returns a dict with 'plain' and 'html' keys. If the email is multipart,
    both may be populated. For HTML-only emails, we also generate a
    stripped-text version.
    """
    body = {"plain": "", "html": "", "plain_from_html": ""}

    if msg.is_multipart():
        # Walk through all MIME parts
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain":
                payload = part.get_content()
                if isinstance(payload, str):
                    body["plain"] = payload
            elif content_type == "text/html":
                payload = part.get_content()
                if isinstance(payload, str):
                    body["html"] = payload
                    body["plain_from_html"] = strip_html_tags(payload)
    else:
        # Single-part message
        content_type = msg.get_content_type()
        payload = msg.get_content()
        if isinstance(payload, str):
            if content_type == "text/plain":
                body["plain"] = payload
            elif content_type == "text/html":
                body["html"] = payload
                body["plain_from_html"] = strip_html_tags(payload)

    return body


def extract_attachments(msg) -> list[dict]:
    """
    Extract attachment information and content from an email.

    Returns a list of dicts with filename, content_type, size, and content.
    """
    attachments = []

    if not msg.is_multipart():
        return attachments

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        if "attachment" not in content_disposition:
            continue

        filename = part.get_filename() or "unknown"
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)

        attachment_info = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(payload) if payload else 0,
        }

        # Try to decode text attachments
        if payload and content_type.startswith("text/"):
            try:
                attachment_info["content"] = payload.decode("utf-8")
            except UnicodeDecodeError:
                attachment_info["content"] = payload.decode("latin-1")
        else:
            attachment_info["content"] = f"[Binary content: {len(payload)} bytes]" if payload else ""

        attachments.append(attachment_info)

    return attachments


def parse_email_complete(eml_path: Path) -> dict:
    """Parse an email file and return all extracted information."""
    msg = load_email(eml_path)
    return {
        "file": eml_path.name,
        "headers": extract_headers(msg),
        "body": extract_body(msg),
        "attachments": extract_attachments(msg),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    eml_files = sorted(SAMPLE_DIR.glob("*.eml"))

    if not eml_files:
        print("No .eml files found. Run generate_samples.py first.")
        sys.exit(1)

    for eml_path in eml_files:
        print("=" * 70)
        print(f"FILE: {eml_path.name}")
        print("=" * 70)

        result = parse_email_complete(eml_path)

        # --- Headers ---
        print("\n--- Headers ---")
        for key, value in result["headers"].items():
            print(f"  {key}: {value}")

        # --- Body ---
        print("\n--- Body ---")
        body = result["body"]
        if body["plain"]:
            print(f"  Plain text ({len(body['plain'])} chars):")
            # Show first 300 chars
            preview = body["plain"][:300]
            for line in preview.split("\n"):
                print(f"    {line}")
            if len(body["plain"]) > 300:
                print(f"    ... ({len(body['plain']) - 300} more chars)")

        if body["html"]:
            print(f"\n  HTML body present ({len(body['html'])} chars)")
            print(f"  Stripped HTML to plain text ({len(body['plain_from_html'])} chars):")
            preview = body["plain_from_html"][:300]
            for line in preview.split("\n"):
                print(f"    {line}")
            if len(body["plain_from_html"]) > 300:
                print(f"    ... ({len(body['plain_from_html']) - 300} more chars)")

        # --- Attachments ---
        if result["attachments"]:
            print(f"\n--- Attachments ({len(result['attachments'])}) ---")
            for att in result["attachments"]:
                print(f"  Filename: {att['filename']}")
                print(f"  Type: {att['content_type']}")
                print(f"  Size: {att['size_bytes']} bytes")
                if att.get("content") and not att["content"].startswith("[Binary"):
                    preview = att["content"][:200]
                    print("  Content preview:")
                    for line in preview.split("\n"):
                        print(f"    {line}")
                    if len(att["content"]) > 200:
                        print(f"    ... ({len(att['content']) - 200} more chars)")
        else:
            print("\n--- No attachments ---")

        print()
