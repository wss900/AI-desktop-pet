"""导入形象弹窗：形象包 / 人设 / 食物 三条路径。"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.dialog_theme import apply_dialog_light_theme, picker_dialog_stylesheet


class ImportPackDialog(QDialog):
    import_pack_requested = Signal(object)  # Path folder or image
    import_persona_requested = Signal(object)  # Path txt
    import_food_requested = Signal(object)  # Path folder

    def __init__(self, *, target_pack: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("导入形象")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumWidth(460)
        apply_dialog_light_theme(self)
        self.setStyleSheet(
            picker_dialog_stylesheet()
            + """
            QLabel#sectionTitle { font-size: 14px; font-weight: bold; }
            QLabel#hint { font-size: 11px; color: #8B7355; }
            QFrame#importBlock {
                border: 1px solid #E8D5B5;
                border-radius: 8px;
                background: #FFFCF7;
                padding: 8px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        heading = QLabel("导入到形象库")
        heading.setObjectName("heading")
        root.addWidget(heading)

        target = target_pack.strip() or "（尚未选择形象包）"
        target_lbl = QLabel(f"人设 / 食物将写入当前形象包：{target}")
        target_lbl.setObjectName("hint")
        target_lbl.setWordWrap(True)
        root.addWidget(target_lbl)

        root.addWidget(self._block(
            "1. 新形象文件夹",
            "导入完整形象包（含 PNG/GIF），或单张横向图集 PNG。\n"
            "会复制到 形象/ 并切换为该包。",
            [
                ("选择文件夹…", self._browse_pack_folder),
                ("选择图集 PNG…", self._browse_pack_image),
            ],
        ))

        root.addWidget(self._block(
            "2. 新人设文件",
            "选择 .txt 写入当前包的 人设.txt（可含 [行为] 段）。\n"
            "仅更新 AI 对话与主动说话规则，不换立绘。",
            [("选择人设 txt…", self._browse_persona)],
        ))

        root.addWidget(self._block(
            "3. 新食物文件夹",
            "选择含食物图片的文件夹，复制到当前包的 食物/。\n"
            "按文件名自动识别，无需 食物.txt。",
            [("选择食物文件夹…", self._browse_food_folder)],
        ))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    def _block(
        self,
        title: str,
        hint: str,
        buttons: list[tuple[str, callable]],
    ) -> QWidget:
        from PySide6.QtWidgets import QFrame

        frame = QFrame()
        frame.setObjectName("importBlock")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        t = QLabel(title)
        t.setObjectName("sectionTitle")
        layout.addWidget(t)

        h = QLabel(hint)
        h.setObjectName("hint")
        h.setWordWrap(True)
        layout.addWidget(h)

        row = QHBoxLayout()
        for label, handler in buttons:
            btn = QPushButton(label)
            btn.clicked.connect(handler)
            row.addWidget(btn)
        row.addStretch()
        layout.addLayout(row)
        return frame

    def _browse_pack_folder(self) -> None:
        from pet.pack_drop import character_library_root

        from PySide6.QtWidgets import QFileDialog

        folder = QFileDialog.getExistingDirectory(
            self,
            "选择形象文件夹（内含 PNG / GIF）",
            str(character_library_root()),
        )
        if folder:
            self.import_pack_requested.emit(Path(folder))

    def _browse_pack_image(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择横向图集 PNG",
            "",
            "图片 (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if path:
            self.import_pack_requested.emit(Path(path))

    def _browse_persona(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择人设文件",
            "",
            "文本 (*.txt *.md)",
        )
        if path:
            self.import_persona_requested.emit(Path(path))

    def _browse_food_folder(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        folder = QFileDialog.getExistingDirectory(
            self,
            "选择食物文件夹（内含 PNG / GIF）",
            "",
        )
        if folder:
            self.import_food_requested.emit(Path(folder))


def run_import_pack_dialog(
    *,
    target_pack: str = "",
    parent: QWidget | None = None,
) -> ImportPackDialog:
    dlg = ImportPackDialog(target_pack=target_pack, parent=parent)
    dlg.exec()
    return dlg
