from PySide6.QtWidgets import QWidget, QStackedLayout

from .aurora import AuroraGradientBackground
from .grid3d import Grid3DBackground
from .particles import ParticleLayerBackground
from .starfield import StarfieldBackground
from ..core.assets import vignette_style


class BackgroundStack(QWidget):
  def __init__(self, class_name=None):
    super().__init__()
    if class_name:
      self.setObjectName(class_name)

    layout = QStackedLayout()
    layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
    self.setLayout(layout)

    layout.addWidget(AuroraGradientBackground())
    layout.addWidget(Grid3DBackground())
    layout.addWidget(StarfieldBackground())
    layout.addWidget(ParticleLayerBackground())

    vignette = QWidget()
    vignette.setStyleSheet(vignette_style())
    layout.addWidget(vignette)
