# Fast SRT Studio — Groq Whisper Subtitle Generator

A redesigned, BYOK (bring-your-own-key) Gradio 6 app that creates SRT, TXT or JSON captions from YouTube, uploaded audio/video or your microphone.

## Highlights

- Clean, responsive studio UI with explicit input selection and live YouTube thumbnails.
- Whisper Large v3 Turbo or Large v3, automatic language detection and language selection.
- YouTube URLs canonicalized and validated before passing to yt-dlp; one video per request.
- Videos and recordings converted to 16 kHz mono MP3 with FFmpeg.
- Up to **300 MB input** and **3 hours** of media; chunked at **10 minutes** to keep requests far below the Groq free-tier file-size limit.
- Per-chunk timestamps shifted back onto the original timeline.
- UTF-8 SRT, TXT and JSON exports with downloadable files.
- Groq keys entered in the browser; never saved to local files or source control.
- Automatic removal of output files older than 24 hours when a new job completes.
- Docker, Colab and GitHub Actions support.

## Requirements

- Python **3.10 or newer** (3.11 or 3.12 recommended).
- FFmpeg and FFprobe available on PATH.
- A Groq API key from https://console.groq.com/keys.

Install FFmpeg:

~~~bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg
# macOS / Homebrew
brew install ffmpeg
# Windows / Chocolatey (Administrator)
choco install ffmpeg
~~~

## Run locally

~~~bash
git clone https://github.com/Huyvux12/Fast-SRT-with-Groq.git
cd Fast-SRT-with-Groq
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
~~~

Open http://127.0.0.1:7860

Choose your source, enter your Groq API key, select a model/language and click **Generate subtitles**. Longer files are handled automatically. You do not need a GPU: the actual speech recognition runs on Groq.

## Google Colab

Open [the Colab notebook](https://colab.research.google.com/github/Huyvux12/Fast-SRT-with-Groq/blob/feat/full-stack-srt-overhaul-20261016/colab.ipynb). The notebook creates a temporary share link.

Important: do not paste your API key into notebook cells or share a public app session with keys already entered.

## Docker

~~~bash
docker build -t fast-srt-groq .
docker run --rm -p 127.0.0.1:7860:7860 fast-srt-groq
~~~

The Docker container listens on 0.0.0.0 internally so the local port mapping works. For a public deployment, use HTTPS and access control.

~~~bash
docker run --rm -p 7860:7860 \
  -e APP_AUTH_USER=your-user \
  -e APP_AUTH_PASSWORD=replace-with-a-strong-secret \
  fast-srt-groq
~~~

If publicly deployed, put it behind HTTPS and additional rate limiting. Never commit secrets. Set both authentication variables or neither. On an exposed server, you may use APP_HOST=0.0.0.0 and PORT=7860. By default the local Python app binds only to 127.0.0.1.

## Formats

- **SRT**: numbered captions with precise start/end timestamps.
- **TXT**: readable transcription, one subtitle segment per line.
- **JSON**: language, duration, full_text, and segment timing/text.

## Operational limits & privacy

- This is a BYOK tool: the API key is transferred from your browser to the running Gradio server and then to Groq. **Only run it on infrastructure you trust.**
- No key is intentionally stored in the app's result files. The app has no account database or persistent key store.
- Audio is sent to Groq for transcription. See Groq's privacy policy for processing/retention terms.
- Input files may be temporarily cached by Gradio; downloaded/converted working media is deleted after each request. Downloadable output files expire on subsequent jobs after 24 hours.
- YouTube age restrictions, geo restrictions and anti-bot protections can prevent downloading.
- Extremely long or noisy audio may need manual caption review, especially at chunk boundaries.
- Each chunk consumes Groq API usage; account rate limits and provider quotas still apply.
- FFmpeg is required for **all sources**, not only YouTube.

## Test

~~~bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
~~~

Offline unit tests mock the network calls. GitHub Actions runs the tests on Python 3.10 and 3.12.

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| FFmpeg/ffprobe missing | Install FFmpeg and confirm both executables are on PATH. |
| YouTube download failed | Check availability, use a direct HTTPS video URL, update yt-dlp. |
| Groq 401 / rate limit | Verify the key, then check account limits in Groq Console. |
| Nothing recognized | Confirm the media contains audible speech and has an audio track. |
| Upload rejected | Input must be a supported media format, at most 300 MB and at most 3 hours. |
| Public deployment | Add HTTPS, password protection and rate limiting before exposing. |

## License

MIT — see [LICENSE](LICENSE).
