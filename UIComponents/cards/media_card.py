"""Media card component."""
from PySide6 import QtCore, QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class MediaCard(GlassPanel):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        *,
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(class_name=class_name or "MediaCard", tokens=tokens)
        tokens = resolve_tokens(tokens)
        layout = self.layout()
        media_placeholder = QtWidgets.QLabel("Media")
        media_placeholder.setFixedHeight(120)
        media_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        media_placeholder.setStyleSheet(
            f"background: {tokens.colors.surface_alt};"
            f"border-radius: {tokens.radius.md}px;"
            f"color: {tokens.colors.text_muted};"
        )
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-weight: 600;"
        )
        layout.addWidget(media_placeholder)
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QtWidgets.QLabel(subtitle)
            subtitle_label.setStyleSheet(f"color: {tokens.colors.text_secondary};")
            layout.addWidget(subtitle_label)
