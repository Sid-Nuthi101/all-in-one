from __future__ import annotations

import random
from dataclasses import dataclass

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from ..core.tokens import COLORS


@dataclass
class _Particle:
  x: float
  y: float
  vx: float
  vy: float
  r: float
  a: float


class ParticleLayerBackground(QWidget):
  """Lightweight particle layer background component."""

  def __init__(
    self,
    particle_count: int = 32,
    drift: float = 0.15,
    blur: float = 0.25,
    fps: int = 30,
  ):
    super().__init__()
    self.particle_count = particle_count
    self.drift = drift
    self.blur = blur
    self._base_color = QColor(COLORS.glow)

    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    self._particles = [self._make_particle() for _ in range(particle_count)]

    self._timer = QTimer(self)
    self._timer.timeout.connect(self._tick)
    self._timer.start(max(1, int(1000 / max(1, fps))))

  def _make_particle(self) -> _Particle:
    # Positions are normalized [0,1] so resizing doesn't break distribution.
    x = random.random()
    y = random.random()

    # Small velocities; drift scales the max speed.
    speed = (0.015 + random.random() * 0.04) * max(0.0, self.drift)
    angle = random.random() * 6.283185307179586  # 2*pi
    vx = speed * (random.random() * 2 - 1)
    vy = speed * (random.random() * 2 - 1)

    # Radius + alpha variance
    r = 1.5 + random.random() * 2.5
    a = 0.10 + random.random() * 0.35

    return _Particle(x=x, y=y, vx=vx, vy=vy, r=r, a=a)

  def _tick(self) -> None:
    # Update normalized positions and wrap around edges.
    for p in self._particles:
      p.x = (p.x + p.vx) % 1.0
      p.y = (p.y + p.vy) % 1.0
    self.update()

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    w = self.width()
    h = self.height()
    if w <= 1 or h <= 1:
      return

    painter.setPen(Qt.PenStyle.NoPen)

    # Global layer opacity multiplier (keep it subtle).
    layer_opacity = max(0.0, min(1.0, 0.25 + self.blur * 0.35))

    for p in self._particles:
      c = QColor(self._base_color)
      # Per-particle alpha + layer multiplier
      c.setAlphaF(max(0.0, min(1.0, p.a * layer_opacity)))
      painter.setBrush(c)
      painter.drawEllipse(p.x * w, p.y * h, p.r * 2, p.r * 2)

    painter.end()
