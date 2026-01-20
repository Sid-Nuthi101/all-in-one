"""Table UI shell."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class GlassTable(QtWidgets.QTableWidget):
    def __init__(self, rows: int = 0, columns: int = 0, *, class_name: str = "", tokens=None):
        super().__init__(rows, columns)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassTable")
        self.setStyleSheet(
            f"QTableWidget#{self.objectName()} {{"
            f"background: {tokens.colors.surface};"
            f"border: 1px solid {tokens.colors.border};"
            f"gridline-color: {tokens.colors.border};"
            f"color: {tokens.colors.text_primary};"
            "}"
            f"QHeaderView::section {{"
            f"background: {tokens.colors.surface_alt};"
            f"color: {tokens.colors.text_secondary};"
            f"padding: {tokens.spacing.sm}px;"
            f"border: none;"
            "}"
        )
