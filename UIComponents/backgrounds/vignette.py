"""Vignette overlay component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class VignetteOverlay(QtWidgets.QFrame):
    def __init__(self, strength: float = 0.4, radius: float = 0.9, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "VignetteOverlay")
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: qradialgradient(cx:0.5, cy:0.5, radius:{radius}, "
            f"stop:0 rgba(0, 0, 0, 0.0), stop:1 rgba(0, 0, 0, {strength}));"
            f"color: {tokens.colors.text_primary};"
            "}}"
        )
