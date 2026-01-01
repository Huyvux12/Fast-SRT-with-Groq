"""
API module - Functions for Groq API interactions
"""

import os
import tempfile
import gradio as gr
from groq import Groq

from utils import get_youtube_video_id


def test_api_key(api_key: str) -> str:
    """
    Kiểm tra API key có hợp lệ không
    Returns: status_message string
    """
    if not api_key or not api_key.strip():
        return "❌ Vui lòng nhập API key"
    
    try:
        client = Groq(api_key=api_key.strip())
        client.models.list()
        return "✅ API key hợp lệ và hoạt động!"
    except Exception as e:
        error_msg = str(e)
        if "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "❌ API key không hợp lệ"
        elif "rate_limit" in error_msg.lower():
            return "⚠️ API key hợp lệ nhưng đã hết quota"
        else:
            return f"❌ Lỗi: {error_msg[:100]}"


def download_youtube_audio(url: str, progress=gr.Progress()) -> str | None:
    """Tải audio từ YouTube sử dụng yt-dlp"""
    try:
        import yt_dlp
        
        video_id = get_youtube_video_id(url)
        if not video_id:
            raise gr.Error("URL YouTube không hợp lệ")
        
        progress(0.1, desc="Đang chuẩn bị tải...")
        
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"{video_id}.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(temp_dir, f"{video_id}.%(ext)s"),
            'quiet': True,
            'no_warnings': True,
        }
        
        progress(0.3, desc="Đang tải audio từ YouTube...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        progress(0.9, desc="Hoàn tất tải audio!")
        
        if os.path.exists(output_path):
            return output_path
        
        for f in os.listdir(temp_dir):
            if f.endswith('.mp3'):
                return os.path.join(temp_dir, f)
        
        raise gr.Error("Không tìm thấy file audio sau khi tải")
        
    except ImportError:
        raise gr.Error("Vui lòng cài đặt yt-dlp: pip install yt-dlp")
    except Exception as e:
        raise gr.Error(f"Lỗi tải YouTube: {str(e)}")


def transcribe_audio(
    audio_path: str,
    api_key: str,
    language: str = "auto",
    progress=gr.Progress()
) -> dict:
    """
    Transcribe audio sử dụng Groq Whisper API
    Returns: dict với segments và text đầy đủ
    """
    if not api_key:
        raise gr.Error("Vui lòng nhập API key")
    
    if not audio_path or not os.path.exists(audio_path):
        raise gr.Error("Không tìm thấy file audio")
    
    progress(0.2, desc="Đang kết nối với Groq API...")
    
    try:
        client = Groq(api_key=api_key.strip())
        
        progress(0.4, desc="Đang transcribe audio...")
        
        with open(audio_path, "rb") as audio_file:
            params = {
                "file": (os.path.basename(audio_path), audio_file.read()),
                "model": "whisper-large-v3",
                "response_format": "verbose_json",
            }
            
            if language and language != "auto":
                params["language"] = language
            
            transcription = client.audio.transcriptions.create(**params)
        
        progress(0.9, desc="Hoàn tất transcribe!")
        
        return {
            "segments": transcription.segments,
            "text": transcription.text,
            "language": getattr(transcription, 'language', language),
            "duration": getattr(transcription, 'duration', None),
        }
        
    except Exception as e:
        raise gr.Error(f"Lỗi Groq API: {str(e)}")
