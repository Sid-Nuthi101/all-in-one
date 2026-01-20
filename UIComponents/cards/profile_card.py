from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget

from ..core.styles import apply_glass_panel
from ..core.tokens import COLORS, RADII, SPACING, TYPOGRAPHY


class ProfileCard(QWidget):
  """Glassmorphism profile card component."""

  def __init__(
    self,
    name: str,
    last_message: str,
    timestamp: str,
    *,
    avatar_text: str = "?",
    is_selected: bool = False,
    is_disabled: bool = False,
    on_click: Optional[Callable[[], None]] = None,
    class_name: str = "",
  ):
    super().__init__()
    self.on_click = on_click
    self.is_disabled = is_disabled
    self.setObjectName(class_name)
    apply_glass_panel(self, is_active=is_selected, is_disabled=is_disabled, padding=SPACING.md)

    layout = QHBoxLayout()
    layout.setContentsMargins(SPACING.sm, SPACING.sm, SPACING.sm, SPACING.sm)
    layout.setSpacing(SPACING.sm)

    avatar = QLabel(avatar_text)
    avatar.setFixedSize(32, 32)
    avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
    avatar.setStyleSheet(
      f"""
      QLabel {{
        background: {COLORS.surface_light};
        border-radius: {RADII.md}px;
        color: {COLORS.text_primary};
        font-weight: 600;
      }}
      """.strip()
    )

    text_layout = QVBoxLayout()
    name_label = QLabel(name)
    name_label.setStyleSheet(f"color: {COLORS.text_primary}; font-size: {TYPOGRAPHY.title_size}px;")

    message_label = QLabel(last_message)
    message_label.setStyleSheet(f"color: {COLORS.text_secondary}; font-size: {TYPOGRAPHY.body_size}px;")

    text_layout.addWidget(name_label)
    text_layout.addWidget(message_label)

    time_label = QLabel(timestamp)
    time_label.setStyleSheet(f"color: {COLORS.text_secondary}; font-size: {TYPOGRAPHY.caption_size}px;")

    layout.addWidget(avatar)
    layout.addLayout(text_layout)
    layout.addStretch()
    layout.addWidget(time_label)

    self.setLayout(layout)
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    if is_disabled:
      self.setCursor(Qt.CursorShape.ForbiddenCursor)
      self.setEnabled(False)

  def mousePressEvent(self, event):
    if self.on_click and not self.is_disabled:
      self.on_click()
    super().mousePressEvent(event)
