import json
from pathlib import Path

import pytest

import processor
from media import AudioChunk


def no_progress(*args, **kwargs):
    pass


def test_upload_pipeline_uses_selected_input_and_correct_chunk_offset(
    tmp_path, monkeypatch
):
    upload = tmp_path / "my audio.mp3"
    upload.write_bytes(b"mock")
    monkeypatch.setattr(processor, "OUTPUT_DIR", tmp_path / "output")

    def fake_chunks(path, directory):
        assert path == str(upload)
        return (
            [
                AudioChunk(str(upload), offset=0.0, duration=600.0),
                AudioChunk(str(upload), offset=600.0, duration=1.0),
            ],
            601.0,
        )

    responses = iter([
        {"segments": [{"start": 1, "end": 2, "text": "Hello"}], "language": "en"},
        {"segments": [{"start": 0.5, "end": 1, "text": "world"}], "language": "en"},
    ])
    monkeypatch.setattr(processor, "prepare_chunks", fake_chunks)
    monkeypatch.setattr(processor, "transcribe_audio", lambda *a: next(responses))

    content, output_path, summary = processor.process_audio(
        "test-key",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        str(upload),
        None,
        "upload",
        "auto",
        "whisper-large-v3-turbo",
        "JSON",
        progress=no_progress,
    )
    output = json.loads(content)
    assert output["segments"][0]["start"] == 1.0
    assert output["segments"][1]["start"] == 600.5
    assert output["duration"] == 601.0
    assert output["language"] == "en"
    assert Path(output_path).is_file()
    assert "2 subtitle segments" in summary


def test_cannot_download_before_entering_key(monkeypatch):
    monkeypatch.setattr(
        processor,
        "download_youtube_audio",
        lambda *args: pytest.fail("Download must not run without key"),
    )
    with pytest.raises(Exception, match="Groq API key"):
        processor.process_audio(
            "", "https://youtu.be/dQw4w9WgXcQ", None, None,
            "youtube", "auto", "whisper-large-v3-turbo", "SRT",
            progress=no_progress,
        )


def test_microphone_source_requires_recording():
    with pytest.raises(Exception, match="record"):
        processor.process_audio(
            "test-key", "", None, None, "microphone", "auto",
            "whisper-large-v3-turbo", "SRT", progress=no_progress,
        )
