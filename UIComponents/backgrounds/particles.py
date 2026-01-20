"""Particle layer background component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class ParticleLayerBackground(QtWidgets.QFrame):
    def __init__(self, particle_count: int = 24, drift: float = 0.4, blur: float = 0.3, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "ParticleLayerBackground")
        opacity = 0.2 + blur * 0.2
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: qradialgradient(cx:0.2, cy:0.2, radius:1, "
            f"stop:0 rgba(110, 231, 255, {opacity}), "
            f"stop:1 rgba(10, 15, 31, 0.0));"
            f"color: {tokens.colors.text_primary};"
            "}}"
        )
        self.particle_count = particle_count
        self.drift = drift
        self.blur = blur
