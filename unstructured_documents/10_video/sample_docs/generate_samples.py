"""
Generate sample video files for testing video extraction methods.

Creates short videos with text overlays and spoken-word style content
that can be used to demonstrate transcription and frame extraction.

Requirements:
  - Python: opencv-python-headless (or opencv-python)

Usage:
    uv run python unstructured_documents/10_video/sample_docs/generate_samples.py
"""

import sys
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent


def check_opencv_available() -> bool:
    """Check if OpenCV is available."""
    try:
        import cv2  # noqa: F401

        return True
    except ImportError:
        print("=" * 60)
        print("opencv-python-headless is NOT installed.")
        print("=" * 60)
        print()
        print("Install it with:")
        print("  uv sync --extra video")
        print("  # or: uv pip install opencv-python-headless")
        print()
        return False


def generate_lecture_video():
    """
    Generate a sample 'lecture' video with text slides.

    Creates a short video (10 seconds, 1 fps) with text frames simulating
    a lecture about machine learning. Each frame displays different content,
    providing material for both frame extraction and (simulated) transcription.
    """
    import cv2
    import numpy as np

    output_path = SAMPLE_DIR / "lecture.mp4"

    # Video settings
    width, height = 640, 480
    fps = 1
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    slides = [
        {
            "title": "Introduction to Machine Learning",
            "body": "Machine learning is a subset of AI that enables\n"
            "systems to learn from data without being\n"
            "explicitly programmed.",
        },
        {
            "title": "Supervised Learning",
            "body": "The model learns from labeled training data.\n"
            "Common algorithms: Linear Regression,\n"
            "Decision Trees, Neural Networks.",
        },
        {
            "title": "Unsupervised Learning",
            "body": "The model finds patterns in unlabeled data.\n"
            "Common algorithms: K-Means Clustering,\n"
            "PCA, Autoencoders.",
        },
        {
            "title": "Deep Learning",
            "body": "Neural networks with many layers can learn\n"
            "complex representations. Used in image\n"
            "recognition and NLP.",
        },
        {
            "title": "Training Process",
            "body": "1. Prepare data\n"
            "2. Choose architecture\n"
            "3. Train with backpropagation\n"
            "4. Evaluate on test set",
        },
        {
            "title": "Applications",
            "body": "Image recognition, natural language processing,\n"
            "recommendation systems, autonomous vehicles,\n"
            "medical diagnosis.",
        },
        {
            "title": "RAG Systems",
            "body": "Retrieval-Augmented Generation combines\n"
            "document retrieval with language models\n"
            "for accurate, grounded answers.",
        },
        {
            "title": "Document Parsing for RAG",
            "body": "Extract text from PDFs, DOCX, HTML, images,\n"
            "and video. Chunk the text and embed it\n"
            "for vector search.",
        },
        {
            "title": "Video in RAG Pipelines",
            "body": "Transcribe audio with Whisper.\n"
            "Extract keyframes for visual context.\n"
            "Chunk transcript for retrieval.",
        },
        {
            "title": "Summary",
            "body": "Machine learning enables intelligent systems.\n"
            "RAG makes LLMs more accurate.\n"
            "Video is a rich source for RAG.",
        },
    ]

    for slide in slides:
        # Create a dark blue background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (80, 50, 20)  # Dark blue-gray (BGR)

        # Draw title
        cv2.putText(
            frame,
            slide["title"],
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # Draw separator line
        cv2.line(frame, (30, 80), (width - 30, 80), (200, 200, 200), 1)

        # Draw body text (handle newlines)
        y_offset = 130
        for line in slide["body"].split("\n"):
            cv2.putText(
                frame,
                line.strip(),
                (40, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (220, 220, 220),
                1,
            )
            y_offset += 35

        writer.write(frame)

    writer.release()
    print(f"  Created: {output_path.name} ({len(slides)} frames, {width}x{height})")
    return output_path


def generate_short_clip():
    """
    Generate a very short video clip (3 seconds) for quick testing.

    Creates a simple video with colored frames and text, useful for
    verifying that extraction pipelines work before running on longer videos.
    """
    import cv2
    import numpy as np

    output_path = SAMPLE_DIR / "short_clip.mp4"

    width, height = 320, 240
    fps = 1
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    colors_and_text = [
        ((40, 40, 120), "Frame 1: Hello World"),
        ((40, 120, 40), "Frame 2: RAG Pipeline"),
        ((120, 40, 40), "Frame 3: Video Parsing"),
    ]

    for color, text in colors_and_text:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = color
        cv2.putText(
            frame,
            text,
            (15, height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
        writer.write(frame)

    writer.release()
    print(f"  Created: {output_path.name} (3 frames, {width}x{height})")
    return output_path


if __name__ == "__main__":
    if not check_opencv_available():
        sys.exit(1)

    print("Generating sample video files...")
    print()

    generate_lecture_video()
    generate_short_clip()

    print()
    print("Done. Sample videos are ready for extraction demos.")
