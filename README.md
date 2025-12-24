# 🎬 SRT Subtitle Generator

Tạo file phụ đề SRT từ audio/video sử dụng **Groq Whisper API** với giao diện **Gradio**.

## ✨ Tính năng

- ⚡ **Nhanh hơn 189x** so với GPU truyền thống (real-time speed factor)
- 🚀 Transcription cực nhanh với Groq Whisper
- 🌐 Hỗ trợ 30+ ngôn ngữ + Auto Detect
- 📁 Hỗ trợ MP3, MP4, M4A, WAV, WEBM, OGG, FLAC
- 🎨 Giao diện web đẹp với Gradio
- 📓 Notebook cho Google Colab & Local

## 🛠️ Cài đặt

### Local

```bash
# Clone repo
cd srtgqoq

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình API key
# Cách 1: Tạo file .env
cp .env.example .env
# Sửa file .env và thêm API key

# Cách 2: Set environment variable
set GROQ_API_KEY=your_api_key_here
```

### Google Colab

Mở file `srt_generator.ipynb` trong Google Colab và chạy các cell theo thứ tự.

## 🚀 Sử dụng

### Web UI

```bash
python app.py
```

Mở browser tại `http://localhost:7860`

### Command Line

```bash
python srt_generator.py audio.mp3 vi
```

### Notebook

Mở `srt_generator.ipynb` và chạy các cell.

## 🔑 API Key

Lấy API key miễn phí tại: https://console.groq.com/keys

## 📋 Models

| Model | Tốc độ | Giá | Ghi chú |
|-------|--------|-----|---------|
| whisper-large-v3-turbo | Nhanh hơn | $0.04/h | Khuyên dùng |
| whisper-large-v3 | Chậm hơn | $0.111/h | Chính xác hơn |

## 📝 License

MIT
