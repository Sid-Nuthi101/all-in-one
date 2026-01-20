"""Icon wrapper component."""
from PySide6 import QtGui, QtWidgets

from UIComponents.core.theme import resolve_tokens


class NeonIcon(QtWidgets.QLabel):
    def __init__(self, icon: QtGui.QIcon, *, size: int = 16, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "NeonIcon")
        pixmap = icon.pixmap(size, size)
        self.setPixmap(pixmap)
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{"
            f"color: {tokens.colors.accent};"
            "}}"
        )
