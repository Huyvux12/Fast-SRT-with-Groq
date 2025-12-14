# 🚀 Groq-SRT-Generator

Tạo file phụ đề `.srt` **siêu nhanh** bằng cách sử dụng sức mạnh xử lý ngôn ngữ tự nhiên (NLP) của Groq API.

## ✨ Tính năng

* Chuyển đổi văn bản/kịch bản thành định dạng SRT chính xác về thời gian (dựa trên đầu vào của người dùng).
* Sử dụng API Groq để xử lý tác vụ NLP/Phân tích định dạng nhanh chóng.
* Dễ dàng tích hợp vào quy trình làm việc video.

## ⚙️ Cài đặt

1.  **Clone repository:**
    ```bash
    git clone [https://github.com/YourUsername/Groq-SRT-Generator.git](https://github.com/YourUsername/Groq-SRT-Generator.git)
    cd Groq-SRT-Generator
    ```

2.  **Cài đặt các thư viện cần thiết** (Cần có Python. Thêm các thư viện sau khi bạn xác định chúng, ví dụ: `pip install groq python-dotenv`):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Thiết lập Khóa API Groq**

    Tạo một file `.env` trong thư mục gốc và thêm khóa API của bạn:
    ```
    GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"
    ```

## 📝 Cách Sử dụng

Chạy script chính (Giả sử script của bạn tên là `generate_srt.py`):

```bash
python generate_srt.py --input "Đường dẫn đến file văn bản/dữ liệu đầu vào"
# Ví dụ: python generate_srt.py --input script.txt --output video_subtitles.srt
