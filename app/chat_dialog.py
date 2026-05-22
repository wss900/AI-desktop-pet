import html

from PySide6.QtCore import QEvent, Qt, Signal, QPoint
from PySide6.QtGui import QColor, QKeyEvent, QPalette, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class _DragTitleBar(QWidget):
    """可拖动移动父对话框的标题栏。"""

    def __init__(self, dialog: QDialog, parent=None):
        super().__init__(parent)
        self._dialog = dialog
        self._drag_offset: QPoint | None = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self._dialog.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._dialog.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
        super().mouseReleaseEvent(event)


class ChatDialog(QDialog):
    message_sent = Signal(str)
    stop_requested = Signal()

    def __init__(self, pet_name: str, parent=None):
        super().__init__(parent)
        self._pet_name = pet_name
        self._busy = False

        self.setWindowTitle(f"和{pet_name}聊天")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(320, 300)
        self.setStyleSheet(
            """
            QDialog { background: #FFF8F0; border: 2px solid #C9A227; border-radius: 12px; }
            QWidget#titleBar { background: #F5E6C8; border-top-left-radius: 10px; border-top-right-radius: 10px; }
            QTextEdit {
                background: white;
                color: #5C4033;
                border: 1px solid #E8D5B5;
                border-radius: 8px;
                font-size: 13px;
                selection-background-color: #C9A227;
                selection-color: white;
            }
            QLineEdit {
                padding: 8px;
                color: #5C4033;
                background: white;
                border: 1px solid #E8D5B5;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton { background: #C9A227; color: white; border: none; padding: 8px 16px; border-radius: 8px; }
            QPushButton:hover { background: #B8922A; }
            QPushButton:disabled { background: #E8D5B5; color: #8B7355; }
            QPushButton#stopBtn { background: #B85C5C; }
            QPushButton#stopBtn:hover { background: #A04A4A; }
            QPushButton#closeBtn { background: transparent; color: #5C4033; padding: 4px 10px; font-size: 16px; }
            QPushButton#closeBtn:hover { background: #E8D5B5; }
            QLabel#title { font-size: 14px; font-weight: bold; color: #5C4033; }
            QLabel#dragHint { font-size: 11px; color: #8B7355; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._title_bar = _DragTitleBar(self)
        self._title_bar.setObjectName("titleBar")
        self._title_bar.setFixedHeight(36)
        title_row = QHBoxLayout(self._title_bar)
        title_row.setContentsMargins(10, 4, 4, 4)

        titles = QVBoxLayout()
        self._title_label = QLabel(f"🌸 {pet_name}")
        self._title_label.setObjectName("title")
        self._title_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        drag_hint = QLabel("按住此处拖动")
        drag_hint.setObjectName("dragHint")
        drag_hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        titles.addWidget(self._title_label)
        titles.addWidget(drag_hint)
        title_row.addLayout(titles, stretch=1)

        close_btn = QPushButton("×")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide)
        title_row.addWidget(close_btn)

        layout.addWidget(self._title_bar)

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        pal = self.history.palette()
        pal.setColor(QPalette.ColorRole.Text, QColor("#5C4033"))
        pal.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        self.history.setPalette(pal)
        self._body_fmt = QTextCharFormat()
        self._body_fmt.setForeground(QColor("#5C4033"))
        layout.addWidget(self.history)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("说点什么…")
        self.input.returnPressed.connect(self._send)
        self.input.installEventFilter(self)
        self.history.installEventFilter(self)
        self._send_btn = QPushButton("发送")
        self._send_btn.setDefault(True)
        self._send_btn.setAutoDefault(True)
        self._send_btn.clicked.connect(self._send)
        self._stop_btn = QPushButton("停止")
        self._stop_btn.setObjectName("stopBtn")
        self._stop_btn.setVisible(False)
        self._stop_btn.clicked.connect(self.stop_requested.emit)
        row.addWidget(self.input)
        row.addWidget(self._stop_btn)
        row.addWidget(self._send_btn)
        layout.addLayout(row)

    def showEvent(self, event):
        super().showEvent(event)
        self.input.setFocus()

    def eventFilter(self, watched, event):
        if (
            event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and watched in (self.input, self.history)
        ):
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return False
                if not self._busy and self.input.isEnabled():
                    self._send()
                    return True
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                if not self._busy and self.input.isEnabled():
                    self._send()
                    event.accept()
                    return
        super().keyPressEvent(event)

    def set_pet_name(self, name: str) -> None:
        self._pet_name = name
        self._title_label.setText(f"🌸 {name}")
        self.setWindowTitle(f"和{name}聊天")

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.input.setEnabled(not busy)
        self._send_btn.setEnabled(not busy)
        self._stop_btn.setVisible(busy)

    def _send(self) -> None:
        if self._busy:
            return
        text = self.input.text().strip()
        if not text:
            return
        self.input.clear()
        self.append_user(text)
        self.message_sent.emit(text)

    def _append_html(self, html_block: str) -> None:
        self.history.append(html_block)

    def append_user(self, text: str) -> None:
        safe = html.escape(text)
        self._append_html(
            f'<p style="color:#5C4033; margin:4px 0;"><b>你：</b>{safe}</p>'
        )

    def append_pet(self, text: str) -> None:
        safe = html.escape(text)
        self._append_html(
            f'<p style="color:#5C4033; margin:4px 0;">'
            f"<b>{html.escape(self._pet_name)}：</b>{safe}</p>"
        )

    def append_pet_stream(self, text: str) -> None:
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setCharFormat(self._body_fmt)
        cursor.insertText(text)
        self.history.setTextCursor(cursor)

    def start_pet_reply(self) -> None:
        self._append_html(
            f'<p style="color:#5C4033; margin:4px 0;">'
            f"<b>{html.escape(self._pet_name)}：</b>"
        )

    def finish_pet_reply(self) -> None:
        self.history.append("")
