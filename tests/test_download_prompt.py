"""The download prompt: the app's light look, the facts the user needs, and no download by default."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import engines  # noqa: E402
from test_gui_med import make_window  # noqa: E402,F401  (fixture)


def _text(dialog) -> str:
    from PySide6.QtWidgets import QLabel
    return " ".join(label.text() for label in dialog.findChildren(QLabel))


def test_the_prompt_names_the_model_where_it_comes_from_and_how_long_it_takes(qapp):
    from PySide6.QtGui import QPalette
    from download_prompt import DownloadDialog

    d = DownloadDialog(engines.ENGINES["whisper"], has_fallback=True, model="large-v3")
    text = _text(d)
    assert "Download Whisper large-v3?" in text and "most accurate model" in text
    assert "Systran/faster-whisper-large-v3" in text and "about 3 GB, downloaded once" in text
    assert "no sign-in and nothing to accept" in text and "MIT" in text
    assert "Whisper small.en, which came with the installer" in text            # what is already here
    assert "takes a few minutes" in text and "Nothing you dictate is sent" in text
    assert "turbo" not in text                                                    # only the model it fetches
    assert d.palette().color(QPalette.ColorRole.Window).lightness() > 200      # light also when Windows is dark
    assert d.not_now_button.isDefault() and not d.download_button.autoDefault()  # Enter never downloads
    d.download_button.click()
    assert d.result() == 1


def test_without_a_known_model_the_prompt_describes_the_recogniser(qapp):
    from download_prompt import DownloadDialog

    d = DownloadDialog(engines.ENGINES["parakeet"], has_fallback=False)
    assert "needs it before you can dictate" in _text(d) and "istupakov/parakeet" in _text(d)
    d.not_now_button.click()
    assert d.result() == 0


def test_the_window_asks_with_the_prompt(make_window, monkeypatch):
    import download_prompt

    shown = []
    monkeypatch.setattr(download_prompt.DownloadDialog, "exec",
                        lambda self: shown.append((self.parent(), _text(self))) or 1)
    w = make_window()
    assert w._confirm_download("whisper", "large-v3") is True
    assert shown[0][0] is w and "Download Whisper large-v3?" in shown[0][1]


def test_the_app_theme_stays_light(qapp):
    from PySide6.QtCore import Qt
    import gui_med

    gui_med.apply_app_theme(qapp)
    try:
        assert qapp.styleSheet() == gui_med.MED_QSS
        if hasattr(qapp.styleHints(), "colorScheme"):
            assert qapp.styleHints().colorScheme() == Qt.ColorScheme.Light
    finally:
        qapp.setStyleSheet("")
        if hasattr(qapp.styleHints(), "unsetColorScheme"):
            qapp.styleHints().unsetColorScheme()
