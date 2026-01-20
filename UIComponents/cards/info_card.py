"""Info card component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class InfoCard(GlassPanel):
    def __init__(
        self,
        title: str,
        body: str,
        *,
        class_name: str = "",
        tokens=None,
        actions: list[QtWidgets.QWidget] | None = None,
    ) -> None:
        super().__init__(class_name=class_name or "InfoCard", tokens=tokens)
        tokens = resolve_tokens(tokens)
        layout = self.layout()
        title_label = QtWidgets.QLabel(title)
        body_label = QtWidgets.QLabel(body)
        body_label.setWordWrap(True)
        title_label.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h3_size}px;"
            f"font-weight: 600;"
        )
        body_label.setStyleSheet(f"color: {tokens.colors.text_secondary};")
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        if actions:
            action_row = QtWidgets.QHBoxLayout()
            action_row.setSpacing(tokens.spacing.sm)
            for action in actions:
                action_row.addWidget(action)
            layout.addLayout(action_row)
