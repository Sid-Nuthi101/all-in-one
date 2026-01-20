"""Toast UI component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class Toast(QtWidgets.QFrame):
    def __init__(self, message: str, *, variant: str = "info", class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "Toast")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(tokens.spacing.md, tokens.spacing.sm, tokens.spacing.md, tokens.spacing.sm)
        label = QtWidgets.QLabel(message)
        label.setStyleSheet(f"color: {tokens.colors.text_primary};")
        layout.addWidget(label)
        color_map = {
            "success": tokens.colors.success,
            "danger": tokens.colors.danger,
            "info": tokens.colors.accent,
        }
        accent = color_map.get(variant, tokens.colors.accent)
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: {tokens.colors.surface_alt};"
            f"border: 1px solid {accent};"
            f"border-radius: {tokens.radius.md}px;"
            "}}"
        )
