"""
Video transcription using OpenAI Whisper.

Whisper is a general-purpose speech recognition model from OpenAI.
It can transcribe audio in multiple languages with word-level timestamps.
For video files, we first extract the audio track, then run Whisper on it.

Requirements:
  - System: ffmpeg must be installed on the OS
    macOS:   brew install ffmpeg
    Ubuntu:  sudo apt-get install ffmpeg
    Windows: https://www.gyan.dev/ffmpeg/builds/
  - Python:  pip install openai-whisper

Strengths:  High accuracy, multilingual, word-level timestamps, fully local.
Weaknesses: Requires ffmpeg, GPU recommended for speed, large model downloads.

Usage:
    uv run python unstructured_documents/10_video/01_whisper_transcription.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unstructured_documents.shared.chunking import (
    chunk_by_characters,
    chunk_by_sentences,
    preview_chunks,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
LECTURE_VIDEO = SAMPLE_DIR / "lecture.mp4"


def check_whisper_available() -> bool:
    """Check if openai-whisper and ffmpeg are available."""
    try:
        import whisper  # noqa: F401

        return True
    except ImportError:
        print("=" * 60)
        print("openai-whisper is NOT installed.")
        print("=" * 60)
        print()
        print("Install it with:")
        print("  uv sync --extra video")
        print("  # or: uv pip install openai-whisper")
        print()
        print("You also need ffmpeg on your system:")
        print("  macOS:   brew install ffmpeg")
        print("  Ubuntu:  sudo apt-get install ffmpeg")
        print("  Windows: https://www.gyan.dev/ffmpeg/builds/")
        print()
        return False


def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is available on the system."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("=" * 60)
        print("ffmpeg is NOT installed.")
        print("=" * 60)
        print()
        print("Install it:")
        print("  macOS:   brew install ffmpeg")
        print("  Ubuntu:  sudo apt-get install ffmpeg")
        print("  Windows: https://www.gyan.dev/ffmpeg/builds/")
        print()
        return False


def extract_audio(video_path: Path, output_path: Path | None = None) -> Path:
    """
    Extract audio track from a video file using ffmpeg.

    Converts the audio to 16kHz mono WAV, which is the format Whisper expects.
    If output_path is not specified, creates a temporary file.
    """
    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".wav"))

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",  # 16-bit PCM
            "-ar",
            "16000",  # 16kHz sample rate
            "-ac",
            "1",  # Mono
            "-y",  # Overwrite
            str(output_path),
        ],
        capture_output=True,
        check=True,
    )
    return output_path


def transcribe_video(video_path: Path, model_size: str = "base") -> dict:
    """
    Transcribe a video file using Whisper.

    Extracts audio from the video, then runs Whisper speech recognition.
    Returns a dict with the full transcript text, language, and segments.

    Model sizes (accuracy vs speed tradeoff):
      - tiny:   ~1GB RAM, fastest, lower accuracy
      - base:   ~1GB RAM, good balance (recommended to start)
      - small:  ~2GB RAM, better accuracy
      - medium: ~5GB RAM, high accuracy
      - large:  ~10GB RAM, highest accuracy
    """
    import whisper

    model = whisper.load_model(model_size)

    # Whisper can handle video files directly if ffmpeg is available
    result = model.transcribe(str(video_path))

    return {
        "text": result["text"].strip(),
        "language": result.get("language", "unknown"),
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result.get("segments", [])
        ],
    }


def transcribe_with_timestamps(
    video_path: Path, model_size: str = "base"
) -> list[dict]:
    """
    Transcribe video and return timestamped segments.

    Each segment includes start time, end time, and text.
    Useful for creating time-indexed chunks for RAG so users
    can be directed to the exact moment in the video.
    """
    result = transcribe_video(video_path, model_size)
    return result["segments"]


def extract_metadata(video_path: Path) -> dict:
    """
    Extract video metadata using ffprobe (part of ffmpeg).

    Returns duration, resolution, frame rate, codec, and file size.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return {"error": "ffprobe failed", "file": str(video_path)}

    import json

    probe = json.loads(result.stdout)

    metadata = {
        "filename": video_path.name,
        "file_size_bytes": int(probe.get("format", {}).get("size", 0)),
        "duration_seconds": float(probe.get("format", {}).get("duration", 0)),
        "format": probe.get("format", {}).get("format_long_name", "unknown"),
    }

    # Find video stream info
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video":
            metadata["width"] = stream.get("width")
            metadata["height"] = stream.get("height")
            metadata["fps"] = stream.get("r_frame_rate", "unknown")
            metadata["video_codec"] = stream.get("codec_name", "unknown")
            break

    # Find audio stream info
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "audio":
            metadata["audio_codec"] = stream.get("codec_name", "unknown")
            metadata["sample_rate"] = stream.get("sample_rate", "unknown")
            metadata["channels"] = stream.get("channels", 0)
            break

    return metadata


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def demo_metadata():
    """Show video metadata extraction."""
    print("=" * 70)
    print("1. VIDEO METADATA EXTRACTION (ffprobe)")
    print("=" * 70)

    metadata = extract_metadata(LECTURE_VIDEO)
    for key, value in metadata.items():
        print(f"  {key:20s}: {value}")


