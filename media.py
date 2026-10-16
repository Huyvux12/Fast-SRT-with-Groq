"""Bounded local media processing and secure YouTube downloads."""
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yt_dlp

from config import (
    ALLOWED_EXTENSIONS,
    CHUNK_SECONDS,
    MAX_CHUNK_BYTES,
    MAX_DURATION_SECONDS,
    MAX_UPLOAD_BYTES,
)
from utils import canonical_youtube_url


@dataclass(frozen=True)
class AudioChunk:
    path: str
    offset: float
    duration: float


def require_ffmpeg() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise ValueError("ffmpeg and ffprobe are required. See the README installation guide.")


def probe_duration(path: str) -> float:
    require_ffmpeg()
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=duration", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", path,
            ],
            check=True, capture_output=True, text=True, timeout=30,
        )
        durations = []
        for line in result.stdout.splitlines():
            try:
                number = float(line)
                if math.isfinite(number) and number > 0:
                    durations.append(number)
            except ValueError:
                pass
        if not durations:
            raise ValueError("No readable audio track found.")
        return max(durations)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Cannot read the file's audio track (ffprobe failed).") from exc


def validate_media(path: str) -> tuple[Path, float]:
    candidate = Path(path)
    if not candidate.is_file():
        raise ValueError("Upload a valid audio or video file.")
    if candidate.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file extension.")
    if candidate.stat().st_size > MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds the 300 MB upload limit.")
    duration = probe_duration(str(candidate))
    if duration > MAX_DURATION_SECONDS:
        raise ValueError("Recording exceeds the three-hour limit.")
    return candidate, duration


def download_youtube_audio(url: str, directory: str) -> str:
    """Canonicalize input before yt-dlp touches the network; download only one video."""
    require_ffmpeg()
    safe_url = canonical_youtube_url(url)
    output_dir = Path(directory)
    options = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "youtube.%(ext)s"),
        "noplaylist": True,
        "max_downloads": 1,
        "max_filesize": MAX_UPLOAD_BYTES,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            metadata = downloader.extract_info(safe_url, download=False)
            if not metadata or not metadata.get("duration"):
                raise ValueError("Could not determine YouTube video length.")
            if float(metadata["duration"]) > MAX_DURATION_SECONDS:
                raise ValueError("YouTube video exceeds the three-hour limit.")
            info = downloader.extract_info(safe_url, download=True)
            path = Path(downloader.prepare_filename(info))
        if not path.is_file():
            matches = sorted(output_dir.glob("youtube.*"))
            if not matches:
                raise ValueError("YouTube audio file was not produced.")
            path = matches[0]
        if path.stat().st_size > MAX_UPLOAD_BYTES:
            raise ValueError("Downloaded file is too large.")
        return str(path)
    except yt_dlp.utils.DownloadError as exc:
        raise ValueError(
            "YouTube download failed. Video may be private, geo-blocked or unavailable."
        ) from exc


def prepare_chunks(media_path: str, directory: str) -> tuple[list[AudioChunk], float]:
    """Convert to 16 kHz mono MP3; each 10-minute chunk is well under 25 MB."""
    path, duration = validate_media(media_path)
    chunks = []
    for index in range(math.ceil(duration / CHUNK_SECONDS)):
        start = index * CHUNK_SECONDS
        length = min(CHUNK_SECONDS, duration - start)
        out = Path(directory) / f"audio_chunk_{index:04d}.mp3"
        command = [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-y", "-ss", str(start), "-i", str(path), "-t", str(length),
            "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "libmp3lame", "-b:a", "48k", str(out),
        ]
        try:
            subprocess.run(
                command, check=True, capture_output=True, text=True,
                timeout=max(120, int(length * 3)),
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ValueError("Audio conversion failed. Check that ffmpeg supports this file.") from exc
        if not out.is_file() or out.stat().st_size == 0:
            raise ValueError("Audio conversion produced an empty chunk.")
        if out.stat().st_size > MAX_CHUNK_BYTES:
            raise ValueError("Converted chunk exceeds the Groq upload safety limit.")
        chunks.append(AudioChunk(str(out), float(start), float(length)))
    return chunks, duration
