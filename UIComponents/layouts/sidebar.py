"""Sidebar navigation UI."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class Sidebar(QtWidgets.QFrame):
    def __init__(self, title: str = "Navigation", *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "Sidebar")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        panel = GlassPanel(tokens=tokens)
        panel_layout = panel.layout()
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h3_size}px;"
            f"font-weight: 600;"
        )
        panel_layout.addWidget(title_label)
        layout.addWidget(panel)
