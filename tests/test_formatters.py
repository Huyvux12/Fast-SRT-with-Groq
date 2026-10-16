import json

from formatters import normalize_segments, to_json, to_srt, to_txt


def test_srt_txt_json_output():
    segments = [
        {"start": 2.5, "end": 4.0, "text": " world "},
        {"start": 0.0, "end": 2.5, "text": "Hello"},
    ]
    expected = (
        "1\n00:00:00,000 --> 00:00:02,500\nHello\n\n"
        "2\n00:00:02,500 --> 00:00:04,000\nworld\n"
    )
    assert to_srt(segments) == expected
    assert to_txt(segments) == "Hello\nworld"
    data = json.loads(to_json(segments, "Hello world", "en", 4.0))
    assert data["duration"] == 4.0
    assert data["language"] == "en"
    assert data["segments"][0]["id"] == 1


def test_unusable_segments_removed():
    segments = [
        {"start": 0, "end": 1, "text": " "},
        {"start": -1, "end": 0, "text": "invalid"},
        {"start": float("nan"), "end": 1, "text": "nan"},
        {"start": 2, "end": 1, "text": "reversed"},
        {"start": 1, "end": 2, "text": "Valid"},
    ]
    assert normalize_segments(segments) == [
        {"start": 1.0, "end": 2.0, "text": "Valid"}
    ]
    assert to_srt([]) == ""
