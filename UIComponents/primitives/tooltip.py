"""Tooltip primitive."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class GlassTooltip(QtWidgets.QFrame):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassTooltip")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(tokens.spacing.sm, tokens.spacing.xs, tokens.spacing.sm, tokens.spacing.xs)
        label = QtWidgets.QLabel(text)
        label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.caption_size}px;"
        )
        layout.addWidget(label)
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: {tokens.colors.surface_alt};"
            f"border: 1px solid {tokens.colors.border};"
            f"border-radius: {tokens.radius.sm}px;"
            "}}"
        )
