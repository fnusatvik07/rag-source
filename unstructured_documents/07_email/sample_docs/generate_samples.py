"""Generate sample .eml files for testing email extraction methods."""

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent


def generate_plain_text_email():
    """A simple plain text email about a project update."""
    msg = MIMEText(
        "Hi Team,\n"
        "\n"
        "I wanted to share a quick update on the Project Atlas initiative.\n"
        "\n"
        "Phase 1 - Data Collection:\n"
        "We have successfully completed the data collection phase ahead of schedule. "
        "The team gathered over 15,000 documents from 12 different source systems, "
        "including internal wikis, customer support tickets, and product documentation. "
        "Quality checks indicate that approximately 92% of the collected documents "
        "meet our minimum quality threshold for downstream processing.\n"
        "\n"
        "Phase 2 - Pipeline Development:\n"
        "The engineering team has begun building the document parsing pipeline. "
        "We are using a modular architecture that supports PDF, DOCX, HTML, and "
        "plain text formats. Initial benchmarks show processing speeds of roughly "
        "500 documents per minute on our current infrastructure. We expect to have "
        "the pipeline fully operational by the end of next week.\n"
        "\n"
        "Phase 3 - Embedding and Indexing:\n"
        "This phase is scheduled to begin on March 15th. We have evaluated three "
        "embedding models and have selected the one that provides the best balance "
        "between quality and latency for our use case. The vector database has been "
        "provisioned and is ready for ingestion.\n"
        "\n"
        "Next Steps:\n"
        "- Complete pipeline testing with edge cases\n"
        "- Finalize the chunking strategy (currently leaning toward recursive splitting)\n"
        "- Set up monitoring dashboards for pipeline health\n"
        "- Schedule a demo with stakeholders for March 20th\n"
        "\n"
        "Please let me know if you have any questions or concerns. I am available "
        "for a sync call tomorrow between 2-4 PM EST.\n"
        "\n"
        "Best regards,\n"
        "Sarah Chen\n"
        "Senior Data Engineer\n"
        "Project Atlas Team",
        "plain",
        "utf-8",
    )

    msg["From"] = "Sarah Chen <sarah.chen@techcorp.com>"
    msg["To"] = "project-atlas-team@techcorp.com"
    msg["CC"] = "james.wilson@techcorp.com, maria.garcia@techcorp.com"
    msg["Subject"] = "Project Atlas - Weekly Status Update (Week 10)"
    msg["Date"] = "Mon, 10 Mar 2025 09:30:00 -0500"
    msg["Message-ID"] = "<atlas-update-w10-20250310@techcorp.com>"

    (SAMPLE_DIR / "plain_text.eml").write_text(msg.as_string())
    print("Generated: plain_text.eml")


