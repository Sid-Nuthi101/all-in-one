"""Stat card component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class StatCard(GlassPanel):
    def __init__(
        self,
        title: str,
        value: str,
        change: str = "",
        *,
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(class_name=class_name or "StatCard", tokens=tokens)
        tokens = resolve_tokens(tokens)
        layout = self.layout()
        title_label = QtWidgets.QLabel(title)
        value_label = QtWidgets.QLabel(value)
        change_label = QtWidgets.QLabel(change)
        title_label.setStyleSheet(f"color: {tokens.colors.text_secondary};")
        value_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h2_size}px;"
            f"font-weight: 600;"
        )
        change_label.setStyleSheet(f"color: {tokens.colors.success};")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        if change:
            layout.addWidget(change_label)
