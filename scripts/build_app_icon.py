"""从指定形象图生成带边框的 assets/app_icon.ico。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# 默认：歪头 + 古风金边（与聊天窗 #C9A227 一致）
DEFAULT_ICON_SOURCE = ROOT / "形象" / "银杰动漫形象" / "歪头.png"
ICON_SIZE = 256
BORDER_WIDTH = 10
BORDER_COLOR = os.getenv("APP_ICON_BORDER_COLOR", "#C9A227")
BG_TINT = os.getenv("APP_ICON_BG_TINT", "#FFF8F0")  # 淡米白底，可选透明


def _resolve_source() -> Path | None:
    raw = os.getenv("APP_ICON_SOURCE", "").strip()
    if raw:
        p = Path(raw)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_file():
            return p
    if DEFAULT_ICON_SOURCE.is_file():
        return DEFAULT_ICON_SOURCE
    return None


def _make_icon_pixmap(
    src: Path,
    size: int = ICON_SIZE,
    border_width: int = BORDER_WIDTH,
    border_color: str = BORDER_COLOR,
    bg_tint: str = BG_TINT,
) -> QPixmap:
    inner = size - border_width * 2 - 8
    # 图标直接用原图，不抠图
    character = QPixmap(str(src))
    if character.isNull():
        return QPixmap()
    if character.height() > inner:
        character = character.scaledToHeight(
            inner,
            Qt.TransformationMode.SmoothTransformation,
        )

    canvas = QPixmap(size, size)
    canvas.fill(Qt.GlobalColor.transparent)

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    margin = 4
    outer = QRectF(
        margin,
        margin,
        size - 2 * margin,
        size - 2 * margin,
    )
    radius = size * 0.18

    # 淡色圆角底，衬托透明边
    if bg_tint and bg_tint.lower() not in ("none", "transparent"):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(bg_tint))
        painter.drawRoundedRect(outer, radius, radius)

    # 金色边框
    pen = QPen(QColor(border_color))
    pen.setWidth(border_width)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(outer, radius, radius)

    # 角色居中
    cw, ch = character.width(), character.height()
    x = (size - cw) // 2
    y = (size - ch) // 2
    painter.drawPixmap(x, y, character)
    painter.end()

    return canvas


def png_to_ico(pix: QPixmap, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    return pix.save(str(dest), "ICO")


def main() -> int:
    app = QApplication(sys.argv)
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else _resolve_source()
    if not src or not src.is_file():
        print("未找到图标源图，请设置 APP_ICON_SOURCE 或放置", DEFAULT_ICON_SOURCE)
        return 1

    pix = _make_icon_pixmap(src)
    dest = ROOT / "assets" / "app_icon.ico"
    if not png_to_ico(pix, dest):
        print("保存 ICO 失败")
        return 1
    # 同时存一张 PNG 便于预览
    preview = ROOT / "assets" / "app_icon.png"
    pix.save(str(preview), "PNG")
    print("已生成", dest)
    print("预览", preview)
    print("源图", src)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
