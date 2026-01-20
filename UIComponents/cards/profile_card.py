from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

from ..core.tokens import TOKENS
from ..core.styles import apply_glass_panel


class ProfileCard(QWidget):
  def __init__(
    self,
    name,
    last_message,
    timestamp,
    variant="default",
    size="md",
    is_selected=False,
    on_click=None,
    class_name=None,
    style_override=None,
  ):
    super().__init__()
    self.on_click = on_click
    self.setCursor(Qt.CursorShape.PointingHandCursor)
    apply_glass_panel(self, variant=variant, size=size, class_name=class_name, style_override=style_override)

    layout = QHBoxLayout()
    layout.setSpacing(TOKENS["spacing"]["sm"])
    layout.setContentsMargins(*([TOKENS["spacing"]["sm"]] * 4))
    self.setLayout(layout)

    avatar = QLabel(name[:1].upper())
    avatar.setFixedSize(36, 36)
    avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
    avatar.setStyleSheet(
      """
      QLabel {{
        border-radius: 18px;
        background: {accent_soft};
        color: {accent};
        font-weight: 600;
      }}
      """.format(
        accent_soft=TOKENS["color"]["accent_soft"],
        accent=TOKENS["color"]["accent"],
      )
    )

    text_stack = QVBoxLayout()
    text_stack.setSpacing(2)

    name_label = QLabel(name)
    name_label.setStyleSheet(
      "font-size: {size}px; font-weight: 600;".format(size=TOKENS["typography"]["title"])
    )

    message_label = QLabel(last_message)
    message_label.setStyleSheet(
      "color: {secondary}; font-size: {size}px;".format(
        secondary=TOKENS["color"]["text_secondary"],
        size=TOKENS["typography"]["body"],
      )
    )

    time_label = QLabel(timestamp)
    time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
    time_label.setStyleSheet(
      "color: {secondary}; font-size: {size}px;".format(
        secondary=TOKENS["color"]["text_secondary"],
        size=TOKENS["typography"]["caption"],
      )
    )

    text_stack.addWidget(name_label)
    text_stack.addWidget(message_label)

    layout.addWidget(avatar)
    layout.addLayout(text_stack)
    layout.addStretch()
    layout.addWidget(time_label)

    if is_selected:
      self.setStyleSheet(
        self.styleSheet()
        + "border: 1px solid {accent};".format(accent=TOKENS["color"]["accent"])
      )

  def mousePressEvent(self, event):
    if self.on_click:
      self.on_click()
    super().mousePressEvent(event)
