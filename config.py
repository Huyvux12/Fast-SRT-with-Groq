"""Application settings kept in one place."""
from pathlib import Path
import tempfile

MODELS = ("whisper-large-v3-turbo", "whisper-large-v3")
LANGUAGES = {
    "auto": "Auto detect",
    "vi": "Vietnamese",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "ru": "Russian",
    "th": "Thai",
}
OUTPUT_FORMATS = ("SRT", "TXT", "JSON")
ALLOWED_EXTENSIONS = (
    ".mp3", ".wav", ".m4a", ".mp4", ".mpeg", ".mpga", ".ogg",
    ".flac", ".webm", ".mov", ".mkv", ".avi", ".aac", ".wma",
)
MAX_UPLOAD_BYTES = 300 * 1024 * 1024
MAX_DURATION_SECONDS = 3 * 60 * 60
CHUNK_SECONDS = 10 * 60
# Leave headroom under Groq's 25 MB free-tier upload limit.
MAX_CHUNK_BYTES = 20 * 1024 * 1024
OUTPUT_DIR = Path(tempfile.gettempdir()) / "fast-srt-groq-outputs"
OUTPUT_TTL_SECONDS = 24 * 60 * 60
