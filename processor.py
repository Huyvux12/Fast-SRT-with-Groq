"""
Processor module - Main audio processing logic
"""

import os
import tempfile
import gradio as gr

from utils import get_youtube_video_id, get_youtube_thumbnail
from api import download_youtube_audio, transcribe_audio
from formatters import to_srt, to_txt, to_json


def update_thumbnail(url: str):
    """Cập nhật thumbnail khi URL thay đổi"""
    if not url or not url.strip():
        return None
    return get_youtube_thumbnail(url.strip())


def process_audio(
    api_key: str,
    youtube_url: str,
    audio_file,
    recorded_audio,
    output_format: str,
    language: str,
    progress=gr.Progress()
) -> tuple[str, str | None]:
    """
    Xử lý audio từ các nguồn khác nhau và tạo output
    Returns: (content_preview, download_file_path)
    """
    
    # Xác định nguồn audio
    audio_path = None
    source_name = "audio"
    
    if youtube_url and youtube_url.strip():
        progress(0.1, desc="Đang xử lý YouTube URL...")
        audio_path = download_youtube_audio(youtube_url.strip(), progress)
        source_name = get_youtube_video_id(youtube_url) or "youtube"
    elif audio_file is not None:
        audio_path = audio_file
        source_name = os.path.splitext(os.path.basename(audio_file))[0]
    elif recorded_audio is not None:
        audio_path = recorded_audio
        source_name = "recording"
    else:
        raise gr.Error("Vui lòng cung cấp audio (YouTube URL, upload file, hoặc ghi âm)")
    
    # Transcribe
    progress(0.3, desc="Đang transcribe...")
    result = transcribe_audio(audio_path, api_key, language, progress)
    
    segments = result["segments"]
    full_text = result["text"]
    detected_lang = result["language"]
    duration = result["duration"]
    
    # Format output
    progress(0.8, desc="Đang tạo output...")
    
    if output_format == "SRT":
        content = to_srt(segments)
        ext = ".srt"
    elif output_format == "TXT":
        content = to_txt(segments)
        ext = ".txt"
    elif output_format == "JSON":
        content = to_json(segments, full_text, detected_lang, duration)
        ext = ".json"
    else:
        content = to_srt(segments)
        ext = ".srt"
    
    # Lưu file
    output_filename = f"{source_name}_subtitle{ext}"
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    progress(1.0, desc="Hoàn tất!")
    
    return content, output_path
