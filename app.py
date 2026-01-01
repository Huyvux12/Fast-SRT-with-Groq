"""
SRT Generator Pro - Main Application
Giao diện Gradio cho tool tạo phụ đề
"""

import gradio as gr
from api import test_api_key
from processor import process_audio, update_thumbnail


# ============== CONSTANTS ==============

LANGUAGES = {
    "auto": "🌐 Tự động nhận diện",
    "vi": "🇻🇳 Tiếng Việt",
    "en": "🇺🇸 English",
    "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어",
    "zh": "🇨🇳 中文",
    "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch",
    "es": "🇪🇸 Español",
    "pt": "🇵🇹 Português",
    "ru": "🇷🇺 Русский",
    "th": "🇹🇭 ไทย",
}

CUSTOM_CSS = """
.api-status-ok { color: #22c55e; font-weight: bold; }
.api-status-error { color: #ef4444; font-weight: bold; }
.api-status-warning { color: #f97316; font-weight: bold; }
.main-title { text-align: center; margin-bottom: 1rem; }
.subtitle { text-align: center; color: #6b7280; margin-bottom: 2rem; }
"""


# ============== UI COMPONENTS ==============

def create_ui():
    with gr.Blocks(
        title="SRT Generator Pro",
    ) as demo:
        
        # Header
        gr.Markdown("# 🎬 SRT Generator Pro", elem_classes="main-title")
        gr.Markdown(
            "Tạo phụ đề từ video/audio sử dụng Groq Whisper API",
            elem_classes="subtitle"
        )
        
        # API Key Section
        with gr.Group():
            gr.Markdown("### 🔑 API Configuration")
            with gr.Row():
                api_key_input = gr.Textbox(
                    label="Groq API Key",
                    placeholder="Nhập API key của bạn (gsk_...)",
                    type="password",
                    scale=4,
                )
                test_api_btn = gr.Button("🔍 Kiểm tra API", scale=1)
            api_status = gr.Markdown("", elem_id="api-status")
        
        gr.Markdown("---")
        
        # Input Section với Tabs
        gr.Markdown("### 📥 Nguồn Audio")
        
        with gr.Tabs() as input_tabs:
            # Tab 1: YouTube
            with gr.TabItem("🎬 YouTube", id="youtube"):
                youtube_url = gr.Textbox(
                    label="YouTube URL",
                    placeholder="https://www.youtube.com/watch?v=... hoặc https://youtu.be/...",
                )
                youtube_thumbnail = gr.Image(
                    label="Thumbnail Preview",
                    type="filepath",
                    interactive=False,
                    height=200,
                )
            
            # Tab 2: Upload Audio
            with gr.TabItem("📁 Upload File", id="upload"):
                audio_file = gr.Audio(
                    label="Upload Audio/Video",
                    type="filepath",
                    sources=["upload"],
                )
            
            # Tab 3: Record
            with gr.TabItem("🎙️ Ghi âm", id="record"):
                recorded_audio = gr.Audio(
                    label="Ghi âm từ Microphone",
                    type="filepath",
                    sources=["microphone"],
                )
        
        gr.Markdown("---")
        
        # Output Settings
        gr.Markdown("### ⚙️ Cài đặt Output")
        
        with gr.Row():
            output_format = gr.Dropdown(
                label="Định dạng xuất",
                choices=["SRT", "TXT", "JSON"],
                value="SRT",
                scale=1,
            )
            language_select = gr.Dropdown(
                label="Ngôn ngữ",
                choices=list(LANGUAGES.keys()),
                value="auto",
                scale=1,
            )
        
        # Generate Button
        generate_btn = gr.Button(
            "🚀 Tạo Phụ Đề",
            variant="primary",
            size="lg",
        )
        
        gr.Markdown("---")
        
        # Output Section
        gr.Markdown("### 📤 Kết quả")
        
        output_preview = gr.Textbox(
            label="Preview",
            lines=15,
            max_lines=20,
            interactive=False,
        )
        
        output_file = gr.File(label="📥 Tải file", interactive=False)
        
        # Footer
        gr.Markdown("---")
        gr.Markdown(
            """
            <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
                <p>💡 <strong>Tips:</strong> Lấy API key miễn phí tại 
                <a href="https://console.groq.com/keys" target="_blank">console.groq.com</a></p>
                <p>SRT Generator Pro v1.0 | Powered by Groq Whisper API</p>
            </div>
            """,
            elem_id="footer"
        )
        
        # ============== EVENT HANDLERS ==============
        
        test_api_btn.click(
            fn=test_api_key,
            inputs=[api_key_input],
            outputs=[api_status],
        )
        
        youtube_url.change(
            fn=update_thumbnail,
            inputs=[youtube_url],
            outputs=[youtube_thumbnail],
        )
        
        generate_btn.click(
            fn=process_audio,
            inputs=[
                api_key_input,
                youtube_url,
                audio_file,
                recorded_audio,
                output_format,
                language_select,
            ],
            outputs=[output_preview, output_file],
        )
    
    return demo


# ============== MAIN ==============

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="blue",
        ),
    )
