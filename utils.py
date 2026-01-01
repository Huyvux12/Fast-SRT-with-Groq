"""
Utility functions - Helper functions for time formatting and YouTube
"""

import re
import requests


def format_time_srt(seconds: float) -> str:
    """Chuyển đổi giây sang định dạng SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def get_youtube_video_id(url: str) -> str | None:
    """Trích xuất video ID từ URL YouTube"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_thumbnail(url: str) -> str | None:
    """Lấy URL thumbnail từ YouTube video"""
    video_id = get_youtube_video_id(url)
    if video_id:
        thumbnail_urls = [
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        ]
        for thumb_url in thumbnail_urls:
            try:
                response = requests.head(thumb_url, timeout=5)
                if response.status_code == 200:
                    return thumb_url
            except:
                continue
        return thumbnail_urls[1]
    return None
