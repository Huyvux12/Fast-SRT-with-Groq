"""Groq Whisper client: no API keys persisted and no raw secrets in errors."""
from pathlib import Path

from groq import Groq, RateLimitError, AuthenticationError, APIConnectionError, APIStatusError

from config import MODELS
from formatters import normalize_segments


def _client(api_key: str) -> Groq:
    return Groq(api_key=api_key.strip(), max_retries=2, timeout=180.0)


def test_api_key(api_key: str) -> str:
    if not api_key or not api_key.strip():
        return "⚠️ Enter a Groq API key first."
    try:
        _client(api_key).models.list()
        return "✅ API key verified. Ready to transcribe."
    except AuthenticationError:
        return "❌ Invalid or expired API key."
    except RateLimitError:
        return "⚠️ Groq rate limit reached. Try again later."
    except (APIConnectionError, APIStatusError):
        return "❌ Unable to verify the key. Check network and Groq status."
    except Exception:
        return "❌ API key check failed. Please try again."


def transcribe_audio(
    audio_path: str,
    api_key: str,
    language: str = "auto",
    model: str = "whisper-large-v3-turbo",
) -> dict:
    if model not in MODELS:
        raise ValueError("Unsupported transcription model.")
    path = Path(audio_path)
    if not path.is_file():
        raise ValueError("Audio chunk was not found.")
    if not api_key or not api_key.strip():
        raise ValueError("Please enter your Groq API key.")

    params = {
        "model": model,
        "response_format": "verbose_json",
        "timestamp_granularities": ["segment"],
    }
    if language and language != "auto":
        params["language"] = language

    try:
        # Pass the file handle to the SDK rather than loading the entire file into RAM.
        with path.open("rb") as audio_file:
            response = _client(api_key).audio.transcriptions.create(
                file=(path.name, audio_file), **params
            )
    except AuthenticationError as exc:
        raise ValueError("Groq rejected the API key.") from exc
    except RateLimitError as exc:
        raise ValueError("Groq rate limit exceeded. Please retry later.") from exc
    except APIConnectionError as exc:
        raise ValueError("Unable to connect to Groq. Check your internet connection.") from exc
    except APIStatusError as exc:
        raise ValueError(f"Groq API returned HTTP {exc.status_code}.") from exc

    return {
        "segments": normalize_segments(getattr(response, "segments", []) or []),
        "text": getattr(response, "text", "") or "",
        "language": getattr(response, "language", None) or language,
        "duration": getattr(response, "duration", None),
    }
