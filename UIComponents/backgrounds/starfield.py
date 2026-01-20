from __future__ import annotations

import random
from dataclasses import dataclass

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import QWidget

from ..core.tokens import COLORS


@dataclass
class Star:
  position: QPointF
  radius: float
  alpha: float


class StarfieldBackground(QWidget):
  """Lightweight starfield background."""

  def __init__(self, intensity: float = 0.6, speed: float = 0.2, density: int = 80):
    super().__init__()
    self.intensity = intensity
    self.speed = speed
    self.density = density
    self._stars = self._generate_stars()
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

  def _generate_stars(self) -> list[Star]:
    stars: list[Star] = []
    for _ in range(self.density):
      stars.append(
        Star(
          QPointF(random.random(), random.random()),
          radius=random.uniform(0.6, 1.8),
          alpha=random.uniform(0.35, 0.9),
        )
      )
    return stars

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    width = self.width()
    height = self.height()
    for star in self._stars:
      painter.setBrush(QBrush(QColor(COLORS.accent_alt)))
      painter.setPen(Qt.PenStyle.NoPen)
      alpha = int(255 * star.alpha * self.intensity)
      painter.setOpacity(alpha / 255)
      painter.drawEllipse(
        QPointF(star.position.x() * width, star.position.y() * height),
        star.radius,
        star.radius,
      )
    painter.end()
