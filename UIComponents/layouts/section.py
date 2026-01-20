"""Section layout component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.neon_divider import NeonDivider


class Section(QtWidgets.QFrame):
    def __init__(self, title: str, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "Section")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h3_size}px;"
            f"font-weight: 600;"
        )
        layout.addWidget(title_label)
        layout.addWidget(NeonDivider())
