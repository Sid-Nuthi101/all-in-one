import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

from ..core.tokens import TOKENS


class StarfieldBackground(QWidget):
  def __init__(self, intensity=0.6, speed=0.2, density=120, class_name=None):
    super().__init__()
    self.intensity = intensity
    self.speed = speed
    self.density = density
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    if class_name:
      self.setObjectName(class_name)
    self._stars = self._generate_stars()

  def _generate_stars(self):
    rng = random.Random(42)
    return [
      (rng.random(), rng.random(), rng.uniform(0.6, 1.8))
      for _ in range(self.density)
    ]

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    color = QColor(TOKENS["color"]["accent"])
    color.setAlphaF(0.2 + 0.6 * self.intensity)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)

    width = self.width()
    height = self.height()
    for x_ratio, y_ratio, size in self._stars:
      x = int(width * x_ratio)
      y = int(height * y_ratio)
      painter.drawEllipse(x, y, size, size)
