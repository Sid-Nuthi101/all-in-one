from __future__ import annotations

import random

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ..core.tokens import COLORS


class ParticleLayerBackground(QWidget):
  """Lightweight particle layer background component."""

  def __init__(self, particle_count: int = 32, drift: float = 0.15, blur: float = 0.25):
    super().__init__()
    self.particle_count = particle_count
    self.drift = drift
    self.blur = blur
    self._particles = [QPointF(random.random(), random.random()) for _ in range(particle_count)]
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    width = self.width()
    height = self.height()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(COLORS.glow))
    painter.setOpacity(0.35 + self.blur)
    for point in self._particles:
      painter.drawEllipse(QPointF(point.x() * width, point.y() * height), 3, 3)
    painter.end()
