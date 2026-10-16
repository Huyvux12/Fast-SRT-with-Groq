from app import create_ui, select_source


def test_ui_builds():
    demo = create_ui()
    assert demo is not None


def test_source_switching():
    visible = [component.get("visible") for component in select_source("upload")]
    assert visible == [False, True, False]