def generate_html_email():
    """An HTML newsletter email with both HTML and plain text parts."""
    msg = MIMEMultipart("alternative")

    msg["From"] = "AI Weekly Newsletter <newsletter@aiweekly.io>"
    msg["To"] = "subscriber@example.com"
    msg["Subject"] = "AI Weekly #42: Advances in Retrieval-Augmented Generation"
    msg["Date"] = "Fri, 14 Mar 2025 08:00:00 +0000"
    msg["Message-ID"] = "<newsletter-42-20250314@aiweekly.io>"

    # Plain text version
    plain_text = (
        "AI WEEKLY NEWSLETTER - Issue #42\n"
        "================================\n"
        "\n"
        "TOP STORY: Advances in Retrieval-Augmented Generation\n"
        "\n"
        "This week saw several breakthrough papers in RAG technology. "
        "Researchers at Stanford published a new framework called AdaptiveRAG "
        "that dynamically adjusts retrieval strategies based on query complexity. "
        "The system achieves a 23% improvement over standard RAG pipelines on "
        "the Natural Questions benchmark.\n"
        "\n"
        "KEY HIGHLIGHTS:\n"
        "\n"
        "1. New Chunking Strategies\n"
        "A comprehensive study comparing 8 different chunking strategies found "
        "that semantic chunking with overlap consistently outperforms fixed-size "
        "approaches. The optimal chunk size varies by domain but generally falls "
        "between 256-512 tokens.\n"
        "\n"
        "2. Embedding Model Benchmarks\n"
        "The MTEB leaderboard was updated with 15 new models. The top performers "
        "now achieve over 70% on the retrieval subset. Notable entries include "
        "models optimized for specific domains like legal and medical text.\n"
        "\n"
        "3. Production RAG Patterns\n"
        "A popular blog post outlined seven common patterns for production RAG "
        "systems, including hybrid search (combining dense and sparse retrieval), "
        "query expansion, and re-ranking with cross-encoders.\n"
        "\n"
        "UPCOMING EVENTS:\n"
        "- RAG Summit 2025 - April 5-6, San Francisco\n"
        "- NeurIPS Workshop on Retrieval - June 12, Virtual\n"
        "\n"
        "---\n"
        "You are receiving this because you subscribed at aiweekly.io\n"
        "Unsubscribe: https://aiweekly.io/unsubscribe\n"
    )
    plain_part = MIMEText(plain_text, "plain", "utf-8")

    # HTML version
    html_text = """\
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .highlight { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }
        .footer { background-color: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; }
        h2 { color: #2c3e50; }
        h3 { color: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Weekly Newsletter</h1>
        <p>Issue #42 - March 14, 2025</p>
    </div>

    <div class="content">
        <h2>Top Story: Advances in Retrieval-Augmented Generation</h2>
        <p>This week saw several breakthrough papers in RAG technology.
        Researchers at Stanford published a new framework called <strong>AdaptiveRAG</strong>
        that dynamically adjusts retrieval strategies based on query complexity.
        The system achieves a <em>23% improvement</em> over standard RAG pipelines on
        the Natural Questions benchmark.</p>

        <h2>Key Highlights</h2>

        <div class="highlight">
            <h3>1. New Chunking Strategies</h3>
            <p>A comprehensive study comparing 8 different chunking strategies found
            that semantic chunking with overlap consistently outperforms fixed-size
            approaches. The optimal chunk size varies by domain but generally falls
            between 256-512 tokens.</p>
        </div>

        <div class="highlight">
            <h3>2. Embedding Model Benchmarks</h3>
            <p>The MTEB leaderboard was updated with 15 new models. The top performers
            now achieve over 70% on the retrieval subset. Notable entries include
            models optimized for specific domains like legal and medical text.</p>
        </div>

        <div class="highlight">
            <h3>3. Production RAG Patterns</h3>
            <p>A popular blog post outlined seven common patterns for production RAG
            systems, including hybrid search (combining dense and sparse retrieval),
            query expansion, and re-ranking with cross-encoders.</p>
        </div>

        <h2>Upcoming Events</h2>
        <ul>
            <li><strong>RAG Summit 2025</strong> - April 5-6, San Francisco</li>
            <li><strong>NeurIPS Workshop on Retrieval</strong> - June 12, Virtual</li>
        </ul>
    </div>

    <div class="footer">
        <p>You are receiving this because you subscribed at aiweekly.io</p>
        <p><a href="https://aiweekly.io/unsubscribe">Unsubscribe</a></p>
    </div>
</body>
</html>"""
    html_part = MIMEText(html_text, "html", "utf-8")

    # Attach plain text first, then HTML (email clients prefer the last part)
    msg.attach(plain_part)
    msg.attach(html_part)

    (SAMPLE_DIR / "html_email.eml").write_text(msg.as_string())
    print("Generated: html_email.eml")


