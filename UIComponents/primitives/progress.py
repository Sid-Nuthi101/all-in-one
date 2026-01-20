"""Progress indicators."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, value: int = 0, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "ProgressBar")
        self.setValue(value)
        self.setStyleSheet(
            f"QProgressBar#{self.objectName()} {{"
            f"background: {tokens.colors.surface_alt};"
            f"border-radius: {tokens.radius.sm}px;"
            f"border: 1px solid {tokens.colors.border};"
            f"text-align: center;"
            "}"
            f"QProgressBar#{self.objectName()}::chunk {{"
            f"background: {tokens.colors.accent};"
            f"border-radius: {tokens.radius.sm}px;"
            "}"
        )


class ProgressRing(QtWidgets.QLabel):
    def __init__(self, text: str = "", *, class_name: str = "", tokens=None):
        super().__init__(text)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "ProgressRing")
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{"
            f"border: 2px solid {tokens.colors.border_active};"
            f"border-radius: {tokens.radius.xl}px;"
            f"padding: {tokens.spacing.sm}px;"
            f"color: {tokens.colors.text_primary};"
            "}}"
        )
