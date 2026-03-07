"""
Marker - Output Formats
=========================
Marker supports four output formats, each suited to different use cases:

1. Markdown - Clean markdown with tables, equations (LaTeX), code blocks
2. JSON     - Tree structure with pages, blocks, types, and coordinates
3. HTML     - Rendered HTML with images, tables, equations
4. Chunks   - Flattened list of top-level blocks (optimized for RAG)

uv pip install marker-pdf
"""

from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "unstructured_documents"


def output_formats_overview():
    """Show all four output formats and when to use each."""
    print("=" * 60)
    print("MARKER OUTPUT FORMATS")
    print("=" * 60)
    print("""
Format    | Description                       | Best For
----------|-----------------------------------|---------------------------
markdown  | Clean MD with tables, LaTeX, code | RAG text extraction, reading
json      | Tree: pages -> blocks with types  | Programmatic processing,
          | polygon coords, section hierarchy | layout analysis
html      | Rendered HTML with <img>, <math>  | Web display, preview
chunks    | Flat list of top-level blocks     | Direct RAG ingestion,
          | with complete HTML per block      | embedding pipelines

JSON Block Types:
  Line, Span, Table, Figure, Code, Equation, Form,
  SectionHeader, PageHeader, PageFooter, ListItem,
  Caption, Footnote, Handwriting, TextInlineMath

Metadata (all formats):
  - Table of contents
  - Page statistics
  - Text extraction methods used
  - Block type counts
""")

    # Try live demo if marker is installed
    try:
        from marker.config.parser import ConfigParser
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        pdf_path = str(SAMPLES_DIR / "01_pdf" / "sample_docs" / "simple_text.pdf")

        for fmt in ["markdown", "json", "html", "chunks"]:
            config = {"output_format": fmt}
            config_parser = ConfigParser(config)
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
            )
            rendered = converter(pdf_path)
            text, metadata, images = text_from_rendered(rendered)

            print(f"\n--- {fmt.upper()} ({len(text)} chars) ---")
            print(text[:300] + "..." if len(text) > 300 else text)

    except ImportError:
        print("\nInstall marker-pdf to see live output: uv pip install marker-pdf")


if __name__ == "__main__":
    output_formats_overview()
