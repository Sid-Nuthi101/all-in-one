"""Empty state component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class EmptyState(QtWidgets.QFrame):
    def __init__(self, title: str, body: str, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "EmptyState")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h2_size}px;"
            f"font-weight: 600;"
        )
        body_label = QtWidgets.QLabel(body)
        body_label.setStyleSheet(
            f"color: {tokens.colors.text_secondary};"
            f"font-size: {tokens.typography.body_size}px;"
        )
        body_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: {tokens.colors.surface};"
            f"border: 1px dashed {tokens.colors.border};"
            f"border-radius: {tokens.radius.md}px;"
            "}}"
        )
