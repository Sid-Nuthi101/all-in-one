"""Profile card component."""
from PySide6 import QtCore, QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class ProfileCard(GlassPanel):
    def __init__(
        self,
        name: str,
        title: str,
        *,
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(class_name=class_name or "ProfileCard", tokens=tokens)
        tokens = resolve_tokens(tokens)
        layout = self.layout()
        avatar = QtWidgets.QLabel(name[:1].upper())
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(QtCore.Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background: {tokens.colors.accent};"
            f"border-radius: 24px;"
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h3_size}px;"
        )
        name_label = QtWidgets.QLabel(name)
        title_label = QtWidgets.QLabel(title)
        name_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-weight: 600;"
        )
        title_label.setStyleSheet(f"color: {tokens.colors.text_secondary};")
        header = QtWidgets.QHBoxLayout()
        header.addWidget(avatar)
        header.addSpacing(tokens.spacing.sm)
        text_column = QtWidgets.QVBoxLayout()
        text_column.addWidget(name_label)
        text_column.addWidget(title_label)
        header.addLayout(text_column)
        layout.addLayout(header)
