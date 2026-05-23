"""宠物头顶陪伴气泡（可点击打开聊天）。"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QWidget


class SpeechBubbleLabel(QLabel):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMaximumWidth(240)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.hide()
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self._on_click: Callable[[], None] | None = None
        self._clickable = False

    def show_message(
        self,
        text: str,
        *,
        duration_ms: int = 5000,
        clickable: bool = False,
        on_click: Callable[[], None] | None = None,
    ) -> None:
        self._clickable = clickable
        self._on_click = on_click
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("点击回复")
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        else:
            self.unsetCursor()
            self.setToolTip("")
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setStyleSheet(
            "color: #FFF8F0;"
            "background: rgba(40, 32, 28, 200);"
            "border: 1px solid rgba(201, 162, 39, 180);"
            "border-radius: 10px;"
            "padding: 6px 10px;"
        )
        self.setText(text)
        self.adjustSize()
        self.show()
        self.raise_()
        self._hide_timer.start(max(2000, duration_ms))

    def mouseReleaseEvent(self, event) -> None:
        if (
            self._clickable
            and self._on_click
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._on_click()
            self.hide()
            event.accept()
            return
        super().mouseReleaseEvent(event)
