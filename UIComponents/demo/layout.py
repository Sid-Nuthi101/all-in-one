from PySide6.QtWidgets import QWidget, QStackedLayout

from ..backgrounds.stack import BackgroundStack
from ..layouts.sidebar import Sidebar
from ..layouts.messages import MessagesView
from ..layouts.split_pane import SplitPane


def build_demo():
  profiles = [
    {
      "name": "Nova Shaw",
      "last_message": "See you at 8?",
      "timestamp": "2m",
      "is_selected": True,
    },
    {
      "name": "Kai Reed",
      "last_message": "Draft is ready to review.",
      "timestamp": "8m",
    },
    {
      "name": "Lena Ortiz",
      "last_message": "Sending the files now.",
      "timestamp": "1h",
    },
  ]

  messages = [
    {"text": "Hey! Did you see the new glass UI build?", "timestamp": "7:45 PM"},
    {"text": "Yes, it looks incredible. The glow is perfect.", "timestamp": "7:46 PM", "is_outgoing": True},
    {"text": "Let’s lock the spacing tokens next.", "timestamp": "7:47 PM"},
    {"text": "Already on it — sending in a minute.", "timestamp": "7:48 PM", "is_outgoing": True},
  ]

  sidebar = Sidebar(items=profiles, title="Conversations")
  message_view = MessagesView(title="Nova Shaw", subtitle="Active now", messages=messages)
  split = SplitPane(left=sidebar, right=message_view)

  root = QWidget()
  layout = QStackedLayout()
  layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
  root.setLayout(layout)

  layout.addWidget(BackgroundStack())
  layout.addWidget(split)
  return root
