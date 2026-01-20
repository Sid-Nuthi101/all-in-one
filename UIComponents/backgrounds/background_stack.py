"""Background stack composition."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from .aurora import AuroraGradientBackground
from .grid3d import Grid3DBackground
from .particles import ParticleLayerBackground
from .vignette import VignetteOverlay


class BackgroundStack(QtWidgets.QFrame):
    def __init__(self, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "BackgroundStack")
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{background: {tokens.colors.background};}}"
        )
        layout = QtWidgets.QStackedLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        layout.addWidget(AuroraGradientBackground(tokens=tokens))
        layout.addWidget(Grid3DBackground(tokens=tokens))
        layout.addWidget(ParticleLayerBackground(tokens=tokens))
        layout.addWidget(VignetteOverlay(tokens=tokens))
