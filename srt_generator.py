"""
SRT Generator using Groq Whisper API

This module provides functions to transcribe audio files and generate SRT subtitles.
"""

import os
from groq import Groq

# Whisper supported languages with ISO 639-1 codes
SUPPORTED_LANGUAGES = {
    "Auto Detect": "",
    "English": "en",
    "Vietnamese": "vi",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Arabic": "ar",
    "Hindi": "hi",
    "Thai": "th",
    "Indonesian": "id",
    "Malay": "ms",
    "Turkish": "tr",
    "Polish": "pl",
    "Ukrainian": "uk",
    "Dutch": "nl",
    "Swedish": "sv",
    "Norwegian": "no",
    "Danish": "da",
    "Finnish": "fi",
    "Greek": "el",
    "Hebrew": "he",
    "Czech": "cs",
    "Romanian": "ro",
    "Hungarian": "hu",
    "Filipino": "tl",
}

AVAILABLE_MODELS = [
    "whisper-large-v3-turbo",
    "whisper-large-v3",
]


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe_audio(
    filepath: str,
    model: str = "whisper-large-v3-turbo",
    language: str = "",
    prompt: str = "",
    api_key: str = None,
) -> dict:
    """
    Transcribe audio file using Groq Whisper API.
    
    Args:
        filepath: Path to audio file
        model: Whisper model to use
        language: ISO 639-1 language code (empty for auto-detect)
        prompt: Optional prompt for context/spelling
        api_key: Groq API key (uses GROQ_API_KEY env var if not provided)
    
    Returns:
        Transcription response with segments and timestamps
    """
    if api_key:
        client = Groq(api_key=api_key)
    else:
        client = Groq()
    
    with open(filepath, "rb") as file:
        params = {
            "file": (os.path.basename(filepath), file.read()),
            "model": model,
            "response_format": "verbose_json",
            "timestamp_granularities": ["segment"],
            "temperature": 0,
        }
        
        if language:
            params["language"] = language
        if prompt:
            params["prompt"] = prompt
        
        transcription = client.audio.transcriptions.create(**params)
    
    return transcription


def segments_to_srt(segments: list) -> str:
    """
    Convert transcription segments to SRT format.
    
    Args:
        segments: List of segment objects with start, end, and text
    
    Returns:
        SRT formatted string
    """
    srt_lines = []
    
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment.get("start", 0))
        end_time = format_timestamp(segment.get("end", 0))
        text = segment.get("text", "").strip()
        
        srt_lines.append(f"{i}")
        srt_lines.append(f"{start_time} --> {end_time}")
        srt_lines.append(text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)


def generate_srt(
    filepath: str,
    model: str = "whisper-large-v3-turbo",
    language: str = "",
    prompt: str = "",
    api_key: str = None,
) -> tuple[str, str]:
    """
    Generate SRT content from audio file.
    
    Args:
        filepath: Path to audio file
        model: Whisper model to use
        language: ISO 639-1 language code
        prompt: Optional context prompt
        api_key: Groq API key
    
    Returns:
        Tuple of (srt_content, full_text)
    """
    transcription = transcribe_audio(
        filepath=filepath,
        model=model,
        language=language,
        prompt=prompt,
        api_key=api_key,
    )
    
    # Get segments from response
    segments = []
    if hasattr(transcription, "segments"):
        segments = transcription.segments
    elif isinstance(transcription, dict) and "segments" in transcription:
        segments = transcription["segments"]
    
    # Convert segments to list of dicts if needed
    segment_list = []
    for seg in segments:
        if hasattr(seg, "start"):
            segment_list.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
            })
        else:
            segment_list.append(seg)
    
    srt_content = segments_to_srt(segment_list)
    full_text = transcription.text if hasattr(transcription, "text") else ""
    
    return srt_content, full_text


def save_srt(srt_content: str, output_path: str) -> str:
    """
    Save SRT content to file.
    
    Args:
        srt_content: SRT formatted string
        output_path: Path to save the SRT file
    
    Returns:
        Path to saved file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return output_path


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python srt_generator.py <audio_file> [language]")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"Transcribing: {audio_file}")
    srt, text = generate_srt(audio_file, language=lang)
    
    output_file = os.path.splitext(audio_file)[0] + ".srt"
    save_srt(srt, output_file)
    print(f"Saved: {output_file}")
