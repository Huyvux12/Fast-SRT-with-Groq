"""
Formatters module - Output format converters (SRT, TXT, JSON)
"""

import json
from utils import format_time_srt


def to_srt(segments: list) -> str:
    """Chuyển đổi segments sang định dạng SRT"""
    srt_lines = []
    for i, segment in enumerate(segments):
        start_time = format_time_srt(segment['start'])
        end_time = format_time_srt(segment['end'])
        text = segment['text'].strip()
        srt_lines.append(f"{i + 1}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_lines)


def to_txt(segments: list) -> str:
    """Chuyển đổi segments sang text thuần"""
    return "\n".join([segment['text'].strip() for segment in segments])


def to_json(segments: list, full_text: str, language: str, duration: float) -> str:
    """Chuyển đổi sang JSON format"""
    data = {
        "language": language,
        "duration": duration,
        "full_text": full_text,
        "segments": [
            {
                "id": i + 1,
                "start": seg['start'],
                "end": seg['end'],
                "text": seg['text'].strip()
            }
            for i, seg in enumerate(segments)
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
