"""Resizable split pane wrapper."""
from PySide6 import QtCore, QtWidgets

from UIComponents.core.theme import resolve_tokens


class SplitPane(QtWidgets.QSplitter):
    def __init__(self, orientation=QtCore.Qt.Horizontal, *, class_name: str = "", tokens=None):
        super().__init__(orientation)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "SplitPane")
        self.setStyleSheet(
            f"QSplitter#{self.objectName()}::handle {{"
            f"background: {tokens.colors.border};"
            f"margin: {tokens.spacing.xs}px;"
            "}"
        )
