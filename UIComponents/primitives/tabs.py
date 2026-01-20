"""Tabs UI shell."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class GlassTabs(QtWidgets.QTabWidget):
    def __init__(self, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassTabs")
        self.setStyleSheet(
            f"QTabWidget::pane {{"
            f"border: 1px solid {tokens.colors.border};"
            f"border-radius: {tokens.radius.md}px;"
            "}"
            f"QTabBar::tab {{"
            f"background: {tokens.colors.surface};"
            f"padding: {tokens.spacing.sm}px {tokens.spacing.md}px;"
            f"border-radius: {tokens.radius.sm}px;"
            f"color: {tokens.colors.text_secondary};"
            "}"
            f"QTabBar::tab:selected {{"
            f"background: {tokens.colors.accent};"
            f"color: {tokens.colors.text_primary};"
            "}"
        )
