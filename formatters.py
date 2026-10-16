"""Strict, reusable subtitle output formatters."""
import json
import math

from utils import format_time_srt


def normalize_segments(segments: list) -> list[dict]:
    """Convert SDK objects/dicts into clean, time-ordered segments."""
    cleaned = []
    for raw in segments or []:
        if hasattr(raw, "model_dump"):
            raw = raw.model_dump()
        elif not isinstance(raw, dict):
            raw = {
                "start": getattr(raw, "start", None),
                "end": getattr(raw, "end", None),
                "text": getattr(raw, "text", ""),
            }
        try:
            start, end = float(raw["start"]), float(raw["end"])
            text = str(raw.get("text") or "").strip()
        except (KeyError, TypeError, ValueError):
            continue
        if not all(math.isfinite(t) for t in (start, end)):
            continue
        if start < 0 or end < start or not text:
            continue
        cleaned.append({"start": start, "end": end, "text": text})
    cleaned.sort(key=lambda seg: (seg["start"], seg["end"]))
    return cleaned


def to_srt(segments: list[dict]) -> str:
    lines = []
    for i, segment in enumerate(normalize_segments(segments), 1):
        lines.append(
            f"{i}\n{format_time_srt(segment['start'])} --> "
            f"{format_time_srt(segment['end'])}\n{segment['text']}"
        )
    return "\n\n".join(lines) + ("\n" if lines else "")


def to_txt(segments: list[dict]) -> str:
    return "\n".join(segment["text"] for segment in normalize_segments(segments))


def to_json(segments: list[dict], full_text: str, language: str, duration: float) -> str:
    normalized = normalize_segments(segments)
    return json.dumps(
        {
            "language": language,
            "duration": duration,
            "full_text": full_text,
            "segments": [
                {"id": i, **segment} for i, segment in enumerate(normalized, 1)
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
