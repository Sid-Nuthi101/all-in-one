"""Neon divider primitive."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class NeonDivider(QtWidgets.QFrame):
    def __init__(self, *, orientation: str = "horizontal", class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "NeonDivider")
        if orientation == "vertical":
            self.setFixedWidth(2)
        else:
            self.setFixedHeight(2)
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 rgba(110, 231, 255, 0.0), stop:0.5 {tokens.colors.accent}, stop:1 rgba(110, 231, 255, 0.0));"
            "}}"
        )
