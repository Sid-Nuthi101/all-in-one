"""Input primitives."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class GlassInput(QtWidgets.QLineEdit):
    def __init__(
        self,
        placeholder: str = "",
        *,
        variant: str = "default",
        size: str = "md",
        class_name: str = "",
        is_error: bool = False,
        is_disabled: bool = False,
        tokens=None,
    ) -> None:
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassInput")
        self.setPlaceholderText(placeholder)
        self.setDisabled(is_disabled)
        padding_map = {"sm": 6, "md": 10, "lg": 12}
        padding = padding_map.get(size, 10)
        border = tokens.colors.danger if is_error else tokens.colors.border
        self.setStyleSheet(
            f"QLineEdit#{self.objectName()} {{"
            f"background: {tokens.colors.surface};"
            f"border: 1px solid {border};"
            f"border-radius: {tokens.radius.md}px;"
            f"padding: {padding}px;"
            f"color: {tokens.colors.text_primary};"
            f"font-family: {tokens.typography.font_family};"
            "}"
            f"QLineEdit#{self.objectName()}:focus {{"
            f"border-color: {tokens.colors.border_active};"
            f"box-shadow: 0 0 12px rgba(110, 231, 255, 0.4);"
            "}"
        )


class GlassTextArea(QtWidgets.QTextEdit):
    def __init__(
        self,
        placeholder: str = "",
        *,
        class_name: str = "",
        is_error: bool = False,
        is_disabled: bool = False,
        tokens=None,
    ) -> None:
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassTextArea")
        self.setPlaceholderText(placeholder)
        self.setDisabled(is_disabled)
        border = tokens.colors.danger if is_error else tokens.colors.border
        self.setStyleSheet(
            f"QTextEdit#{self.objectName()} {{"
            f"background: {tokens.colors.surface};"
            f"border: 1px solid {border};"
            f"border-radius: {tokens.radius.md}px;"
            f"padding: {tokens.spacing.sm}px;"
            f"color: {tokens.colors.text_primary};"
            f"font-family: {tokens.typography.font_family};"
            "}"
            f"QTextEdit#{self.objectName()}:focus {{"
            f"border-color: {tokens.colors.border_active};"
            f"box-shadow: 0 0 12px rgba(110, 231, 255, 0.4);"
            "}"
        )
