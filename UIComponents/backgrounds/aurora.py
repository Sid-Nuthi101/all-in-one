from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QLinearGradient, QPainter
from PySide6.QtWidgets import QWidget

from ..core.assets import GRADIENT_PRESETS


class AuroraGradientBackground(QWidget):
  """Gradient aurora background component."""

  def __init__(self, palette: str = "nebula", motion_level: float = 0.35):
    super().__init__()
    self.palette = palette
    self.motion_level = motion_level
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    gradient = QLinearGradient(0, 0, self.width(), self.height())
    preset = next((preset for preset in GRADIENT_PRESETS if preset.name == self.palette), GRADIENT_PRESETS[0])
    for index, color in enumerate(preset.colors):
      gradient.setColorAt(index / max(len(preset.colors) - 1, 1), color)
    painter.fillRect(self.rect(), QBrush(gradient))
    painter.end()
