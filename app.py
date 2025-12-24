"""
SRT Generator Web UI using Gradio

A web interface for generating SRT subtitles from audio/video files using Groq Whisper API.
"""

import os
import tempfile
import gradio as gr
from srt_generator import (
    generate_srt,
    save_srt,
    SUPPORTED_LANGUAGES,
    AVAILABLE_MODELS,
)


def process_audio(
    audio_file,
    model: str,
    language: str,
    prompt: str,
    api_key: str,
):
    """
    Process audio file and generate SRT subtitle.
    
    Returns:
        Tuple of (srt_content, srt_file_path, status_message)
    """
    if audio_file is None:
        return "", None, "⚠️ Vui lòng upload file audio/video"
    
    # Get API key from input or environment
    key = api_key.strip() if api_key else os.environ.get("GROQ_API_KEY", "")
    if not key:
        return "", None, "⚠️ Vui lòng nhập Groq API Key hoặc set GROQ_API_KEY environment variable"
    
    # Get language code from selection
    lang_code = SUPPORTED_LANGUAGES.get(language, "")
    
    try:
        # Generate SRT
        srt_content, full_text = generate_srt(
            filepath=audio_file,
            model=model,
            language=lang_code,
            prompt=prompt,
            api_key=key,
        )
        
        # Save to temp file for download
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        temp_dir = tempfile.gettempdir()
        srt_path = os.path.join(temp_dir, f"{base_name}.srt")
        save_srt(srt_content, srt_path)
        
        return srt_content, srt_path, f"✅ Đã tạo phụ đề thành công! ({len(srt_content.splitlines())} dòng)"
    
    except Exception as e:
        return "", None, f"❌ Lỗi: {str(e)}"


# Custom CSS for better UI
custom_css = """
.gradio-container {
    max-width: 1200px !important;
}
.output-textbox textarea {
    font-family: 'Consolas', 'Monaco', monospace !important;
    font-size: 14px !important;
}
"""

# Build Gradio interface
with gr.Blocks(
    title="SRT Generator - Groq Whisper",
    css=custom_css,
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
    ),
) as app:
    
    gr.Markdown(
        """
        # 🎬 SRT Subtitle Generator
        ### Tạo phụ đề từ audio/video sử dụng Groq Whisper API
        
        Upload file audio hoặc video, chọn ngôn ngữ và nhấn **Generate** để tạo file phụ đề SRT.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input section
            audio_input = gr.Audio(
                label="📁 Upload Audio/Video",
                type="filepath",
                sources=["upload"],
            )
            
            model_dropdown = gr.Dropdown(
                label="🤖 Model",
                choices=AVAILABLE_MODELS,
                value="whisper-large-v3-turbo",
                info="turbo: nhanh hơn, rẻ hơn | v3: chính xác hơn",
            )
            
            language_dropdown = gr.Dropdown(
                label="🌐 Ngôn ngữ",
                choices=list(SUPPORTED_LANGUAGES.keys()),
                value="Auto Detect",
                info="Chọn ngôn ngữ của audio hoặc để Auto Detect",
            )
            
            prompt_input = gr.Textbox(
                label="📝 Prompt (Tùy chọn)",
                placeholder="Nhập context hoặc cách viết từ đặc biệt...",
                lines=2,
            )
            
            api_key_input = gr.Textbox(
                label="🔑 Groq API Key",
                placeholder="Nhập API key hoặc để trống nếu đã set GROQ_API_KEY",
                type="password",
            )
            
            generate_btn = gr.Button(
                "🚀 Generate SRT",
                variant="primary",
                size="lg",
            )
        
        with gr.Column(scale=1):
            # Output section
            status_output = gr.Textbox(
                label="📊 Trạng thái",
                interactive=False,
            )
            
            srt_output = gr.Textbox(
                label="📄 Nội dung SRT",
                lines=15,
                max_lines=25,
                show_copy_button=True,
                elem_classes=["output-textbox"],
            )
            
            download_output = gr.File(
                label="⬇️ Download SRT",
            )
    
    # Event handler
    generate_btn.click(
        fn=process_audio,
        inputs=[
            audio_input,
            model_dropdown,
            language_dropdown,
            prompt_input,
            api_key_input,
        ],
        outputs=[srt_output, download_output, status_output],
    )
    
    # Footer
    gr.Markdown(
        """
        ---
        💡 **Tips:**
        - Hỗ trợ định dạng: MP3, MP4, M4A, WAV, WEBM, OGG, FLAC
        - Kích thước tối đa: 25MB (free tier) / 100MB (dev tier)
        - Lấy API key tại: [console.groq.com](https://console.groq.com)
        """
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
