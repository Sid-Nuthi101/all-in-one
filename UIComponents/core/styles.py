from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from .tokens import TOKENS


def glass_panel_style(variant="default"):
  colors = TOKENS["color"]
  base = colors["panel"] if variant == "default" else colors["panel_strong"]
  return """
    QWidget {{
      background: {base};
      border: 1px solid {border};
      border-radius: {radius}px;
      color: {text_primary};
    }}
  """.format(
    base=base,
    border=colors["border"],
    radius=TOKENS["radius"]["md"],
    text_primary=colors["text_primary"],
  )


def apply_glass_panel(widget, variant="default", size="md", class_name=None, style_override=None):
  if class_name:
    widget.setObjectName(class_name)

  style = glass_panel_style(variant)
  if style_override:
    style = f"{style}\n{style_override}"

  widget.setStyleSheet(style)

  shadow = QGraphicsDropShadowEffect(widget)
  shadow.setBlurRadius(24)
  shadow.setXOffset(0)
  shadow.setYOffset(10)
  shadow_color = TOKENS["shadow"]["soft"]
  shadow.setColor(QColor(*shadow_color))
  widget.setGraphicsEffect(shadow)
  widget.setContentsMargins(*([TOKENS["spacing"]["md"]] * 4))
  return widget
