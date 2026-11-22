"""The download prompt: the app's light look, the facts the user needs, and no download by default."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import engines  # noqa: E402
from test_gui_med import make_window  # noqa: E402,F401  (fixture)


def test_the_prompt_says_what_where_how_big_and_which_licence(qapp):
    from PySide6.QtGui import QPalette
    from PySide6.QtWidgets import QLabel
    from download_prompt import DownloadDialog

    d = DownloadDialog(engines.ENGINES["whisper"], has_fallback=True)
    text = " ".join(label.text() for label in d.findChildren(QLabel))
    assert "Systran/faster-whisper-large-v3" in text and "about 3 GB" in text and "MIT" in text
    assert "smaller model that came with the installer" in text and "Nothing you dictate is sent" in text
    assert d.palette().color(QPalette.ColorRole.Window).lightness() > 200      # light also when Windows is dark
    assert d.not_now_button.isDefault() and not d.download_button.autoDefault()  # Enter never downloads
    d.download_button.click()
    assert d.result() == 1
    d = DownloadDialog(engines.ENGINES["parakeet"], has_fallback=False)
    assert "needs it before you can dictate" in " ".join(label.text() for label in d.findChildren(QLabel))
    d.not_now_button.click()
    assert d.result() == 0


def test_the_window_asks_with_the_prompt(make_window, monkeypatch):
    import download_prompt

    shown = []
    monkeypatch.setattr(download_prompt.DownloadDialog, "exec", lambda self: shown.append(self.parent()) or 1)
    w = make_window()
    assert w._confirm_download("whisper") is True and shown == [w]


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
