"""Message bubble mock component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class MessageBubble(QtWidgets.QFrame):
    def __init__(
        self,
        text: str,
        *,
        is_outgoing: bool = False,
        timestamp: str = "",
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "MessageBubble")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(tokens.spacing.md, tokens.spacing.sm, tokens.spacing.md, tokens.spacing.sm)
        layout.setSpacing(tokens.spacing.xs)
        message_label = QtWidgets.QLabel(text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.body_size}px;"
        )
        layout.addWidget(message_label)
        if timestamp:
            time_label = QtWidgets.QLabel(timestamp)
            time_label.setStyleSheet(
                f"color: {tokens.colors.text_muted};"
                f"font-size: {tokens.typography.caption_size}px;"
            )
            layout.addWidget(time_label)
        bubble_color = tokens.colors.accent if is_outgoing else tokens.colors.surface_alt
        border_color = tokens.colors.border_active if is_outgoing else tokens.colors.border
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: {bubble_color};"
            f"border: 1px solid {border_color};"
            f"border-radius: {tokens.radius.lg}px;"
            "}}"
        )
