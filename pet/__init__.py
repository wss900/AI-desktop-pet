from __future__ import annotations

__all__ = ["PetController", "PetState"]


def __getattr__(name: str):
    if name in ("PetController", "PetState"):
        from pet.controller import PetController, PetState

        return PetController if name == "PetController" else PetState
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
