"""
Video frame extraction using OpenCV.

Extract frames from video files for visual analysis in RAG systems.
Keyframes capture visual content (slides, diagrams, scenes) that text
transcription alone would miss. Combine with Whisper transcripts for
comprehensive video understanding.

Requirements:
  - Python: opencv-python-headless (or opencv-python)

Strengths:  No external services needed, fast, precise frame control.
Weaknesses: Frames are images (need vision model for text description),
            keyframe detection is heuristic-based.

Usage:
    uv run python unstructured_documents/10_video/02_frame_extraction.py
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import (
    chunk_by_characters,
    preview_chunks,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
LECTURE_VIDEO = SAMPLE_DIR / "lecture.mp4"


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


def extract_metadata(video_path: Path) -> dict:
    """
    Extract video metadata using OpenCV.

    Returns basic video properties: duration, frame count, resolution, FPS.
    For more detailed metadata (codecs, audio info), use ffprobe
    (see 01_whisper_transcription.py).
    """
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {"error": f"Cannot open video: {video_path}"}

    metadata = {
        "filename": video_path.name,
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration_seconds": (
            cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            if cap.get(cv2.CAP_PROP_FPS) > 0
            else 0
        ),
        "codec": int(cap.get(cv2.CAP_PROP_FOURCC)),
    }

    cap.release()
    return metadata


def extract_frames_at_interval(
    video_path: Path,
    interval_sec: float = 1.0,
    output_dir: Path | None = None,
) -> list[dict]:
    """
    Extract frames at regular time intervals.

    Good for: slide-based videos, lectures, presentations where content
    changes at predictable intervals.

    Returns list of dicts with frame index, timestamp, and file path.
    If output_dir is None, frames are not saved to disk (metadata only).
    """
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, int(fps * interval_sec))

    frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            timestamp = frame_idx / fps if fps > 0 else 0
            frame_info = {
                "frame_index": frame_idx,
                "timestamp_sec": round(timestamp, 2),
                "width": frame.shape[1],
                "height": frame.shape[0],
            }

            if output_dir is not None:
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"frame_{frame_idx:06d}.png"
                filepath = output_dir / filename
                cv2.imwrite(str(filepath), frame)
                frame_info["file_path"] = str(filepath)

            frames.append(frame_info)

        frame_idx += 1

    cap.release()
    return frames


def extract_keyframes(
    video_path: Path,
    threshold: float = 30.0,
    output_dir: Path | None = None,
) -> list[dict]:
    """
    Extract keyframes based on scene change detection.

    Compares consecutive frames using mean absolute difference.
    When the difference exceeds the threshold, the frame is considered
    a scene change / keyframe.

    Good for: videos with distinct scenes, slide transitions, topic changes.
    The threshold controls sensitivity (lower = more keyframes detected).

    Returns list of dicts with frame index, timestamp, change score, and
    optionally the saved file path.
    """
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    keyframes = []
    prev_gray = None
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            change_score = float(np.mean(diff))

            if change_score > threshold:
                timestamp = frame_idx / fps if fps > 0 else 0
                frame_info = {
                    "frame_index": frame_idx,
                    "timestamp_sec": round(timestamp, 2),
                    "change_score": round(change_score, 2),
                    "width": frame.shape[1],
                    "height": frame.shape[0],
                }

                if output_dir is not None:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    filename = f"keyframe_{frame_idx:06d}.png"
                    filepath = output_dir / filename
                    cv2.imwrite(str(filepath), frame)
                    frame_info["file_path"] = str(filepath)

                keyframes.append(frame_info)

        # Always capture first frame as a keyframe
        elif frame_idx == 0:
            timestamp = 0.0
            frame_info = {
                "frame_index": 0,
                "timestamp_sec": 0.0,
                "change_score": 0.0,
                "width": frame.shape[1],
                "height": frame.shape[0],
            }

            if output_dir is not None:
                output_dir.mkdir(parents=True, exist_ok=True)
                filepath = output_dir / "keyframe_000000.png"
                cv2.imwrite(str(filepath), frame)
                frame_info["file_path"] = str(filepath)

            keyframes.append(frame_info)

        prev_gray = gray
        frame_idx += 1

    cap.release()
    return keyframes


def build_frame_descriptions(keyframes: list[dict]) -> str:
    """
    Build a text representation of extracted keyframes.

    Creates a structured text from keyframe metadata that can be
    chunked and embedded for RAG. In production, you would use a
    vision model (GPT-4o, Claude, etc.) to describe each frame's
    visual content.

    This function creates placeholder descriptions from metadata.
    Replace with vision model calls for real applications.
    """
    lines = []
    for i, kf in enumerate(keyframes):
        timestamp = kf["timestamp_sec"]
        mins = int(timestamp // 60)
        secs = int(timestamp % 60)
        lines.append(
            f"[{mins:02d}:{secs:02d}] Keyframe {i + 1}: "
            f"Scene at {kf['timestamp_sec']}s "
            f"(change score: {kf.get('change_score', 'N/A')}, "
            f"resolution: {kf['width']}x{kf['height']})"
        )

    return "\n".join(lines)


def demo_metadata():
    """Show video metadata extraction."""
    print("=" * 70)
    print("1. VIDEO METADATA EXTRACTION (OpenCV)")
    print("=" * 70)

    metadata = extract_metadata(LECTURE_VIDEO)
    for key, value in metadata.items():
        print(f"  {key:20s}: {value}")


def demo_interval_extraction():
    """Show frame extraction at regular intervals."""
    print("\n" + "=" * 70)
    print("2. FRAME EXTRACTION AT INTERVALS (every 1 second)")
    print("=" * 70)

    frames = extract_frames_at_interval(LECTURE_VIDEO, interval_sec=1.0)
    print(f"\nExtracted {len(frames)} frames at 1-second intervals")
    for f in frames[:5]:
        print(
            f"  Frame {f['frame_index']:>6d} | "
            f"t={f['timestamp_sec']:>6.2f}s | "
            f"{f['width']}x{f['height']}"
        )
    if len(frames) > 5:
        print(f"  ... and {len(frames) - 5} more frames")


def demo_keyframe_detection():
    """Show keyframe extraction based on scene changes."""
    print("\n" + "=" * 70)
    print("3. KEYFRAME DETECTION (scene change)")
    print("=" * 70)

    keyframes = extract_keyframes(LECTURE_VIDEO, threshold=30.0)
    print(f"\nDetected {len(keyframes)} keyframes (threshold=30.0)")
    for kf in keyframes[:10]:
        print(
            f"  Frame {kf['frame_index']:>6d} | "
            f"t={kf['timestamp_sec']:>6.2f}s | "
            f"change={kf['change_score']:>6.2f} | "
            f"{kf['width']}x{kf['height']}"
        )
    if len(keyframes) > 10:
        print(f"  ... and {len(keyframes) - 10} more keyframes")


def demo_frame_descriptions():
    """Show how to build text from keyframes for RAG chunking."""
    print("\n" + "=" * 70)
    print("4. KEYFRAME DESCRIPTIONS FOR RAG")
    print("=" * 70)

    keyframes = extract_keyframes(LECTURE_VIDEO, threshold=30.0)
    descriptions = build_frame_descriptions(keyframes)
    print(f"\nGenerated descriptions for {len(keyframes)} keyframes:")
    print(descriptions)

    # Chunk the descriptions for embedding
    print("\n--- Chunking Frame Descriptions ---")
    chunks = chunk_by_characters(descriptions, chunk_size=300, overlap=30)
    preview_chunks(chunks, max_preview=3, max_chars=200)


def demo_threshold_comparison():
    """Compare different keyframe detection thresholds."""
    print("\n" + "=" * 70)
    print("5. THRESHOLD COMPARISON")
    print("=" * 70)

    print(f"\n  {'Threshold':>10s} {'Keyframes':>10s}  Notes")
    print(f"  {'-'*10} {'-'*10}  {'-'*30}")

    for threshold in [10.0, 20.0, 30.0, 50.0, 80.0]:
        keyframes = extract_keyframes(LECTURE_VIDEO, threshold=threshold)
        note = ""
        if threshold <= 10:
            note = "(very sensitive, many frames)"
        elif threshold <= 30:
            note = "(balanced)"
        else:
            note = "(less sensitive, fewer frames)"
        print(f"  {threshold:>10.1f} {len(keyframes):>10d}  {note}")


if __name__ == "__main__":
    if not check_opencv_available():
        print("Skipping frame extraction demos (OpenCV not available).")
        sys.exit(0)

    if not LECTURE_VIDEO.exists():
        print(f"ERROR: {LECTURE_VIDEO} not found.")
        print("Run generate_samples.py first:")
        print(
            "  uv run python unstructured_documents/10_video/sample_docs/generate_samples.py"
        )
        sys.exit(1)

    demo_metadata()
    demo_interval_extraction()
    demo_keyframe_detection()
    demo_frame_descriptions()
    demo_threshold_comparison()

    print("\n" + "=" * 70)
    print("Done. OpenCV provides fast, local frame extraction for video RAG.")
    print("Combine with Whisper transcripts (01_whisper_transcription.py)")
    print("for comprehensive video understanding.")
    print("=" * 70)
