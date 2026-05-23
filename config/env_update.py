"""Update .env and reload config modules after character selection."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

from dotenv import load_dotenv

from config.character_presets import CharacterPreset, preset_to_env
from config.chat_api_config import LEGACY_CHAT_ENV_KEYS
from config.settings import ROOT

ENV_PATH = ROOT / ".env"

# 已从逻辑中废弃；更新 .env 时自动删掉对应行
_OBSOLETE_ENV_KEYS = frozenset(
    {
        "CHARACTER_STATES",
        "CHARACTER_DISPLAY_NAME",
        "CHARACTER_ON_HOVER",
        "CHARACTER_RANDOM",
        "PET_NAME",
        "CHARACTER_MATTE_DARK",
        "CHARACTER_DEFRINGE",
        "CHARACTER_ALPHA_FEATHER",
    }
)


def update_env_file(
    updates: dict[str, str],
    *,
    drop_keys: frozenset[str] | None = None,
) -> None:
    lines: list[str] = []
    if ENV_PATH.is_file():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    pending = dict(updates)
    remove = drop_keys or frozenset()
    out: list[str] = []
    seen: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in _OBSOLETE_ENV_KEYS or key in remove:
                continue
            if key in pending:
                out.append(f"{key}={pending.pop(key)}")
                seen.add(key)
                continue
        out.append(line)

    for key, value in pending.items():
        if key not in seen:
            out.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def apply_preset(
    preset: CharacterPreset,
    *,
    remember_skip_picker: bool,
    run_mode: str | None = None,
    chat_api: "ChatApiConfig | None" = None,
    survival_mode: bool | None = None,
    survival_memory: bool | None = None,
) -> None:
    from config.chat_api_config import ChatApiConfig, chat_api_to_env
    from config.pet_mode import run_mode_env_updates

    env = preset_to_env(preset)
    if remember_skip_picker:
        env["SHOW_CHARACTER_PICKER"] = "0"
    else:
        env["SHOW_CHARACTER_PICKER"] = "1"
    if run_mode is not None:
        env.update(run_mode_env_updates(run_mode=run_mode))
    elif survival_mode is not None:
        legacy = "entertainment"
        if survival_mode and survival_memory:
            legacy = "companion"
        elif survival_mode:
            legacy = "entertainment"
        env.update(run_mode_env_updates(run_mode=legacy))
    if chat_api is not None:
        env.update(chat_api_to_env(chat_api))
        update_env_file(env, drop_keys=LEGACY_CHAT_ENV_KEYS)
    else:
        update_env_file(env)
    load_dotenv(ENV_PATH, override=True)
    reload_config_modules()


def reload_config_modules() -> None:
    for name in (
        "config.settings",
        "config.character_config",
        "config.character_presets",
        "config.pack_discovery",
        "config.pet_mode",
        "config.companion",
        "brain.prompts",
        "brain.persona_behavior",
        "brain.chat",
        "pet.pack_prompt",
    ):
        mod = importlib.import_module(name)
        importlib.reload(mod)


def should_show_character_picker() -> bool:
    return os.getenv("SHOW_CHARACTER_PICKER", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


def apply_settings(
    *,
    run_mode: str,
    chat_api: "ChatApiConfig",
    show_character_picker: bool,
    max_height: int | None = None,
    companion_enabled: bool | None = None,
) -> None:
    """Save mode / API / picker flag without changing character pack."""
    from config.chat_api_config import ChatApiConfig, chat_api_to_env
    from config.character_config import clamp_character_height
    from config.companion import companion_to_env
    from config.pet_mode import run_mode_env_updates

    env: dict[str, str] = {
        "SHOW_CHARACTER_PICKER": "1" if show_character_picker else "0",
    }
    env.update(run_mode_env_updates(run_mode=run_mode))
    if max_height is not None:
        env["CHARACTER_MAX_HEIGHT"] = str(clamp_character_height(max_height))
    if companion_enabled is not None:
        env.update(companion_to_env(enabled=companion_enabled))
    env.update(chat_api_to_env(chat_api))
    update_env_file(env, drop_keys=LEGACY_CHAT_ENV_KEYS)
    load_dotenv(ENV_PATH, override=True)
    reload_config_modules()


def relaunch_app() -> None:
    import subprocess
    import sys

    from config.paths import is_frozen

    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) or 0
    if is_frozen():
        subprocess.Popen([sys.executable], cwd=str(ROOT), creationflags=flags)
        return

    main_py = ROOT / "main.py"
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        pyw = Path(exe).with_name("pythonw.exe")
        if pyw.is_file():
            exe = str(pyw)
    subprocess.Popen(
        [exe, str(main_py)],
        cwd=str(ROOT),
        creationflags=flags,
    )
