from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea

from ..core.tokens import TOKENS
from ..core.styles import apply_glass_panel
from ..cards.message_bubbles import MessageBubble


class MessagesView(QWidget):
  def __init__(
    self,
    title,
    subtitle,
    messages=None,
    variant="default",
    size="md",
    on_info=None,
    class_name=None,
    style_override=None,
  ):
    super().__init__()
    apply_glass_panel(self, variant=variant, size=size, class_name=class_name, style_override=style_override)

    layout = QVBoxLayout()
    layout.setContentsMargins(*([TOKENS["spacing"]["md"]] * 4))
    layout.setSpacing(TOKENS["spacing"]["sm"])
    self.setLayout(layout)

    header = QHBoxLayout()
    title_stack = QVBoxLayout()

    title_label = QLabel(title)
    title_label.setStyleSheet(
      "font-size: {size}px; font-weight: 600;".format(size=TOKENS["typography"]["title"])
    )
    subtitle_label = QLabel(subtitle)
    subtitle_label.setStyleSheet(
      "color: {secondary}; font-size: {size}px;".format(
        secondary=TOKENS["color"]["text_secondary"],
        size=TOKENS["typography"]["caption"],
      )
    )

    title_stack.addWidget(title_label)
    title_stack.addWidget(subtitle_label)

    info_button = QPushButton("i")
    info_button.setFixedSize(28, 28)
    info_button.clicked.connect(lambda: on_info() if on_info else None)
    info_button.setStyleSheet(
      """
      QPushButton {{
        background: {accent_soft};
        color: {accent};
        border-radius: 14px;
        border: 1px solid {border};
      }}
      QPushButton:hover {{
        border: 1px solid {accent};
      }}
      """.format(
        accent_soft=TOKENS["color"]["accent_soft"],
        accent=TOKENS["color"]["accent"],
        border=TOKENS["color"]["border"],
      )
    )

    header.addLayout(title_stack)
    header.addStretch()
    header.addWidget(info_button)

    layout.addLayout(header)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    message_container = QWidget()
    message_layout = QVBoxLayout()
    message_layout.setSpacing(TOKENS["spacing"]["sm"])
    message_layout.setContentsMargins(0, 0, 0, 0)
    message_container.setLayout(message_layout)

    for message in messages or []:
      bubble = MessageBubble(
        text=message["text"],
        timestamp=message["timestamp"],
        is_outgoing=message.get("is_outgoing", False),
      )
      bubble_layout = QHBoxLayout()
      if message.get("is_outgoing", False):
        bubble_layout.addStretch()
        bubble_layout.addWidget(bubble)
      else:
        bubble_layout.addWidget(bubble)
        bubble_layout.addStretch()
      wrapper = QWidget()
      wrapper.setLayout(bubble_layout)
      message_layout.addWidget(wrapper)

    message_layout.addStretch()
    scroll.setWidget(message_container)

    layout.addWidget(scroll)
