from config.pet_mode import (
    is_companion_run_mode,
    is_entertainment_run_mode,
    is_survival_memory_mode,
    is_survival_mode,
    pet_mode_env_value,
    resolve_run_mode,
    run_mode_env_updates,
)


def test_is_survival_always_on():
    assert is_survival_mode()


def test_resolve_companion():
    assert resolve_run_mode("companion") == "companion"
    assert resolve_run_mode("陪伴") == "companion"


def test_resolve_entertainment():
    assert resolve_run_mode("entertainment") == "entertainment"
    assert resolve_run_mode("娱乐") == "entertainment"
    assert resolve_run_mode("normal") == "entertainment"


def test_legacy_survival_with_memory():
    import os

    old = os.environ.get("SURVIVAL_MEMORY_MODE")
    os.environ["SURVIVAL_MEMORY_MODE"] = "1"
    try:
        assert resolve_run_mode("survival") == "companion"
    finally:
        if old is None:
            os.environ.pop("SURVIVAL_MEMORY_MODE", None)
        else:
            os.environ["SURVIVAL_MEMORY_MODE"] = old


def test_companion_has_offline_memory():
    env = run_mode_env_updates(run_mode="companion")
    assert env["SURVIVAL_MEMORY_MODE"] == "1"
    env2 = run_mode_env_updates(run_mode="entertainment")
    assert env2["SURVIVAL_MEMORY_MODE"] == "0"


def test_pet_mode_env_value():
    assert pet_mode_env_value(run_mode="companion") == "companion"
    assert pet_mode_env_value(run_mode="entertainment") == "entertainment"


def test_run_mode_env_updates():
    env = run_mode_env_updates(run_mode="companion")
    assert env["PET_MODE"] == "companion"
    assert env["SURVIVAL_MEMORY_MODE"] == "1"
    env2 = run_mode_env_updates(run_mode="entertainment")
    assert env2["SURVIVAL_MEMORY_MODE"] == "0"
