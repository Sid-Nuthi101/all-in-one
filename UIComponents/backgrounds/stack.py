from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedLayout, QWidget

from .aurora import AuroraGradientBackground
from .grid3d import Grid3DBackground
from .particles import ParticleLayerBackground
from .starfield import StarfieldBackground


class BackgroundStack(QWidget):
  """Composite background: gradient + grid + particles + starfield."""

  def __init__(self):
    super().__init__()
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    layout = QStackedLayout()
    layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

    self._aurora = AuroraGradientBackground()
    self._grid = Grid3DBackground()
    self._particles = ParticleLayerBackground()
    self._stars = StarfieldBackground()

    layout.addWidget(self._aurora)
    layout.addWidget(self._grid)
    layout.addWidget(self._particles)
    layout.addWidget(self._stars)

    self.setLayout(layout)

  def set_intensity(self, glow_level: float = 0.45, density: int = 80):
    self._grid.glow_level = glow_level
    self._stars.density = density
    self._stars._stars = self._stars._generate_stars()
    self.update()
