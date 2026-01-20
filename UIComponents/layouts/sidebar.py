from __future__ import annotations

from typing import Callable, Iterable, Optional

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from ..cards.profile_card import ProfileCard
from ..core.styles import apply_glass_panel
from ..core.tokens import COLORS, SPACING, TYPOGRAPHY


class Sidebar(QWidget):
  """Futuristic sidebar navigation with profile cards."""

  def __init__(
    self,
    title: str,
    items: Iterable[dict],
    *,
    on_select: Optional[Callable[[dict], None]] = None,
    class_name: str = "",
  ):
    super().__init__()
    self.setObjectName(class_name)
    apply_glass_panel(self)

    layout = QVBoxLayout()
    layout.setContentsMargins(SPACING.lg, SPACING.lg, SPACING.lg, SPACING.lg)
    layout.setSpacing(SPACING.lg)

    title_label = QLabel(title)
    title_label.setStyleSheet(
      f"color: {COLORS.text_primary}; font-size: {TYPOGRAPHY.title_size + 2}px; font-weight: 600;"
    )

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)

    list_container = QWidget()
    list_layout = QVBoxLayout()
    list_layout.setContentsMargins(0, 0, 0, 0)
    list_layout.setSpacing(SPACING.sm)

    for item in items:
      card = ProfileCard(
        name=item.get("name", "Unknown"),
        last_message=item.get("last_message", ""),
        timestamp=item.get("timestamp", ""),
        avatar_text=item.get("avatar_text", "?"),
        is_selected=item.get("is_selected", False),
        on_click=lambda data=item: on_select(data) if on_select else None,
      )
      list_layout.addWidget(card)

    list_layout.addStretch()
    list_container.setLayout(list_layout)
    scroll.setWidget(list_container)

    layout.addWidget(title_label)
    layout.addWidget(scroll)

    self.setLayout(layout)
