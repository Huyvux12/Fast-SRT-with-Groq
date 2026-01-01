# SRT Generator Pro

Tool tạo phụ đề cải tiến sử dụng Groq Whisper API với giao diện Gradio thân thiện.

## Tính năng

- **API Key Management**: Nhập trực tiếp API key + kiểm tra hoạt động ngay
- **YouTube Input**: Paste link YouTube, hiển thị thumbnail, tải audio tự động
- **Audio Upload**: Hỗ trợ upload file audio/video
- **Microphone Recording**: Ghi âm trực tiếp từ browser
- **Multi-format Output**: SRT, TXT, JSON
- **Multi-language**: Tự động nhận diện hoặc chọn ngôn ngữ cụ thể

## Cài đặt

### Yêu cầu

- Python 3.9+
- ffmpeg (cần cho tính năng YouTube)

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Cài đặt ffmpeg (nếu chưa có)

**Windows (Chocolatey):**
```bash
choco install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Sử dụng

### Chạy ứng dụng

```bash
python app.py
```

Mở browser tại: http://localhost:7860

### Lấy API Key

1. Truy cập https://console.groq.com/keys
2. Đăng nhập/Đăng ký tài khoản
3. Tạo API key mới
4. Copy và paste vào ô "Groq API Key" trong app

### Google Colab

Mở file `colab.ipynb` hoặc click badge bên dưới:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/srt-gen-pro/blob/main/colab.ipynb)

## Định dạng Output

### SRT
```srt
1
00:00:00,000 --> 00:00:02,500
Xin chào mọi người

2
00:00:02,500 --> 00:00:05,000
Hôm nay chúng ta sẽ học...
```

### TXT
```
Xin chào mọi người
Hôm nay chúng ta sẽ học...
```

### JSON
```json
{
  "language": "vi",
  "duration": 120.5,
  "full_text": "Xin chào mọi người...",
  "segments": [
    {"id": 1, "start": 0.0, "end": 2.5, "text": "Xin chào mọi người"}
  ]
}
```

## Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| API key không hoạt động | Kiểm tra key đúng format `gsk_...` |
| Lỗi tải YouTube | Cài đặt/cập nhật ffmpeg |
| Lỗi "No audio" | Kiểm tra file audio hợp lệ |

## License

MIT License
