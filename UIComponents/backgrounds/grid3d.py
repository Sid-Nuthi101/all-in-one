from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget, QSizePolicy

from ..core.tokens import COLORS


class Grid3DBackground(QWidget):
  """Perspective grid background component."""

  def __init__(self, depth: int = 12, glow_level: float = 0.45):
    super().__init__()
    self.depth = depth
    self.glow_level = glow_level

    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.setMinimumHeight(180)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    width = self.width()
    height = self.height()
    if width <= 1 or height <= 1:
      return

    pen = QPen(QColor(COLORS.border_active))
    pen.setWidthF(1.0)
    painter.setPen(pen)

    horizon = height * 0.35
    vanish_x = width / 2
    vanish_y = horizon

    # horizontal depth lines (fade toward horizon)
    for i in range(1, self.depth + 1):
      ratio = i / self.depth
      y = horizon + (height - horizon) * ratio
      painter.setOpacity(self.glow_level * (0.10 + 0.90 * ratio))
      painter.drawLine(0, int(y), width, int(y))

    # perspective vertical lines converging to vanishing point
    for i in range(-self.depth, self.depth + 1):
      t = i / self.depth
      x_bottom = width / 2 + t * width * 0.9
      painter.setOpacity(self.glow_level * 0.9)
      painter.drawLine(int(x_bottom), height, int(vanish_x), int(vanish_y))
