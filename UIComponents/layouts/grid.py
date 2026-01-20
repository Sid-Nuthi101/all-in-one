"""Responsive grid helpers."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class Grid(QtWidgets.QWidget):
    def __init__(self, columns: int = 3, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "Grid")
        self.columns = columns
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(tokens.spacing.md)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_widget(self, widget: QtWidgets.QWidget) -> None:
        row = self.layout.count() // self.columns
        column = self.layout.count() % self.columns
        self.layout.addWidget(widget, row, column)
