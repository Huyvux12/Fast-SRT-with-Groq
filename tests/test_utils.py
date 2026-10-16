import pytest

from utils import canonical_youtube_url, format_time_srt, get_youtube_video_id

VIDEO_ID = "dQw4w9WgXcQ"


@pytest.mark.parametrize("url", [
    f"https://www.youtube.com/watch?v={VIDEO_ID}",
    f"https://youtube.com/watch?si=abc123&v={VIDEO_ID}&t=14",
    f"https://youtu.be/{VIDEO_ID}?si=abc",
    f"https://www.youtube.com/shorts/{VIDEO_ID}",
    f"https://www.youtube.com/live/{VIDEO_ID}",
    f"https://www.youtube.com/embed/{VIDEO_ID}",
])
def test_supported_youtube_urls(url):
    assert get_youtube_video_id(url) == VIDEO_ID
    assert canonical_youtube_url(url) == f"https://www.youtube.com/watch?v={VIDEO_ID}"


@pytest.mark.parametrize("url", [
    f"http://www.youtube.com/watch?v={VIDEO_ID}",
    f"https://youtube.com.evil.example/watch?v={VIDEO_ID}",
    f"https://evil.example/path/youtube.com/watch?v={VIDEO_ID}",
    f"https://127.0.0.1/redirect/youtube.com/watch?v={VIDEO_ID}",
    f"https://www.youtube.com:444/watch?v={VIDEO_ID}",
    f"https://user:pass@www.youtube.com/watch?v={VIDEO_ID}",
    "https://www.youtube.com/watch?v=incorrect",
    "https://www.youtube.com/playlist?list=PL123",
    "file:///etc/passwd",
    "",
])
def test_rejects_unsafe_or_invalid_urls(url):
    assert get_youtube_video_id(url) is None
    with pytest.raises(ValueError):
        canonical_youtube_url(url)


def test_time_rounding_and_rollover():
    assert format_time_srt(0) == "00:00:00,000"
    assert format_time_srt(59.9998) == "00:01:00,000"
    assert format_time_srt(3601.001) == "01:00:01,001"


@pytest.mark.parametrize("value", [-0.1, float("nan"), float("inf"), "invalid"])
def test_invalid_timestamps(value):
    with pytest.raises(ValueError):
        format_time_srt(value)
