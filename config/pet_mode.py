"""宠物运行模式：陪伴（离线也计时）或娱乐（仅运行时扣 HP）。"""

from __future__ import annotations

import os

# companion=陪伴（离线扣 HP）| entertainment=娱乐（仅运行时扣 HP）
# 兼容旧值 survival/normal + SURVIVAL_MEMORY_MODE
PET_MODE = os.getenv("PET_MODE", "entertainment").strip().lower()

COMPANION_ALIASES = frozenset(
    {"companion", "陪伴", "companion_mode", "陪伴模式"}
)
ENTERTAINMENT_ALIASES = frozenset(
    {"entertainment", "娱乐", "entertainment_mode", "娱乐模式"}
)
LEGACY_SURVIVAL_ALIASES = frozenset(
    {"survival", "生存", "on", "1", "true", "yes"}
)
LEGACY_NORMAL_ALIASES = frozenset(
    {"normal", "普通", "off", "0", "false", "no"}
)


def is_survival_memory_mode_value(value: str) -> bool:
    v = value.strip().lower()
    return v in ("1", "true", "yes", "on", "survival_memory", "memory")


def resolve_run_mode(raw: str | None = None) -> str:
    """返回 companion | entertainment。"""
    mode = (raw if raw is not None else PET_MODE).strip().lower()
    if mode in COMPANION_ALIASES:
        return "companion"
    if mode in ENTERTAINMENT_ALIASES:
        return "entertainment"
    if mode in LEGACY_NORMAL_ALIASES:
        return "entertainment"
    if mode in LEGACY_SURVIVAL_ALIASES:
        mem = os.getenv("SURVIVAL_MEMORY_MODE", "0")
        return "companion" if is_survival_memory_mode_value(mem) else "entertainment"
    return "entertainment"


def is_companion_run_mode() -> bool:
    return resolve_run_mode() == "companion"


def is_entertainment_run_mode() -> bool:
    return resolve_run_mode() == "entertainment"


def is_survival_mode() -> bool:
    """两种模式均有 HP / 喂食。"""
    return True


def is_survival_mode_value(value: str) -> bool:
    """兼容旧测试与迁移逻辑。"""
    return value.strip().lower() not in LEGACY_NORMAL_ALIASES


def is_survival_memory_mode() -> bool:
    """陪伴模式：退出程序也按真实时间扣 HP。"""
    return is_companion_run_mode()


def pet_mode_env_value(*, run_mode: str) -> str:
    mode = run_mode.strip().lower()
    if mode in COMPANION_ALIASES or mode == "companion":
        return "companion"
    return "entertainment"


def survival_memory_env_value(*, enabled: bool) -> str:
    return "1" if enabled else "0"


def run_mode_env_updates(*, run_mode: str) -> dict[str, str]:
    companion = pet_mode_env_value(run_mode=run_mode) == "companion"
    return {
        "PET_MODE": pet_mode_env_value(run_mode=run_mode),
        "SURVIVAL_MEMORY_MODE": survival_memory_env_value(enabled=companion),
    }


def mode_display_name() -> str:
    return "陪伴模式" if is_companion_run_mode() else "娱乐模式"


def run_mode_display_name(run_mode: str) -> str:
    return "陪伴模式" if run_mode == "companion" else "娱乐模式"
