"""Tray settings: run mode, chat API, character, startup picker."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.character_manage_panel import CharacterManagePanel
from config.chat_api_config import (
    EXAMPLE_BASE_URLS,
    EXAMPLE_MODELS,
    ChatApiConfig,
    load_chat_api_config,
)
from config.env_update import should_show_character_picker
from app.dialog_theme import (
    apply_content_light_theme,
    apply_dialog_light_theme,
    picker_dialog_stylesheet,
)
from config.character_config import (
    CHARACTER_MAX_HEIGHT,
    CHARACTER_SIZE_MAX,
    CHARACTER_SIZE_MIN,
    clamp_character_height,
)
from config.companion import companion_enabled, memory_recent_limit
from config.pet_mode import is_companion_run_mode, resolve_run_mode


class SettingsDialog(QDialog):
    def __init__(
        self,
        parent=None,
        *,
        on_height_preview: Callable[[int], None] | None = None,
        memory_lines: list[str] | None = None,
        companion_days: str = "",
        on_open_import_dialog: Callable[[], None] | None = None,
        on_open_switch_dialog: Callable[[], None] | None = None,
        current_pack: str = "",
    ):
        super().__init__(parent)
        self._run_mode = resolve_run_mode()
        self._initial_run_mode = self._run_mode
        self._show_picker = should_show_character_picker()
        self._on_height_preview = on_height_preview
        self._initial_height = clamp_character_height(CHARACTER_MAX_HEIGHT)
        self._companion_enabled = companion_enabled()
        self._initial_companion_enabled = self._companion_enabled
        self._memory_lines = memory_lines or []

        self.setWindowTitle("设置")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumWidth(520)
        self.setMinimumHeight(560)
        apply_dialog_light_theme(self)
        self.setStyleSheet(picker_dialog_stylesheet())

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_content_light_theme(scroll.viewport())
        content = QWidget()
        apply_content_light_theme(content)
        body = QVBoxLayout(content)
        body.setContentsMargins(0, 0, 4, 0)
        body.setSpacing(10)

        heading = QLabel("桌面宠物设置")
        heading.setObjectName("heading")
        body.addWidget(heading)

        char_title = QLabel("形象")
        char_title.setObjectName("sectionTitle")
        body.addWidget(char_title)
        self._char_panel = CharacterManagePanel(current_pack=current_pack)
        if on_open_import_dialog:
            self._char_panel.import_dialog_requested.connect(
                on_open_import_dialog
            )
        if on_open_switch_dialog:
            self._char_panel.switch_dialog_requested.connect(
                on_open_switch_dialog
            )
        body.addWidget(self._char_panel)

        mode_title = QLabel("运行模式")
        mode_title.setObjectName("sectionTitle")
        body.addWidget(mode_title)
        mode_row = QHBoxLayout()
        self._mode_group = QButtonGroup(self)
        self._rb_companion = QRadioButton("陪伴模式")
        self._rb_entertainment = QRadioButton("娱乐模式")
        self._mode_group.addButton(self._rb_companion, 1)
        self._mode_group.addButton(self._rb_entertainment, 0)
        if is_companion_run_mode():
            self._rb_companion.setChecked(True)
        else:
            self._rb_entertainment.setChecked(True)
        self._mode_group.idClicked.connect(self._on_mode_clicked)
        mode_row.addWidget(self._rb_companion)
        mode_row.addWidget(self._rb_entertainment)
        mode_row.addStretch()
        body.addLayout(mode_row)
        mode_hint = QLabel(
            "均有 HP 条、喂食与复活 · 陪伴：关闭程序也计时，久不打开可能离线饿死 · "
            "娱乐：仅桌宠运行时扣 HP。切换后立即按新规则结算。"
        )
        mode_hint.setObjectName("hint")
        mode_hint.setWordWrap(True)
        body.addWidget(mode_hint)

        size_title = QLabel("宠物大小")
        size_title.setObjectName("sectionTitle")
        body.addWidget(size_title)
        size_row = QHBoxLayout()
        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setMinimum(CHARACTER_SIZE_MIN)
        self._size_slider.setMaximum(CHARACTER_SIZE_MAX)
        self._size_slider.setValue(self._initial_height)
        self._size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._size_slider.setTickInterval(40)
        self._size_slider.valueChanged.connect(self._on_size_slider)
        self._size_label = QLabel()
        self._size_label.setObjectName("sizeValue")
        self._update_size_label(self._initial_height)
        size_row.addWidget(self._size_slider, stretch=1)
        size_row.addWidget(self._size_label)
        body.addLayout(size_row)
        size_hint = QLabel(
            f"拖动滑块调节立绘高度（{CHARACTER_SIZE_MIN}～{CHARACTER_SIZE_MAX} 像素），"
            "拖动时即时预览；点「保存」写入配置。"
        )
        size_hint.setObjectName("hint")
        size_hint.setWordWrap(True)
        body.addWidget(size_hint)

        api_title = QLabel("聊天 API（OpenAI 兼容）")
        api_title.setObjectName("sectionTitle")
        body.addWidget(api_title)
        api_cfg = load_chat_api_config()
        api_form = QFormLayout()
        api_form.setSpacing(8)
        self._api_key = QLineEdit()
        self._api_key.setPlaceholderText("各平台提供的 API Key")
        self._api_key.setText(api_cfg.api_key)
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key.setClearButtonEnabled(True)
        api_form.addRow("API Key", self._api_key)
        self._api_base = QLineEdit()
        self._api_base.setPlaceholderText(
            "例如 " + " / ".join(EXAMPLE_BASE_URLS[:2])
        )
        self._api_base.setText(api_cfg.base_url)
        api_form.addRow("API 地址", self._api_base)
        self._api_model = QLineEdit()
        self._api_model.setPlaceholderText(
            "例如 " + "、".join(EXAMPLE_MODELS[:3])
        )
        self._api_model.setText(api_cfg.model)
        api_form.addRow("模型名称", self._api_model)
        body.addLayout(api_form)
        api_hint = QLabel(
            "支持 DeepSeek、OpenAI、Ollama、国内中转等；三项都填好才能聊天。"
            "密钥仅保存在本机 .env，不会上传。"
        )
        api_hint.setObjectName("hint")
        api_hint.setWordWrap(True)
        body.addWidget(api_hint)

        companion_title = QLabel("AI 陪伴")
        companion_title.setObjectName("sectionTitle")
        body.addWidget(companion_title)
        self._companion_cb = QCheckBox("开启 AI 陪伴（问候、气泡、人设 [行为] 段）")
        self._companion_cb.setChecked(self._companion_enabled)
        body.addWidget(self._companion_cb)
        if companion_days:
            days_lbl = QLabel(companion_days)
            days_lbl.setObjectName("hint")
            body.addWidget(days_lbl)
        mem_title = QLabel("它记得：")
        mem_title.setObjectName("sectionTitle")
        body.addWidget(mem_title)
        if self._memory_lines:
            shown = self._memory_lines[-memory_recent_limit():]
            mem_text = "\n".join(f"· {m}" for m in shown)
        else:
            mem_text = "（还没有长期记忆，聊天时告诉它「我叫…」或让它记住的事）"
        mem_lbl = QLabel(mem_text)
        mem_lbl.setObjectName("hint")
        mem_lbl.setWordWrap(True)
        body.addWidget(mem_lbl)

        self._picker_cb = QCheckBox("每次启动时显示形象选择界面")
        self._picker_cb.setChecked(self._show_picker)
        body.addWidget(self._picker_cb)

        body.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("保存")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def refresh_current_pack(self, current_pack: str = "") -> None:
        self._char_panel.refresh(current_pack)

    def run_mode_selected(self) -> str:
        return self._run_mode

    def run_mode_changed(self) -> bool:
        return self._run_mode != self._initial_run_mode

    def companion_enabled_selected(self) -> bool:
        return self._companion_cb.isChecked()

    def companion_enabled_changed(self) -> bool:
        return self.companion_enabled_selected() != self._initial_companion_enabled

    def chat_api_config(self) -> ChatApiConfig:
        return ChatApiConfig(
            api_key=self._api_key.text().strip(),
            base_url=self._api_base.text().strip(),
            model=self._api_model.text().strip(),
        )

    def show_character_picker(self) -> bool:
        return self._picker_cb.isChecked()

    def max_height_selected(self) -> int:
        return clamp_character_height(self._size_slider.value())

    def max_height_changed(self) -> bool:
        return self.max_height_selected() != self._initial_height

    def _update_size_label(self, value: int) -> None:
        self._size_label.setText(f"{value} px")

    def _on_size_slider(self, value: int) -> None:
        v = clamp_character_height(value)
        self._update_size_label(v)
        if self._on_height_preview:
            self._on_height_preview(v)

    def _on_mode_clicked(self, button_id: int) -> None:
        self._run_mode = "companion" if button_id == 1 else "entertainment"

    def reject(self) -> None:
        if self._on_height_preview and self.max_height_changed():
            self._on_height_preview(self._initial_height)
        super().reject()

    def _on_save(self) -> None:
        self._run_mode = "companion" if self._rb_companion.isChecked() else "entertainment"
        self._companion_enabled = self._companion_cb.isChecked()
        self.accept()


def run_settings_dialog(
    parent=None,
    *,
    on_height_preview: Callable[[int], None] | None = None,
    memory_lines: list[str] | None = None,
    companion_days: str = "",
    on_open_import_dialog: Callable[[], None] | None = None,
    on_open_switch_dialog: Callable[[], None] | None = None,
    current_pack: str = "",
) -> SettingsDialog | None:
    dlg = SettingsDialog(
        parent,
        on_height_preview=on_height_preview,
        memory_lines=memory_lines,
        companion_days=companion_days,
        on_open_import_dialog=on_open_import_dialog,
        on_open_switch_dialog=on_open_switch_dialog,
        current_pack=current_pack,
    )
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    return dlg
