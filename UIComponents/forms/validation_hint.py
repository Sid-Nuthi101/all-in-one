"""Validation hint (visual only)."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class ValidationHint(QtWidgets.QLabel):
    def __init__(
        self,
        text: str,
        *,
        state: str = "neutral",
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__(text)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "ValidationHint")
        color_map = {
            "error": tokens.colors.danger,
            "success": tokens.colors.success,
            "neutral": tokens.colors.text_muted,
        }
        color = color_map.get(state, tokens.colors.text_muted)
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{"
            f"color: {color};"
            f"font-size: {tokens.typography.caption_size}px;"
            "}}"
        )
