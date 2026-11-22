"""
download_prompt.py — "Download the speech model?", in the app's own warm light look.

Shown when the model this PC should use is missing and setup has not just agreed to the
download; nothing is downloaded unless the user agrees. Built like the Options screen and
the setup wizard (light palette and their style sheet), so it stays readable when Windows
is in dark mode.
"""

import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

import engines
from hw_profile import CPU_DEFAULT_MODEL
from setup_wizard import WIZARD_STYLE, light_palette

STYLE = WIZARD_STYLE + """
QLabel#details { color: #1F1E1D; background: #FFFFFF; border: 1px solid #E3E1D7; border-radius: 8px; padding: 10px 12px; }
QPushButton#primaryButton { background: #C96442; color: #FFFFFF; border: none; font-weight: 600; padding: 7px 18px; }
QPushButton#primaryButton:hover { background: #B5583A; }
QPushButton#primaryButton:pressed { background: #A14E33; }
"""

# Why this PC uses the model, for each Whisper model the app may download.
ROLES = {
    "large-v3": "the most accurate model, and the one MyTranscribe recommends for this PC's NVIDIA graphics card",
    "large-v3-turbo": "the faster large model for NVIDIA graphics cards, and the one this PC is set to use",
    "small.en": "the model for dictating on the processor",
}
# Who converted OpenAI's model for faster-whisper (the owner of its Hugging Face repository).
CONVERTERS = {"Systran": "Systran", "mobiuslabsgmbh": "Mobius Labs"}
TIME_NOTE = ("The download takes a few minutes on a fast connection and longer on a slow one. "
             "Dictation starts when it is ready.")
PRIVACY_NOTE = ("Only the model files are fetched. Nothing you dictate is sent anywhere, and MyTranscribe "
                "goes back to working offline afterwards.")


def _label(text: str, name: str, rich: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName(name)
    lbl.setWordWrap(True)
    lbl.setTextFormat(Qt.TextFormat.RichText if rich else Qt.TextFormat.PlainText)
    return lbl


def _table(rows) -> str:
    return "<table>" + "".join(
        f'<tr><td style="padding: 2px 14px 2px 0;"><b>{name}</b></td><td style="padding: 2px 0;">'
        f"{html.escape(value)}</td></tr>" for name, value in rows) + "</table>"


def describe(info, has_fallback: bool, model: str = "") -> tuple:
    """(heading, text, detail rows) for the model to download: the exact Whisper model when known."""
    if model in engines.WHISPER_DOWNLOADS:
        repo, size = engines.WHISPER_DOWNLOADS[model]
        text = f"Whisper {model} is {ROLES[model]}. It is not on this PC yet."
        if has_fallback and model != CPU_DEFAULT_MODEL:
            text += (f" Until it is downloaded, MyTranscribe uses Whisper {CPU_DEFAULT_MODEL}, which came with "
                     "the installer and is less accurate, especially with drug names.")
        owner = repo.split("/")[0]
        return (f"Download Whisper {model}?", text, (
            ("Model", f"Whisper {model}, by OpenAI (converted for faster-whisper by {CONVERTERS.get(owner, owner)})"),
            ("From", f"Hugging Face ({repo})"), ("Size", f"{size}, downloaded once"),
            ("Account", "None needed: no sign-in and nothing to accept"),
            ("Licence", "MIT (OpenAI Whisper)")))
    text = f"{info.label} is not on this PC yet. " + (
        "Until it is downloaded, MyTranscribe uses the smaller model that came with the installer, "
        "which makes more mistakes, especially in drug names." if has_fallback else
        "MyTranscribe needs it before you can dictate.")
    return ("Download the speech model?", text,
            (("From", info.source), ("Size", info.size), ("Licence", info.licence)))


class DownloadDialog(QDialog):
    """Asks before a model download: which model, from where, how big, under which licence, how long."""

    def __init__(self, info, has_fallback: bool, model: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("MyTranscribe — Download the speech model")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        light_palette(self)
        self.setStyleSheet(STYLE)
        heading, text, rows = describe(info, has_fallback, model)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(10)
        layout.addWidget(_label("SPEECH MODEL", "eyebrow"))
        layout.addWidget(_label(heading, "heroTitle"))
        layout.addWidget(_label(text, "pageText"))
        layout.addWidget(_label(_table(rows), "details", rich=True))
        layout.addWidget(_label(TIME_NOTE, "pageText"))
        layout.addWidget(_label(PRIVACY_NOTE, "hint"))
        layout.addSpacing(4)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.not_now_button = QPushButton("Not now")
        self.download_button = QPushButton("Download")
        self.download_button.setObjectName("primaryButton")
        self.download_button.setAutoDefault(False)          # Enter does not start a large download
        self.not_now_button.setDefault(True)
        self.not_now_button.clicked.connect(self.reject)
        self.download_button.clicked.connect(self.accept)
        buttons.addWidget(self.not_now_button)
        buttons.addWidget(self.download_button)
        layout.addLayout(buttons)
        self.setMinimumWidth(520)
