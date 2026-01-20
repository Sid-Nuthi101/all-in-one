from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget

from ..core.styles import apply_glass_panel
from ..core.tokens import COLORS, RADII, SPACING, TYPOGRAPHY


class MessageBubble(QWidget):
  """Glassmorphism message bubble component."""

  def __init__(
    self,
    text: str,
    *,
    is_own: bool = False,
    timestamp: str = "",
    variant: str = "primary",
    size: str = "md",
    class_name: str = "",
  ):
    super().__init__()
    self.setObjectName(class_name)
    padding = SPACING.md if size == "md" else SPACING.sm
    apply_glass_panel(self, variant=variant, radius=RADII.lg, padding=padding)

    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    text_label = QLabel(text)
    text_label.setWordWrap(True)
    text_label.setStyleSheet(f"font-size: {TYPOGRAPHY.body_size}px; color: {COLORS.text_primary};")

    layout.addWidget(text_label)

    if timestamp:
      time_label = QLabel(timestamp)
      time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
      time_label.setStyleSheet(f"font-size: {TYPOGRAPHY.caption_size}px; color: {COLORS.text_secondary};")
      layout.addWidget(time_label)

    self.setLayout(layout)


class MessageBubbleRow(QWidget):
  """Row wrapper to align message bubbles."""

  def __init__(self, bubble: MessageBubble, *, is_own: bool = False):
    super().__init__()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(SPACING.sm)
    if is_own:
      layout.addStretch()
      layout.addWidget(bubble)
    else:
      layout.addWidget(bubble)
      layout.addStretch()
    self.setLayout(layout)