def demo_transcription():
    """Show full video transcription using Whisper."""
    print("\n" + "=" * 70)
    print("2. FULL TRANSCRIPTION (Whisper)")
    print("=" * 70)

    result = transcribe_video(LECTURE_VIDEO, model_size="base")
    print(f"\nDetected language: {result['language']}")
    print(f"Transcript length: {len(result['text']):,} characters")
    print(f"\nFull transcript:")
    print(result["text"][:500])
    if len(result["text"]) > 500:
        print("...")


def demo_timestamped_segments():
    """Show timestamped transcription segments."""
    print("\n" + "=" * 70)
    print("3. TIMESTAMPED SEGMENTS (Whisper)")
    print("=" * 70)

    segments = transcribe_with_timestamps(LECTURE_VIDEO, model_size="base")
    print(f"\nTotal segments: {len(segments)}")
    for seg in segments[:10]:
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        print(f"  [{start} -> {end}] {seg['text']}")

    if len(segments) > 10:
        print(f"  ... and {len(segments) - 10} more segments")


def demo_chunking():
    """Show how to chunk transcribed text for RAG."""
    print("\n" + "=" * 70)
    print("4. CHUNKING TRANSCRIPT FOR RAG")
    print("=" * 70)

    result = transcribe_video(LECTURE_VIDEO, model_size="base")
    text = result["text"]
    print(f"\nTranscript length: {len(text):,} characters")

    # Strategy 1: Character chunks
    print("\n--- Strategy: Character Chunking (500 chars, 50 overlap) ---")
    char_chunks = chunk_by_characters(text, chunk_size=500, overlap=50)
    preview_chunks(char_chunks, max_preview=2, max_chars=150)

    # Strategy 2: Sentence-based chunks
    print("\n--- Strategy: Sentence Chunking (5 sentences per chunk) ---")
    sent_chunks = chunk_by_sentences(text, sentences_per_chunk=5, overlap_sentences=1)
    preview_chunks(sent_chunks, max_preview=2, max_chars=150)

    # Summary comparison
    print("\n--- Chunking Strategy Comparison ---")
    print(f"  {'Strategy':<25s} {'Chunks':>8s} {'Avg Size':>10s}")
    print(f"  {'-'*25} {'-'*8} {'-'*10}")
    for name, chunks in [
        ("Character (500)", char_chunks),
        ("Sentence (5/chunk)", sent_chunks),
    ]:
        sizes = [len(c) for c in chunks]
        avg = sum(sizes) / len(sizes) if sizes else 0
        print(f"  {name:<25s} {len(chunks):>8d} {avg:>10.1f}")


if __name__ == "__main__":
    if not LECTURE_VIDEO.exists():
        print(f"ERROR: {LECTURE_VIDEO} not found.")
        print("Run generate_samples.py first:")
        print(
            "  uv run python unstructured_documents/10_video/sample_docs/generate_samples.py"
        )
        sys.exit(1)

    # Always show metadata (requires only ffprobe)
    if check_ffmpeg_available():
        demo_metadata()
    else:
        print("Skipping metadata demo (ffmpeg/ffprobe not available).")

    # Transcription demos require Whisper
    if check_whisper_available() and check_ffmpeg_available():
        demo_transcription()
        demo_timestamped_segments()
        demo_chunking()

        print("\n" + "=" * 70)
        print("Done. Whisper provides accurate speech-to-text for video RAG.")
        print("For visual content extraction, see 02_frame_extraction.py")
        print("=" * 70)
    else:
        print("\nSkipping transcription demos (Whisper or ffmpeg not available).")
        print("Install with: uv sync --extra video")
        print("Also install ffmpeg on your system (see docs above).")
