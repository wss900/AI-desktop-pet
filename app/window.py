"""Frameless pet window — sprite + HP bar; right-click spawns draggable food."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QPoint, Qt, QRect
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QLabel, QMenu, QVBoxLayout, QWidget

from app.feed_popup import FeedPopupLabel
from app.speech_bubble import SpeechBubbleLabel
from app.hp_bar import HpBarWidget
from config.settings import PET_HEIGHT, PET_WIDTH
from pet.character_assets import CharacterAssets
from pet.controller import PetController
from pet.vitality_art import make_skeleton_pixmap


class PetWindow(QWidget):
    def __init__(
        self,
        controller: PetController,
        character: CharacterAssets | None = None,
        on_open_chat=None,
        on_spawn_food: Callable[[], None] | None = None,
        on_advance_hour: Callable[[], None] | None = None,
        survival_mode: bool | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._controller = controller
        self._character = character
        self._on_open_chat = on_open_chat
        self._on_spawn_food = on_spawn_food
        self._on_advance_hour = on_advance_hour
        self._survival_mode = (
            True if survival_mode is None else survival_mode
        )
        self._drag_offset: QPoint | None = None
        self._starved = False
        self._skeleton_pix: QPixmap | None = None
        self._sprite_connected = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        tip = "左键拖动 · 双击聊天"
        if self._survival_mode:
            tip = "右键：生成食物 / 加速一小时\n" + tip
        self.setToolTip(tip)

        self._hp_bar = HpBarWidget(self)
        self._hp_bar.set_survival_visible(self._survival_mode)
        self._feed_popup = FeedPopupLabel(self)
        self._speech_bubble = SpeechBubbleLabel(self)
        self._sprite = QLabel(self)
        self._sprite.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._sprite.setScaledContents(False)
        self._sprite.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._hp_bar)
        layout.addWidget(self._sprite, 1)

        w = character.width if character and character.is_ready else PET_WIDTH
        h = character.height if character and character.is_ready else PET_HEIGHT
        self._resize_for_sprite(w, h)

        if character:
            self._connect_character()
            self._on_pixmap(character.current_pixmap())
        else:
            from pet.animator import PetSprite

            self._legacy_sprite = PetSprite()
            self._legacy_sprite.hide()
            controller.state_changed.connect(self._legacy_sprite.set_state)
            controller.facing_changed.connect(self._legacy_sprite.set_facing)
            self._legacy_sprite._anim_timer.timeout.connect(
                lambda: self._on_pixmap(self._legacy_sprite.current_pixmap())
            )
            self._on_pixmap(self._legacy_sprite.current_pixmap())

        controller.position_changed.connect(self._on_position)
        if character and character.is_ready:
            controller.facing_changed.connect(character.set_facing)

        self._place_center()
        self.move(controller.position.x(), controller.position.y())

    def _connect_character(self) -> None:
        if not self._character or self._sprite_connected:
            return
        self._character.pixmap_changed.connect(self._on_pixmap)
        self._character.size_changed.connect(self._on_size)
        self._sprite_connected = True

    def _disconnect_character(self) -> None:
        if not self._character or not self._sprite_connected:
            return
        try:
            self._character.pixmap_changed.disconnect(self._on_pixmap)
            self._character.size_changed.disconnect(self._on_size)
        except RuntimeError:
            pass
        self._sprite_connected = False

    def _resize_for_sprite(self, w: int, h: int) -> None:
        bar_h = self._hp_bar.height() if self._survival_mode else 0
        spacing = 4 if self._survival_mode else 0
        total_h = h + bar_h + spacing
        self.setFixedSize(w, total_h)
        self._controller.set_size(w, total_h)
        if self._feed_popup.isVisible():
            self._position_feed_popup()
        if self._speech_bubble.isVisible():
            self._position_speech_bubble()

    def update_hp(self, hp: float, hp_max: float, starved: bool = False) -> None:
        """由 vitality.hp_changed 连接；第三参须为位置参数，勿用 keyword-only。"""
        self._hp_bar.set_hp(hp, hp_max, starved=starved)
        self._hp_bar.repaint()

    def show_hp_delta(self, delta: float, *, hp: float = 0, starved: bool = False) -> None:
        if delta == 0 or not self._survival_mode:
            return
        from app.hp_bar import _hp_tier_color

        if delta > 0:
            text = f"+{int(delta)}" if delta == int(delta) else f"+{delta:.1f}"
            color = _hp_tier_color(hp, starved=starved)
        else:
            text = f"{int(delta)}" if delta == int(delta) else f"{delta:.1f}"
            color = QColor(220, 70, 65)
        self._feed_popup.show_bonus(text, color=color)
        self._position_feed_popup()

    def show_feed_bonus(self, delta: float, *, hp: float = 0, starved: bool = False) -> None:
        self.show_hp_delta(delta, hp=hp, starved=starved)

    def show_speech_bubble(
        self,
        text: str,
        *,
        duration_ms: int = 6000,
        clickable: bool = False,
        on_click: Callable[[], None] | None = None,
    ) -> None:
        self._speech_bubble.show_message(
            text,
            duration_ms=duration_ms,
            clickable=clickable,
            on_click=on_click,
        )
        self._position_speech_bubble()

    def _position_speech_bubble(self) -> None:
        bar_h = self._hp_bar.height() if self._survival_mode else 0
        x = max(0, (self.width() - self._speech_bubble.width()) // 2)
        y = max(0, bar_h - self._speech_bubble.height() - 4)
        self._speech_bubble.move(x, y)

    def _position_feed_popup(self) -> None:
        bar_h = self._hp_bar.height()
        x = max(0, (self.width() - self._feed_popup.width()) // 2)
        y = max(0, bar_h - 2)
        self._feed_popup.move(x, y)

    def set_starved(self, starved: bool) -> None:
        self._starved = starved
        if starved:
            self._disconnect_character()
            if self._character:
                self._character.stop()
            w = self._sprite.width() or PET_WIDTH
            h = self._sprite.height() or PET_HEIGHT
            sk = make_skeleton_pixmap(w, h)
            self._skeleton_pix = sk
            self._sprite.setPixmap(sk)
        else:
            self._skeleton_pix = None
            if self._character:
                self._connect_character()
                self._character.resume()
                self._on_pixmap(self._character.current_pixmap())

    def _on_size(self, w: int, h: int) -> None:
        if self._starved:
            sk = make_skeleton_pixmap(w, h)
            self._skeleton_pix = sk
            self._sprite.setPixmap(sk)
        self._resize_for_sprite(w, h)

    def _on_pixmap(self, pix: QPixmap) -> None:
        if self._starved:
            return
        if pix and not pix.isNull():
            self._sprite.setPixmap(pix)
            self.repaint_sprite()

    def repaint_sprite(self) -> None:
        self._sprite.update()
        self._sprite.repaint()
        self.update()

    def _place_center(self) -> None:
        self._controller.center_on_screen()

    def _on_position(self, x: int, y: int) -> None:
        self.move(x, y)

    def enterEvent(self, event):
        if self._character and not self._starved:
            self._character.set_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._character and not self._starved:
            self._character.set_hover(False)
        super().leaveEvent(event)

    def contextMenuEvent(self, event):
        if not self._survival_mode:
            event.accept()
            return
        menu = QMenu(self)
        act_food = menu.addAction("生成食物")
        act_hour = menu.addAction("加速一小时")
        chosen = menu.exec(event.globalPos())
        if chosen == act_food and self._on_spawn_food:
            self._on_spawn_food()
        elif chosen == act_hour and self._on_advance_hour:
            self._on_advance_hour()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            self._controller.start_drag()
            if self._character and not self._starved:
                self._character.set_dragging(True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            pos = event.globalPosition().toPoint() - self._drag_offset
            self._controller.set_position(pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            self._controller.end_drag()
            if self._character and not self._starved:
                self._character.set_dragging(False)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._on_open_chat:
            self._on_open_chat()
        super().mouseDoubleClickEvent(event)

    def show_pet(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def pet_hit_global_rect(self) -> QRect:
        return self.frameGeometry()
