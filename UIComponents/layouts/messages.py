from __future__ import annotations

from typing import Callable, Iterable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from UIComponents.cards.message_bubbles import MessageBubble, MessageBubbleRow
from UIComponents.core.styles import apply_glass_panel, pill_button_style
from UIComponents.core.tokens import COLORS, SPACING, TYPOGRAPHY


class MessageWindow(QWidget):
  """Message window layout with header and message feed."""

  def __init__(
    self,
    title: str,
    messages: Iterable[dict],
    *,
    on_info_click: Optional[Callable[[], None]] = None,
    class_name: str = "",
  ):
    super().__init__()
    self.setObjectName(class_name)
    apply_glass_panel(self, padding=SPACING.lg)

    layout = QVBoxLayout()
    layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
    layout.setSpacing(SPACING.lg)

    header = QWidget()
    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(SPACING.md)

    title_label = QLabel(title)
    title_label.setStyleSheet(
      f"color: {COLORS.text_primary}; font-size: {TYPOGRAPHY.title_size + 4}px; font-weight: 600;"
    )

    info_button = QPushButton("i")
    info_button.setFixedSize(32, 32)
    info_button.setStyleSheet(pill_button_style())
    if on_info_click:
      info_button.clicked.connect(on_info_click)

    header_layout.addWidget(title_label)
    header_layout.addStretch()
    header_layout.addWidget(info_button, alignment=Qt.AlignmentFlag.AlignRight)
    header.setLayout(header_layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)

    feed = QWidget()
    feed_layout = QVBoxLayout()
    feed_layout.setContentsMargins(0, 0, 0, 0)
    feed_layout.setSpacing(SPACING.md)

    for entry in messages:
      bubble = MessageBubble(
        text=entry.get("text", ""),
        is_own=entry.get("is_own", False),
        timestamp=entry.get("timestamp", ""),
        variant="secondary" if entry.get("is_own", False) else "primary",
      )
      row = MessageBubbleRow(bubble, is_own=entry.get("is_own", False))
      feed_layout.addWidget(row)

    feed_layout.addStretch()
    feed.setLayout(feed_layout)
    scroll.setWidget(feed)

    layout.addWidget(header)
    layout.addWidget(scroll)

    self.setLayout(layout)
