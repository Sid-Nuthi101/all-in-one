import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

from ..core.tokens import TOKENS


class ParticleLayerBackground(QWidget):
  def __init__(self, particle_count=80, drift=0.4, blur=0.8, class_name=None):
    super().__init__()
    self.particle_count = particle_count
    self.drift = drift
    self.blur = blur
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    if class_name:
      self.setObjectName(class_name)
    self._particles = self._generate_particles()

  def _generate_particles(self):
    rng = random.Random(99)
    return [
      (rng.random(), rng.random(), rng.uniform(4, 12))
      for _ in range(self.particle_count)
    ]

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    color = QColor(TOKENS["color"]["accent"])
    color.setAlphaF(0.08 + 0.2 * self.drift)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)

    width = self.width()
    height = self.height()
    for x_ratio, y_ratio, radius in self._particles:
      x = int(width * x_ratio)
      y = int(height * y_ratio)
      painter.drawEllipse(x, y, radius, radius)
