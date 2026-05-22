"""Download PuppyPal white-dog GIFs and build a PNG character pack.

Source: https://github.com/scaxkl/PuppyPal_Desktop_Companion (MIT)
Run: python scripts/import_puppypal_pack.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
from collections import deque
from pathlib import Path

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
PACK_DIR = ROOT / "形象" / "PuppyPal线条小狗"
GIF_DIR = PACK_DIR / "gif"
BASE = "https://raw.githubusercontent.com/scaxkl/PuppyPal_Desktop_Companion/master/src_pet/gif"

# PuppyPal main character (white line dog) — Chinese PNG name -> source GIF
SPRITES = {
    "摸一摸": "white_dog_love.gif",
    "开心": "white_dog_happy.gif",
    "打工": "white_dog_job.gif",
    "委屈": "white_dog_cry.gif",
    "害怕": "white_dog_fear.gif",
    "吹气": "white_dog_blow.gif",
    "吃饭": "white_dog_eat.gif",
    "睡觉": "dog_sleep.gif",
    "运动": "dog_exercise.gif",
}

# Tkinter transparentcolor gray15
GRAY15 = (38, 38, 38)
GRAY_TOL = 14


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return
    print(f"  download {dest.name}")
    urllib.request.urlretrieve(url, dest)


def is_chroma(r: int, g: int, b: int) -> bool:
    return all(abs(c - t) <= GRAY_TOL for c, t in zip((r, g, b), GRAY15))


def remove_gray15(img: QImage) -> QImage:
    out = img.convertToFormat(QImage.Format.Format_ARGB32)
    w, h = out.width(), out.height()
    seeds: deque[tuple[int, int]] = deque()
    for x in range(w):
        for sx, sy in ((x, 0), (x, h - 1)):
            c = out.pixelColor(sx, sy)
            if c.alpha() and is_chroma(c.red(), c.green(), c.blue()):
                seeds.append((sx, sy))
    for y in range(h):
        for sx, sy in ((0, y), (w - 1, y)):
            c = out.pixelColor(sx, sy)
            if c.alpha() and is_chroma(c.red(), c.green(), c.blue()):
                seeds.append((sx, sy))
    while seeds:
        x, y = seeds.popleft()
        if x < 0 or x >= w or y < 0 or y >= h:
            continue
        c = out.pixelColor(x, y)
        if c.alpha() == 0:
            continue
        if not is_chroma(c.red(), c.green(), c.blue()):
            continue
        c.setAlpha(0)
        out.setPixelColor(x, y, c)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            seeds.append((nx, ny))
    return out


def gif_to_png(gif_path: Path, png_path: Path) -> bool:
    from PIL import Image, ImageSequence

    gif = Image.open(gif_path)
    frames = list(ImageSequence.Iterator(gif))
    if not frames:
        return False
    frame = frames[len(frames) // 2].convert("RGBA")
    tmp = PACK_DIR / "_tmp_frame.png"
    frame.save(tmp)
    img = QImage(str(tmp))
    tmp.unlink(missing_ok=True)
    if img.isNull():
        return False
    img = remove_gray15(img)
    return QPixmap.fromImage(img).save(str(png_path), "PNG")


def main() -> int:
    QApplication(sys.argv)
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    GIF_DIR.mkdir(parents=True, exist_ok=True)

    ok = 0
    for name, gif_name in SPRITES.items():
        url = f"{BASE}/{gif_name}"
        gif_path = GIF_DIR / gif_name
        png_path = PACK_DIR / f"{name}.png"
        try:
            download(url, gif_path)
            if gif_to_png(gif_path, png_path):
                print(f"  ok {name}.png")
                ok += 1
            else:
                print(f"  fail {name}")
        except Exception as e:
            print(f"  error {name}: {e}")

    map_file = PACK_DIR / "gif_map.json"
    map_file.write_text(
        json.dumps(SPRITES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  wrote {map_file.name}")

    readme = PACK_DIR / "README.txt"
    readme.write_text(
        "PuppyPal 线条小狗形象包\n"
        "来源: https://github.com/scaxkl/PuppyPal_Desktop_Companion (MIT)\n"
        "gif/ 为原始动画；gif_map.json 映射状态名到 gif 文件；根目录 PNG 为无 GIF 时的静态回退。\n"
        "切回银杰: .env 中 CHARACTER_PACK=透明底银杰形象文件夹\n",
        encoding="utf-8",
    )
    print(f"\nDone: {ok}/{len(SPRITES)} PNGs -> {PACK_DIR}")
    return 0 if ok == len(SPRITES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
