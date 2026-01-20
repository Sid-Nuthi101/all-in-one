from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget

from ..core.tokens import TOKENS


class Grid3DBackground(QWidget):
  def __init__(self, depth=0.6, glow_level=0.5, class_name=None):
    super().__init__()
    self.depth = depth
    self.glow_level = glow_level
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    if class_name:
      self.setObjectName(class_name)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    base_color = QColor(TOKENS["color"]["accent"])
    base_color.setAlphaF(0.12 + 0.25 * self.glow_level)
    pen = QPen(base_color, 1)
    painter.setPen(pen)

    width = self.width()
    height = self.height()
    horizon = int(height * (0.35 + 0.2 * (1 - self.depth)))

    for i in range(12):
      y = horizon + i * (height - horizon) / 11
      painter.drawLine(0, int(y), width, int(y))

    for i in range(12):
      x = i * width / 11
      painter.drawLine(int(x), horizon, int(width / 2 + (x - width / 2) * (1.2)), height)
