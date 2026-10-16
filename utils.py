"""Safe URL parsing and timestamp helpers."""
import math
import re
from urllib.parse import parse_qs, urlsplit

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com",
    "music.youtube.com", "youtube-nocookie.com",
    "www.youtube-nocookie.com",
}
SHORT_HOSTS = {"youtu.be", "www.youtu.be"}


def get_youtube_video_id(url: str) -> str | None:
    """Accept only genuine HTTPS YouTube URLs, never arbitrary hosts/redirects."""
    if not isinstance(url, str):
        return None
    try:
        parts = urlsplit(url.strip())
        if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
            return None
        if parts.port not in (None, 443):
            return None
        host = (parts.hostname or "").lower().rstrip(".")
        if host not in YOUTUBE_HOSTS | SHORT_HOSTS:
            return None
        if host in SHORT_HOSTS:
            candidate = parts.path.strip("/")
        elif parts.path == "/watch":
            candidate = parse_qs(parts.query).get("v", [""])[0]
        else:
            path_parts = parts.path.strip("/").split("/")
            candidate = (
                path_parts[1]
                if len(path_parts) == 2 and path_parts[0] in {"shorts", "embed", "live", "v"}
                else ""
            )
        return candidate if VIDEO_ID.fullmatch(candidate) else None
    except (ValueError, TypeError):
        return None


def canonical_youtube_url(url: str) -> str:
    video_id = get_youtube_video_id(url)
    if not video_id:
        raise ValueError("Enter a valid HTTPS YouTube video URL.")
    return f"https://www.youtube.com/watch?v={video_id}"


def get_youtube_thumbnail(url: str) -> str | None:
    video_id = get_youtube_video_id(url)
    return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None


def format_time_srt(seconds: float) -> str:
    """Round to the nearest millisecond, carrying across seconds/minutes."""
    try:
        value = float(seconds)
    except (ValueError, TypeError) as exc:
        raise ValueError("Timestamp must be numeric.") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError("Timestamp must be finite and non-negative.")
    milliseconds = int(math.floor(value * 1000 + 0.5))
    hours, remaining = divmod(milliseconds, 3_600_000)
    minutes, remaining = divmod(remaining, 60_000)
    whole_seconds, millis = divmod(remaining, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{millis:03}"
