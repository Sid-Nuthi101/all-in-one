"""Message card component with profile + bubble."""
from PySide6 import QtCore, QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel
from UIComponents.cards.message_bubble import MessageBubble


class MessageCard(GlassPanel):
    def __init__(
        self,
        name: str,
        message: str,
        *,
        timestamp: str = "",
        is_outgoing: bool = False,
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(class_name=class_name or "MessageCard", tokens=tokens)
        tokens = resolve_tokens(tokens)
        layout = self.layout()
        header = QtWidgets.QHBoxLayout()
        avatar = QtWidgets.QLabel(name[:1].upper())
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(QtCore.Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background: {tokens.colors.surface_alt};"
            f"border-radius: 16px;"
            f"color: {tokens.colors.text_primary};"
            f"font-weight: 600;"
        )
        name_label = QtWidgets.QLabel(name)
        name_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-weight: 600;"
        )
        header.addWidget(avatar)
        header.addSpacing(tokens.spacing.sm)
        header.addWidget(name_label)
        header.addStretch()
        if timestamp:
            time_label = QtWidgets.QLabel(timestamp)
            time_label.setStyleSheet(
                f"color: {tokens.colors.text_muted};"
                f"font-size: {tokens.typography.caption_size}px;"
            )
            header.addWidget(time_label)
        layout.addLayout(header)
        layout.addWidget(MessageBubble(message, is_outgoing=is_outgoing, timestamp="", tokens=tokens))
