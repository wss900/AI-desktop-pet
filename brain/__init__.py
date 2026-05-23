from __future__ import annotations

__all__ = ["ChatService"]


def __getattr__(name: str):
    if name == "ChatService":
        from brain.chat import ChatService

        return ChatService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
