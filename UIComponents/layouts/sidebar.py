from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea

from ..core.tokens import TOKENS
from ..core.styles import apply_glass_panel
from ..cards.profile_card import ProfileCard


class Sidebar(QWidget):
  def __init__(
    self,
    items,
    title="Messages",
    variant="default",
    size="md",
    on_profile_click=None,
    class_name=None,
    style_override=None,
  ):
    super().__init__()
    apply_glass_panel(self, variant=variant, size=size, class_name=class_name, style_override=style_override)

    layout = QVBoxLayout()
    layout.setContentsMargins(*([TOKENS["spacing"]["md"]] * 4))
    layout.setSpacing(TOKENS["spacing"]["sm"])
    self.setLayout(layout)

    header = QLabel(title)
    header.setStyleSheet(
      "font-size: {size}px; font-weight: 600;".format(size=TOKENS["typography"]["title"])
    )

    layout.addWidget(header)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    list_container = QWidget()
    list_layout = QVBoxLayout()
    list_layout.setSpacing(TOKENS["spacing"]["sm"])
    list_layout.setContentsMargins(0, 0, 0, 0)
    list_container.setLayout(list_layout)

    for item in items:
      card = ProfileCard(
        name=item["name"],
        last_message=item["last_message"],
        timestamp=item["timestamp"],
        is_selected=item.get("is_selected", False),
        on_click=(lambda name=item["name"]: on_profile_click(name) if on_profile_click else None),
      )
      list_layout.addWidget(card)

    list_layout.addStretch()
    scroll.setWidget(list_container)
    layout.addWidget(scroll)

    self.setMinimumWidth(260)
