from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QWidget

from ..backgrounds.stack import BackgroundStack
from ..layouts.messages import MessageWindow
from ..layouts.sidebar import Sidebar
from ..layouts.split_pane import SplitPane


class DemoLayout(QWidget):
  """Demo layout rendering sidebar and messages in a split pane."""

  def __init__(self):
    super().__init__()

    sample_profiles = [
      {
        "name": "Nova Garcia",
        "last_message": "New pulse signature detected.",
        "timestamp": "09:41",
        "avatar_text": "N",
        "is_selected": True,
      },
      {
        "name": "Kai Morgan",
        "last_message": "Drift path recalibrated.",
        "timestamp": "09:32",
        "avatar_text": "K",
      },
      {
        "name": "Luna Park",
        "last_message": "Meet at the docking bay.",
        "timestamp": "Yesterday",
        "avatar_text": "L",
      },
    ]

    sample_messages = [
      {"text": "We are synced to the new nav grid.", "timestamp": "09:38"},
      {"text": "Copy that. Routing energy to the core.", "timestamp": "09:39", "is_own": True},
      {"text": "Ready for jump in 3 minutes.", "timestamp": "09:40"},
      {"text": "All systems green on my side.", "timestamp": "09:40", "is_own": True},
    ]

    sidebar = Sidebar("Crew", sample_profiles)
    messages = MessageWindow("Nova Garcia", sample_messages)

    split = SplitPane(sidebar, messages)

    background = BackgroundStack()

    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(background)
    layout.addWidget(split)
    self.setLayout(layout)
