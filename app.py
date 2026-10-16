"""Modern Gradio 6 interface for local, Colab and authenticated server use."""
import os

import gradio as gr

from api import test_api_key
from config import ALLOWED_EXTENSIONS, LANGUAGES, MODELS
from processor import process_audio, update_thumbnail

APP_CSS = """
.gradio-container { max-width: 1240px !important; margin: 0 auto !important; }
body { background: #080f1f !important; }
#hero { padding: 36px 38px; border-radius: 24px; background:
  radial-gradient(circle at 85% 18%, rgba(6,182,212,.32), transparent 39%),
  linear-gradient(125deg, #0c1631, #172955 55%, #0a1a2e);
  color: #f8fafc; border: 1px solid rgba(148,163,184,.2);
  box-shadow: 0 22px 60px rgba(2,6,23,.24); margin-bottom: 22px; }
#hero .eyebrow { font-size: .78rem; font-weight: 800; letter-spacing: .18em;
  color: #67e8f9; text-transform: uppercase; }
#hero h1 { font-size: clamp(2rem,4vw,3.1rem); line-height: 1.12; margin: 14px 0; color: white; }
#hero p { color: #cbd5e1; max-width: 670px; font-size: 1.08rem; }
#hero .hero-pills { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }
#hero .hero-pills span { display: inline-block; border: 1px solid #3c5474;
  background: rgba(9, 23, 49, .58); border-radius: 100px; color: #e2e8f0;
  font-size: .86rem; padding: 8px 14px; }
.section-lead { padding-top: 8px; }
.section-lead h2 { margin: 0 0 5px; }
.section-lead p { margin: 0 0 12px; opacity: .78; }
#main-generate { min-height: 52px; font-weight: 750; }
#key-status, #result-status { min-height: 34px; }
.thumb-placeholder { text-align: center; padding: 42px 16px;
  border: 1px dashed #64748b; border-radius: 16px; color: #94a3b8; }
.youtube-thumb { width: 100%; max-height: 268px; object-fit: contain;
  border-radius: 16px; background: #0c1631; }
#footer-note { text-align: center; opacity: .70; padding: 16px 0; }
"""

APP_THEME = gr.themes.Soft(primary_hue="cyan", secondary_hue="blue", neutral_hue="slate")


def select_source(source: str):
    return (
        gr.update(visible=source == "youtube"),
        gr.update(visible=source == "upload"),
        gr.update(visible=source == "microphone"),
    )


