from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..core.tokens import COLORS


class Grid3DBackground(QWidget):
  """Perspective grid background component."""

  def __init__(self, depth: int = 12, glow_level: float = 0.45):
    super().__init__()
    self.depth = depth
    self.glow_level = glow_level
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    width = self.width()
    height = self.height()
    pen = QPen()
    pen.setWidthF(1)
    pen.setColor(COLORS.border_active)
    painter.setOpacity(self.glow_level)
    painter.setPen(pen)

    horizon = height * 0.35
    for i in range(1, self.depth + 1):
      ratio = i / self.depth
      y = horizon + (height - horizon) * ratio
      painter.drawLine(0, y, width, y)

    center_x = width / 2
    for i in range(-self.depth, self.depth + 1):
      offset = (i / self.depth) * width * 0.6
      painter.drawLine(center_x + offset, horizon, center_x + offset * 2, height)

    painter.end()
