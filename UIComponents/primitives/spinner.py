"""Loading indicator."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class Spinner(QtWidgets.QProgressBar):
    def __init__(self, *, size: str = "md", class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "Spinner")
        self.setRange(0, 0)
        height_map = {"sm": 6, "md": 8, "lg": 12}
        height = height_map.get(size, 8)
        self.setFixedHeight(height)
        self.setStyleSheet(
            f"QProgressBar#{self.objectName()} {{"
            f"background: {tokens.colors.surface_alt};"
            f"border-radius: {height // 2}px;"
            f"border: 1px solid {tokens.colors.border};"
            f"text-align: center;"
            "}"
            f"QProgressBar#{self.objectName()}::chunk {{"
            f"background: {tokens.colors.accent};"
            f"border-radius: {height // 2}px;"
            "}"
        )
