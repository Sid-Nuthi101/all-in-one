"""Common form panel layout."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class FormShell(GlassPanel):
    def __init__(self, title: str = "", *, class_name: str = "", tokens=None):
        super().__init__(class_name=class_name or "FormShell", tokens=tokens)
        tokens = resolve_tokens(tokens)
        if title:
            title_label = QtWidgets.QLabel(title)
            title_label.setStyleSheet(
                f"color: {tokens.colors.text_primary};"
                f"font-size: {tokens.typography.h3_size}px;"
                f"font-weight: 600;"
            )
            self.layout().addWidget(title_label)
