"""Render scene.spz + scene-info.json to a desktop wallpaper PNG.

Uses SPZ v3 gzip layout (read-only). No spz C++ library required.
Run: python scripts/render_spz_wallpaper.py
     python scripts/render_spz_wallpaper.py --apply
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import json
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
NGSP_MAGIC = 0x5053474E
COLOR_SCALE = 0.15
SPI_SETDESKWALLPAPER = 20


def load_scene_info(info_path: Path) -> dict:
    return json.loads(info_path.read_text(encoding="utf-8"))


def decompress_spz_packed(spz_path: Path) -> tuple[dict, memoryview]:
    raw = gzip.decompress(spz_path.read_bytes())
    if len(raw) < 16:
        raise ValueError("SPZ data too short")
    magic, version, num_points, sh_degree, frac_bits, flags, _reserved = struct.unpack_from(
        "<IIIBBBB", raw, 0
    )
    if magic != NGSP_MAGIC:
        raise ValueError(f"Not NGSP gzip SPZ (magic={magic:#x})")
    header = {
        "version": version,
        "num_points": num_points,
        "sh_degree": sh_degree,
        "fractional_bits": frac_bits,
        "flags": flags,
    }
    return header, memoryview(raw)[16:]


def _sh_dim(degree: int) -> int:
    return {0: 0, 1: 3, 2: 8, 3: 15, 4: 24}.get(degree, 0)


def unpack_fixed_positions(pos_flat: np.ndarray, n: int, fractional_bits: int) -> np.ndarray:
    pos = pos_flat.reshape(n, 9)
    out = np.empty((n, 3), dtype=np.float32)
    scale = 1.0 / (1 << fractional_bits)
    for i in range(3):
        b0 = pos[:, i * 3].astype(np.int64)
        b1 = pos[:, i * 3 + 1].astype(np.int64)
        b2 = pos[:, i * 3 + 2].astype(np.int64)
        fixed = b0 | (b1 << 8) | (b2 << 16)
        fixed = np.where(fixed & 0x800000, fixed - 0x1000000, fixed)
        out[:, i] = fixed.astype(np.float32) * scale
    return out


def load_gaussians(spz_path: Path, info: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    header, blob = decompress_spz_packed(spz_path)
    n = header["num_points"]
    sh_dim = _sh_dim(header["sh_degree"])
    uses_smallest_three = header["version"] >= 3
    rot_stride = 4 if uses_smallest_three else 3

    off = 0
    pos_len = n * 9
    positions = unpack_fixed_positions(
        np.frombuffer(blob, dtype=np.uint8, count=pos_len, offset=off),
        n,
        header["fractional_bits"],
    )
    off += pos_len
    alphas = np.frombuffer(blob, dtype=np.uint8, count=n, offset=off)
    off += n
    colors = np.frombuffer(blob, dtype=np.uint8, count=n * 3, offset=off).reshape(n, 3)
    off += n * 3
    off += n * 3  # scales
    off += n * rot_stride
    off += n * sh_dim * 3

    if off > len(blob):
        raise ValueError(f"SPZ buffer truncated at {off} / {len(blob)}")

    # Packed colors are display-ready 0–255
    alpha_f = np.clip(alphas.astype(np.float32) / 255.0, 0.05, 1.0)
    return positions, colors, alpha_f


def render_wallpaper(
    positions: np.ndarray,
    colors: np.ndarray,
    alpha: np.ndarray,
    bbox: dict | None,
    out_path: Path,
    *,
    width: int = 3840,
    height: int = 2160,
    max_points: int = 250_000,
    seed: int = 42,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(positions)
    if n > max_points:
        rng = np.random.default_rng(seed)
        idx = rng.choice(n, max_points, replace=False)
        positions = positions[idx]
        colors = colors[idx]
        alpha = alpha[idx]

    if bbox:
        cx = np.mean([bbox["x"][0], bbox["x"][1]])
        cy = np.mean([bbox["y"][0], bbox["y"][1]])
        cz = np.mean([bbox["z"][0], bbox["z"][1]])
    else:
        cx, cy, cz = positions.mean(axis=0)

    x = positions[:, 0] - cx
    y = positions[:, 1] - cy
    z = positions[:, 2] - cz

    angle = np.radians(28)
    u = x * np.cos(angle) + z * np.sin(angle)
    v = y
    depth = -x * np.sin(angle) + z * np.cos(angle)

    order = np.argsort(depth)
    u, v = u[order], v[order]
    colors = colors[order]
    alpha = alpha[order]

    span_u = max(np.ptp(u), 1e-3)
    span_v = max(np.ptp(v), 1e-3)
    margin = 0.06
    u_n = (u - u.min()) / span_u
    v_n = (v - v.min()) / span_v

    rgb = colors.astype(np.float32) / 255.0
    sizes = 0.15 + 2.5 * alpha

    fig_w = width / 100
    fig_h = height / 100
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=100)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.scatter(
        u_n,
        v_n,
        c=np.clip(rgb, 0, 1),
        s=sizes,
        alpha=np.clip(alpha * 0.85, 0.08, 0.95),
        linewidths=0,
        edgecolors="none",
    )
    ax.set_xlim(-margin, 1 + margin)
    ax.set_ylim(-margin, 1 + margin)
    ax.set_aspect("equal")
    ax.axis("off")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(
        out_path,
        dpi=100,
        bbox_inches="tight",
        pad_inches=0,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    return out_path


def apply_wallpaper(image_path: Path) -> None:
    path = str(image_path.resolve())
    ok = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)
    if not ok:
        raise OSError("SystemParametersInfoW failed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render SPZ scene to wallpaper PNG")
    parser.add_argument("--info", type=Path, default=Path(r"D:\scene-info.json"))
    parser.add_argument("--spz", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path(r"D:\scene_wallpaper.png"))
    parser.add_argument("--apply", action="store_true", help="Set as Windows wallpaper")
    parser.add_argument("--width", type=int, default=3840)
    parser.add_argument("--height", type=int, default=2160)
    args = parser.parse_args()

    if not args.info.is_file():
        print(f"Missing: {args.info}", file=sys.stderr)
        return 1

    info = load_scene_info(args.info)
    spz_path = args.spz or Path("D:/") / info.get("file", "scene.spz")
    if not spz_path.is_file():
        print(f"Missing SPZ: {spz_path}", file=sys.stderr)
        return 1

    print(f"Loading {spz_path.name} ({info.get('num_points', '?')} points)...")
    positions, colors, alpha = load_gaussians(spz_path, info)
    print(f"Rendering {len(positions)} splats -> {args.out}")
    render_wallpaper(
        positions,
        colors,
        alpha,
        info.get("bounding_box"),
        args.out,
        width=args.width,
        height=args.height,
    )
    print(f"Saved: {args.out}")

    if args.apply:
        apply_wallpaper(args.out)
        print("Desktop wallpaper updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
