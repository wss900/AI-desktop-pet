"""Split a 2x2 character sheet into four transparent PNGs."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QImage, QColor
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent

# 四宫格顺序：左上、右上、左下、右下
QUADRANTS = (
    ("打招呼", 0, 0),
    ("坐立", 1, 0),
    ("喝茶", 0, 1),
    ("打哈欠", 1, 1),
)


def black_to_alpha(img: QImage, threshold: int = 28) -> QImage:
    out = img.convertToFormat(QImage.Format.Format_ARGB32)
    for y in range(out.height()):
        for x in range(out.width()):
            c = out.pixelColor(x, y)
            if c.red() <= threshold and c.green() <= threshold and c.blue() <= threshold:
                c.setAlpha(0)
                out.setPixelColor(x, y, c)
    return out


def crop_to_content(img: QImage, pad: int = 4) -> QImage:
    w, h = img.width(), img.height()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            if img.pixelColor(x, y).alpha() > 8:
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if not found:
        return img
    min_x = max(0, min_x - pad)
    min_y = max(0, min_y - pad)
    max_x = min(w - 1, max_x + pad)
    max_y = min(h - 1, max_y + pad)
    return img.copy(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def split_sheet(src: Path, out_dir: Path) -> list[str]:
    img = QImage(str(src))
    if img.isNull():
        raise FileNotFoundError(src)
    w, h = img.width(), img.height()
    cw, ch = w // 2, h // 2
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for name, col, row in QUADRANTS:
        x, y = col * cw, row * ch
        part = img.copy(x, y, cw, ch)
        part = black_to_alpha(part)
        part = crop_to_content(part)
        dest = out_dir / f"{name}.png"
        part.save(str(dest), "PNG")
        saved.append(name)
    return saved


def main() -> int:
    app = QApplication(sys.argv)
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not src or not src.is_file():
        print("Usage: python scripts/split_transparent_sheet.py <sheet.png> [out_dir]")
        return 1
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "形象" / "透明底银杰形象文件夹"
    names = split_sheet(src, out)
    print("Saved to", out)
    for n in names:
        print(" -", n + ".png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
