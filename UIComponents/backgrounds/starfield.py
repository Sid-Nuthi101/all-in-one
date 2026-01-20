"""Starfield background component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class StarfieldBackground(QtWidgets.QFrame):
    def __init__(self, intensity: float = 0.6, speed: float = 0.4, density: int = 80, *, class_name: str = "", tokens=None):
        super().__init__()
        self.intensity = intensity
        self.speed = speed
        self.density = density
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "StarfieldBackground")
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: qradialgradient(cx:0.5, cy:0.5, radius:1, "
            f"stop:0 rgba(110, 231, 255, {self.intensity}), "
            f"stop:1 {tokens.colors.background});"
            "}}"
        )
