"""End-to-end transcription orchestration, independent of Gradio UI internals."""
import re
import tempfile
import time
import uuid
from pathlib import Path

import gradio as gr

from api import transcribe_audio
from config import (
    LANGUAGES, MODELS, OUTPUT_DIR, OUTPUT_FORMATS, OUTPUT_TTL_SECONDS,
)
from formatters import normalize_segments, to_json, to_srt, to_txt
from media import download_youtube_audio, prepare_chunks
from utils import get_youtube_thumbnail, get_youtube_video_id


def update_thumbnail(url: str) -> str:
    thumbnail = get_youtube_thumbnail(url)
    if not thumbnail:
        return '<div class="thumb-placeholder">Paste a valid HTTPS YouTube URL to preview it.</div>'
    return f'<img class="youtube-thumb" src="{thumbnail}" alt="YouTube video thumbnail" />'


def _safe_filename(raw_name: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_-]+", "_", raw_name).strip("_")
    return result[:70] or "recording"


def _cleanup_old_outputs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for item in OUTPUT_DIR.iterdir():
        try:
            if item.is_file() and now - item.stat().st_mtime > OUTPUT_TTL_SECONDS:
                item.unlink()
        except OSError:
            continue


def process_audio(
    api_key: str,
    youtube_url: str,
    uploaded_file: str | None,
    recorded_file: str | None,
    source: str,
    language: str,
    model: str,
    output_format: str,
    progress=gr.Progress(),
) -> tuple[str, str, str]:
    """Return (preview, download path, user-friendly summary)."""
    if not api_key or not api_key.strip():
        raise gr.Error("Enter a Groq API key before processing.")
    if source not in {"youtube", "upload", "microphone"}:
        raise gr.Error("Select an input source.")
    if model not in MODELS or language not in LANGUAGES:
        raise gr.Error("Invalid transcription settings.")
    if output_format not in OUTPUT_FORMATS:
        raise gr.Error("Invalid output format.")

    if source == "youtube":
        video_id = get_youtube_video_id(youtube_url)
        if not video_id:
            raise gr.Error("Enter a valid HTTPS YouTube video link.")
        filename = f"youtube_{video_id}"
    else:
        selected = uploaded_file if source == "upload" else recorded_file
        if not selected:
            raise gr.Error("Select a file or record your audio first.")
        filename = _safe_filename(Path(selected).stem)

    try:
        with tempfile.TemporaryDirectory(prefix="fast-srt-work-") as work_dir:
            progress(0.05, desc="Preparing media...")
            if source == "youtube":
                media_path = download_youtube_audio(youtube_url, work_dir)
            else:
                media_path = str(selected)

            progress(0.20, desc="Converting and splitting audio...")
            chunks, duration = prepare_chunks(media_path, work_dir)
            if not chunks:
                raise ValueError("No audio chunks could be created.")

            segments = []
            detected_language = language
            for index, chunk in enumerate(chunks, 1):
                progress(
                    0.25 + 0.65 * (index - 1) / len(chunks),
                    desc=f"Transcribing chunk {index} of {len(chunks)}...",
                )
                result = transcribe_audio(chunk.path, api_key, language, model)
                if result["language"] and detected_language == "auto":
                    detected_language = str(result["language"])
                for segment in result["segments"]:
                    segments.append({
                        "start": segment["start"] + chunk.offset,
                        "end": min(duration, segment["end"] + chunk.offset),
                        "text": segment["text"],
                    })

            segments = normalize_segments(segments)
            if not segments:
                raise ValueError("No speech with timestamps was detected in this recording.")
            progress(0.94, desc="Building subtitles...")
            text = " ".join(segment["text"] for segment in segments)
            if output_format == "SRT":
                content, ext = to_srt(segments), ".srt"
            elif output_format == "TXT":
                content, ext = to_txt(segments), ".txt"
            else:
                content, ext = to_json(segments, text, detected_language, duration), ".json"

            _cleanup_old_outputs()
            output_path = OUTPUT_DIR / f"{filename}_{uuid.uuid4().hex[:10]}{ext}"
            output_path.write_text(content, encoding="utf-8")
            progress(1.0, desc="Complete!")
            info = (
                f"✅ **Done!** {len(segments)} subtitle segments · "
                f"{duration / 60:.1f} min · {len(chunks)} chunk(s) · "
                f"Language: {detected_language} · Model: {model}"
            )
            return content, str(output_path), info
    except gr.Error:
        raise
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    except OSError as exc:
        raise gr.Error("File processing failed. Check local storage and permissions.") from exc
