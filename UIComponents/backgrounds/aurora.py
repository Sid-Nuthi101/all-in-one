from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtWidgets import QWidget

from ..core.assets import BACKGROUND_PRESETS


class AuroraGradientBackground(QWidget):
  def __init__(self, palette=None, motion_level=0.4, class_name=None):
    super().__init__()
    self.palette = palette or BACKGROUND_PRESETS["aurora"]
    self.motion_level = motion_level
    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    if class_name:
      self.setObjectName(class_name)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    gradient = QLinearGradient(0, 0, self.width(), self.height())

    step = 1 / max(len(self.palette) - 1, 1)
    for index, color in enumerate(self.palette):
      qcolor = QColor(color)
      qcolor.setAlphaF(0.22 + 0.25 * self.motion_level)
      gradient.setColorAt(index * step, qcolor)

    painter.fillRect(self.rect(), gradient)