def create_ui() -> gr.Blocks:
    with gr.Blocks(title="Fast SRT Studio | Groq Whisper") as demo:
        gr.HTML("""
        <section id="hero">
          <div class="eyebrow">Fast SRT Studio · Powered by Groq</div>
          <h1>Your audio. Beautifully timed subtitles.</h1>
          <p>Turn YouTube videos, uploaded media and voice recordings into
          accurate, downloadable captions in just a few steps.</p>
          <div class="hero-pills">
            <span>⚡ Whisper large v3 &amp; turbo</span>
            <span>🎬 Video and audio</span>
            <span>🕒 Long media support</span>
            <span>🔒 Bring your own API key</span>
          </div>
        </section>
        """)

        with gr.Row(equal_height=False):
            with gr.Column(scale=7, min_width=370):
                gr.HTML('<div class="section-lead"><h2>01 / Choose your media</h2>'
                        '<p>Pick one source; only the selected source will be processed.</p></div>')
                source = gr.Radio(
                    choices=[
                        ("▶️ YouTube", "youtube"),
                        ("📂 Upload audio/video", "upload"),
                        ("🎙️ Microphone", "microphone"),
                    ],
                    value="youtube", label="Input source",
                )
                with gr.Group(visible=True) as youtube_panel:
                    youtube_url = gr.Textbox(
                        label="YouTube video URL",
                        placeholder="https://www.youtube.com/watch?v=...",
                    )
                    thumbnail = gr.HTML(update_thumbnail(""))
                    youtube_url.change(
                        update_thumbnail, inputs=youtube_url, outputs=thumbnail,
                        api_name=False,
                    )
                with gr.Group(visible=False) as upload_panel:
                    uploaded_file = gr.File(
                        label="Upload audio or video (max 300 MB / 3 hours)",
                        file_types=list(ALLOWED_EXTENSIONS),
                        type="filepath",
                    )
                    gr.Markdown("Supported: MP3, WAV, FLAC, MP4, MOV, WEBM, MKV and more.")
                with gr.Group(visible=False) as microphone_panel:
                    recorded_audio = gr.Audio(
                        label="Record from microphone",
                        sources=["microphone"], type="filepath",
                    )
                source.change(
                    select_source, inputs=source,
                    outputs=[youtube_panel, upload_panel, microphone_panel],
                    api_name=False,
                )

                gr.HTML('<div class="section-lead"><h2>02 / Customize recognition</h2>'
                        '<p>Turbo is the faster default; large v3 is available for tricky audio.</p></div>')
                with gr.Row():
                    model = gr.Dropdown(
                        choices=[
                            ("Whisper Large v3 Turbo · fast", MODELS[0]),
                            ("Whisper Large v3 · quality", MODELS[1]),
                        ],
                        value=MODELS[0], label="Whisper model",
                    )
                    language = gr.Dropdown(
                        choices=[(label, code) for code, label in LANGUAGES.items()],
                        value="auto", label="Spoken language",
                    )

                gr.HTML('<div class="section-lead"><h2>03 / Export captions</h2>'
                        '<p>Choose a format and generate your transcription.</p></div>')
                output_format = gr.Radio(
                    choices=["SRT", "TXT", "JSON"], value="SRT",
                    label="Output format",
                )
                generate = gr.Button(
                    "✨ Generate subtitles", variant="primary",
                    size="lg", elem_id="main-generate",
                )

            with gr.Column(scale=5, min_width=300):
                gr.HTML('<div class="section-lead"><h2>🔑 Groq connection</h2>'
                        '<p>Your key stays in this session and is not written to disk.</p></div>')
                api_key = gr.Textbox(
                    label="Groq API key", placeholder="gsk_...",
                    type="password",
                )
                verify = gr.Button("Verify API key", variant="secondary")
                key_status = gr.Markdown(elem_id="key-status")
                verify.click(
                    test_api_key, inputs=api_key, outputs=key_status,
                    api_name=False,
                )

                gr.HTML('<div class="section-lead"><h2>📄 Your result</h2>'
                        '<p>Preview your captions, then download the finished file.</p></div>')
                result_status = gr.Markdown(
                    "Your result will appear here.", elem_id="result-status"
                )
                output_preview = gr.Textbox(
                    label="Subtitle preview", lines=15, max_lines=22,
                    interactive=False, show_copy_button=True,
                )
                output_file = gr.File(label="Download subtitle file", interactive=False)

        generate.click(
            fn=process_audio,
            inputs=[
                api_key, youtube_url, uploaded_file, recorded_audio,
                source, language, model, output_format,
            ],
            outputs=[output_preview, output_file, result_status],
            api_name=False,
            concurrency_limit=2,
            show_progress="full",
        )
        gr.HTML(
            '<div id="footer-note">Fast SRT Studio · Python + Gradio + Groq · '
            'FFmpeg runs locally · '
            '<a href="https://console.groq.com/keys" target="_blank" '
            'rel="noopener noreferrer">Get your Groq API key ↗</a></div>'
        )

    return demo.queue(max_size=8, default_concurrency_limit=2)


def launch_app(share: bool = False) -> None:
    username = os.getenv("APP_AUTH_USER")
    password = os.getenv("APP_AUTH_PASSWORD")
    if bool(username) != bool(password):
        raise RuntimeError("Set both APP_AUTH_USER and APP_AUTH_PASSWORD, or neither.")
    auth = (username, password) if username and password else None
    create_ui().launch(
        share=share,
        server_name=os.getenv("APP_HOST", "127.0.0.1"),
        server_port=int(os.getenv("PORT", "7860")),
        css=APP_CSS,
        theme=APP_THEME,
        max_file_size="300mb",
        show_error=False,
        auth=auth,
    )


if __name__ == "__main__":
    launch_app(share=os.getenv("APP_SHARE", "false").lower() == "true")