def generate_email_with_attachment():
    """An email with a text file attachment containing meeting notes."""
    msg = MIMEMultipart("mixed")

    msg["From"] = "David Park <david.park@techcorp.com>"
    msg["To"] = "engineering-leads@techcorp.com"
    msg["CC"] = "sarah.chen@techcorp.com"
    msg["Subject"] = "Architecture Review Meeting Notes - March 12"
    msg["Date"] = "Wed, 12 Mar 2025 16:45:00 -0500"
    msg["Message-ID"] = "<arch-review-20250312@techcorp.com>"

    # Email body
    body = MIMEText(
        "Hi everyone,\n"
        "\n"
        "Please find attached the meeting notes from today's architecture review. "
        "We covered several important topics including the migration plan and "
        "the new caching strategy.\n"
        "\n"
        "Key decisions made:\n"
        "1. We will proceed with the microservices migration in Q2\n"
        "2. Redis will be adopted as our primary caching layer\n"
        "3. API versioning will follow the URL path strategy (v1, v2, etc.)\n"
        "\n"
        "Action items are listed in the attached notes. Please review and "
        "confirm your assignments by end of day Friday.\n"
        "\n"
        "Thanks,\n"
        "David Park\n"
        "Engineering Manager",
        "plain",
        "utf-8",
    )
    msg.attach(body)

    # Create the attachment content
    attachment_content = (
        "ARCHITECTURE REVIEW MEETING NOTES\n"
        "Date: March 12, 2025\n"
        "Attendees: David Park, Sarah Chen, Alex Rivera, Priya Patel, Tom Zhang\n"
        "Location: Conference Room B / Zoom\n"
        "\n"
        "=" * 60 + "\n"
        "\n"
        "AGENDA ITEM 1: Microservices Migration Plan\n"
        "-" * 40 + "\n"
        "Current State:\n"
        "- Monolithic application serving 50K requests/minute\n"
        "- Deployment cycle: 2 weeks\n"
        "- Single PostgreSQL database with 200+ tables\n"
        "\n"
        "Proposed Architecture:\n"
        "- Break into 8 domain services (User, Auth, Product, Order, Payment, "
        "Notification, Analytics, Search)\n"
        "- Each service owns its data store\n"
        "- Communication via async messaging (RabbitMQ) for events, "
        "gRPC for synchronous calls\n"
        "- API Gateway (Kong) for external traffic routing\n"
        "\n"
        "Timeline:\n"
        "- Q2 2025: Extract User and Auth services\n"
        "- Q3 2025: Extract Product and Order services\n"
        "- Q4 2025: Extract remaining services\n"
        "- Q1 2026: Decommission monolith\n"
        "\n"
        "Decision: APPROVED - proceed with Q2 extraction\n"
        "\n"
        "AGENDA ITEM 2: Caching Strategy\n"
        "-" * 40 + "\n"
        "Options Evaluated:\n"
        "1. Redis (standalone) - Selected\n"
        "   - Pros: Mature, fast, rich data structures, pub/sub support\n"
        "   - Cons: Memory-bound, requires cluster management\n"
        "\n"
        "2. Memcached\n"
        "   - Pros: Simple, multi-threaded\n"
        "   - Cons: No persistence, limited data structures\n"
        "\n"
        "3. Application-level caching\n"
        "   - Pros: No external dependency\n"
        "   - Cons: Not shared across instances, cache invalidation complexity\n"
        "\n"
        "Decision: Redis with 3-node cluster, 6GB per node\n"
        "\n"
        "AGENDA ITEM 3: API Versioning\n"
        "-" * 40 + "\n"
        "Approaches Discussed:\n"
        "- URL path versioning: /api/v1/users (Selected)\n"
        "- Header versioning: Accept: application/vnd.api.v1+json\n"
        "- Query parameter: /api/users?version=1\n"
        "\n"
        "Decision: URL path versioning for simplicity and discoverability\n"
        "\n"
        "ACTION ITEMS:\n"
        "-" * 40 + "\n"
        "1. [Sarah Chen] Draft service boundary document by March 19\n"
        "2. [Alex Rivera] Set up Redis cluster in staging by March 17\n"
        "3. [Priya Patel] Create API versioning RFC by March 21\n"
        "4. [Tom Zhang] Benchmark current monolith performance as baseline\n"
        "5. [David Park] Schedule follow-up review for March 26\n"
        "\n"
        "Next Meeting: March 26, 2025 at 2:00 PM EST\n"
    )

    # Create the attachment
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(attachment_content.encode("utf-8"))
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename="meeting_notes_2025-03-12.txt",
    )
    msg.attach(attachment)

    (SAMPLE_DIR / "with_attachment.eml").write_text(msg.as_string())
    print("Generated: with_attachment.eml")


if __name__ == "__main__":
    generate_plain_text_email()
    generate_html_email()
    generate_email_with_attachment()
    print("\nAll email samples generated!")
