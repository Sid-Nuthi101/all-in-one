from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from ..core.tokens import TOKENS
from ..core.styles import apply_glass_panel


class MessageBubble(QWidget):
  def __init__(
    self,
    text,
    timestamp,
    is_outgoing=False,
    variant="default",
    size="md",
    class_name=None,
    style_override=None,
  ):
    super().__init__()
    apply_glass_panel(self, variant=variant, size=size, class_name=class_name, style_override=style_override)

    layout = QVBoxLayout()
    layout.setContentsMargins(*([TOKENS["spacing"]["sm"]] * 4))
    layout.setSpacing(4)
    self.setLayout(layout)

    text_label = QLabel(text)
    text_label.setWordWrap(True)
    text_label.setStyleSheet(
      "font-size: {size}px;".format(size=TOKENS["typography"]["body"])
    )

    time_label = QLabel(timestamp)
    time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    time_label.setStyleSheet(
      "color: {secondary}; font-size: {size}px;".format(
        secondary=TOKENS["color"]["text_secondary"],
        size=TOKENS["typography"]["caption"],
      )
    )

    layout.addWidget(text_label)
    layout.addWidget(time_label)

    if is_outgoing:
      self.setStyleSheet(
        self.styleSheet()
        + "background: rgba(26, 36, 66, 0.7); border: 1px solid rgba(125, 209, 255, 0.3);"
      )
      layout.setAlignment(Qt.AlignmentFlag.AlignRight)
