"""Perspective grid background component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class Grid3DBackground(QtWidgets.QFrame):
    def __init__(self, depth: float = 0.5, glow_level: float = 0.4, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "Grid3DBackground")
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: repeating-linear-gradient("
            f"0deg, rgba(110, 231, 255, {0.12 + glow_level * 0.2}) 0px, "
            f"rgba(110, 231, 255, {0.12 + glow_level * 0.2}) 1px, "
            f"transparent 1px, transparent {20 - depth * 10}px);"
            f"color: {tokens.colors.text_primary};"
            "}}"
        )
