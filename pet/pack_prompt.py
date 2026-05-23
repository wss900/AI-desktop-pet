"""Per-pack persona prompt bundled with character sprites."""

from __future__ import annotations

from pathlib import Path

from config.character_config import resolve_character_dir

BEHAVIOR_MARKERS = ("[行为]", "## 行为", "[behavior]", "## behavior")

# 形象包内任选其一（按优先级）
PROMPT_FILENAMES = (
    "persona.txt",
    "prompt.txt",
    "人设.txt",
    "提示词.txt",
    "character.txt",
)

MAX_PROMPT_CHARS = 12_000


def split_persona_content(raw: str) -> tuple[str, str | None]:
    for marker in BEHAVIOR_MARKERS:
        idx = raw.find(marker)
        if idx >= 0:
            chat = raw[:idx].strip()
            behavior = raw[idx + len(marker) :].strip()
            return chat, behavior or None
    return raw.strip(), None


def find_pack_prompt_file(pack_dir: Path | None = None) -> Path | None:
    root = pack_dir if pack_dir is not None else resolve_character_dir()
    if not root or not root.is_dir():
        return None
    for name in PROMPT_FILENAMES:
        path = root / name
        if path.is_file():
            return path
    return None


def load_pack_persona_raw(pack_dir: Path | None = None) -> str | None:
    path = find_pack_prompt_file(pack_dir)
    if not path:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def load_pack_persona_chat_prompt(pack_dir: Path | None = None) -> str | None:
    """供聊天 API 使用的人设（不含 [行为] 段）。"""
    raw = load_pack_persona_raw(pack_dir)
    if not raw:
        return None
    chat, _behavior = split_persona_content(raw)
    lines = [
        line
        for line in chat.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    text = "\n".join(lines).strip()
    if not text:
        return None
    if len(text) > MAX_PROMPT_CHARS:
        text = text[:MAX_PROMPT_CHARS] + "\n…（人设文件过长已截断）"
    return text


def load_pack_persona_prompt(pack_dir: Path | None = None) -> str | None:
    return load_pack_persona_chat_prompt(pack_dir)


def pack_has_bound_prompt(pack_dir: Path | None = None) -> bool:
    return load_pack_persona_prompt(pack_dir) is not None


def format_pack_prompt(template: str, pet_name: str) -> str:
    return (
        template.replace("{name}", pet_name)
        .replace("{pet_name}", pet_name)
        .replace("{宠物名}", pet_name)
    )
