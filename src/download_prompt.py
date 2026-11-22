"""
download_prompt.py — "Download the speech model?", in the app's own warm light look.

Shown before MyTranscribe fetches a model; nothing is downloaded unless the user agrees.
Built like the Options screen and the setup wizard (light palette and their style sheet),
so it stays readable when Windows is in dark mode.
"""

import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from setup_wizard import WIZARD_STYLE, light_palette

STYLE = WIZARD_STYLE + """
QLabel#details { color: #1F1E1D; background: #FFFFFF; border: 1px solid #E3E1D7; border-radius: 8px; padding: 10px 12px; }
QPushButton#primaryButton { background: #C96442; color: #FFFFFF; border: none; font-weight: 600; padding: 7px 18px; }
QPushButton#primaryButton:hover { background: #B5583A; }
QPushButton#primaryButton:pressed { background: #A14E33; }
"""


def _label(text: str, name: str, rich: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName(name)
    lbl.setWordWrap(True)
    lbl.setTextFormat(Qt.TextFormat.RichText if rich else Qt.TextFormat.PlainText)
    return lbl


class DownloadDialog(QDialog):
    """Asks before a model download: what, from where, how big, under which licence."""

    def __init__(self, info, has_fallback: bool, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("MyTranscribe — Download the speech model")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        light_palette(self)
        self.setStyleSheet(STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(10)
        layout.addWidget(_label("SPEECH MODEL", "eyebrow"))
        layout.addWidget(_label("Download the speech model?", "heroTitle"))
        layout.addWidget(_label(
            f"{info.label} is not on this PC yet. " + (
                "Until it is downloaded, MyTranscribe uses the smaller model that came with the installer, "
                "which makes more mistakes, especially in drug names." if has_fallback else
                "MyTranscribe needs it before you can dictate."), "pageText"))
        rows = "".join(f'<tr><td style="padding: 2px 14px 2px 0;"><b>{name}</b></td>'
                       f'<td style="padding: 2px 0;">{html.escape(value)}</td></tr>'
                       for name, value in (("From", info.source), ("Size", info.size), ("Licence", info.licence)))
        layout.addWidget(_label(f"<table>{rows}</table>", "details", rich=True))
        layout.addWidget(_label("Only the model files are fetched. Nothing you dictate is sent anywhere, and "
                                "MyTranscribe goes back to working offline afterwards.", "hint"))
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
        self.setMinimumWidth(500)
