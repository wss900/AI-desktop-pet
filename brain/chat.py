from __future__ import annotations

from datetime import datetime
from typing import Callable

from openai import OpenAI

from brain.prompts import build_system_prompt
from brain.tools import (
    MemoryAction,
    ReminderAction,
    format_reminders_for_prompt,
    parse_actions,
    validate_reminder_datetime,
)
from config.chat_api_config import load_chat_api_config
from config.settings import PET_NAME, get_character_display_name
from memory.store import MemoryStore


class ChatCancelled(Exception):
    """Stream stopped by user; partial reply may be available."""

    def __init__(self, partial_display: str = "") -> None:
        self.partial_display = partial_display
        super().__init__()


class ChatService:
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self._client: OpenAI | None = None
        api = load_chat_api_config()
        if api.is_complete():
            self._client = OpenAI(api_key=api.api_key, base_url=api.base_url)
        self._model = api.model if api.is_complete() else ""

    @property
    def available(self) -> bool:
        return self._client is not None

    def _build_messages(self, user_text: str, reminders: list[dict]) -> list[dict]:
        pet_name = get_character_display_name() or self.memory.get_pet_name() or PET_NAME
        user_name = self.memory.get_user_name()
        system = build_system_prompt(
            pet_name, user_name, self.memory.recent_memories()
        )
        system += "\n\n" + format_reminders_for_prompt(reminders)
        messages = [{"role": "system", "content": system}]
        for m in self.memory.recent_chats(10):
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_text})
        return messages

    def chat_stream(
        self,
        user_text: str,
        reminders: list[dict],
        on_token: Callable[[str], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> tuple[str, ReminderAction | None, MemoryAction | None]:
        if not self._client:
            return (
                "我还没有配置聊天 API。请打开托盘「设置」，填写 API Key、API 地址和模型。",
                None,
                None,
            )

        messages = self._build_messages(user_text, reminders)

        chunks: list[str] = []
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            if should_cancel and should_cancel():
                partial = "".join(chunks)
                display, _, _ = parse_actions(partial)
                raise ChatCancelled(display)

            delta = chunk.choices[0].delta.content or ""
            if delta:
                chunks.append(delta)
                if on_token:
                    on_token(delta)

        raw = "".join(chunks)
        display, reminder, memory = parse_actions(raw)
        self.memory.add_chat("user", user_text)
        self.memory.add_chat("assistant", display)
        self.memory.trim_chats()
        return display, reminder, memory

    def apply_memory_action(self, action: MemoryAction) -> None:
        if action.user_name:
            self.memory.set_user_name(action.user_name)
        if action.memory:
            self.memory.add_memory(action.memory)

    def validate_reminder(self, action: ReminderAction) -> str | None:
        dt = validate_reminder_datetime(action.datetime)
        if not dt:
            return "提醒时间格式不对，请换个说法试试。"
        if dt <= datetime.now():
            return "提醒时间需要在未来哦。"
        return None
