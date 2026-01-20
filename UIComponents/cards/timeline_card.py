"""Timeline card component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class TimelineCard(GlassPanel):
    def __init__(
        self,
        time_label: str,
        title: str,
        description: str,
        *,
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(class_name=class_name or "TimelineCard", tokens=tokens)
        tokens = resolve_tokens(tokens)
        layout = self.layout()
        time = QtWidgets.QLabel(time_label)
        time.setStyleSheet(f"color: {tokens.colors.text_muted};")
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-weight: 600;"
        )
        description_label = QtWidgets.QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"color: {tokens.colors.text_secondary};")
        layout.addWidget(time)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
