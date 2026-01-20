"""Status badge primitive."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class StatusBadge(QtWidgets.QLabel):
    def __init__(
        self,
        text: str,
        *,
        variant: str = "default",
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(text)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "StatusBadge")
        color_map = {
            "success": tokens.colors.success,
            "danger": tokens.colors.danger,
            "info": tokens.colors.accent,
        }
        background = color_map.get(variant, tokens.colors.surface_alt)
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{"
            f"background: {background};"
            f"border-radius: {tokens.radius.sm}px;"
            f"padding: {tokens.spacing.xs}px {tokens.spacing.sm}px;"
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.caption_size}px;"
            "}}"
        )
