"""Button primitives."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class GlassButton(QtWidgets.QPushButton):
    def __init__(
        self,
        label: str,
        *,
        variant: str = "primary",
        size: str = "md",
        class_name: str = "",
        is_loading: bool = False,
        is_disabled: bool = False,
        tokens=None,
    ) -> None:
        super().__init__(label)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassButton")
        self.setDisabled(is_disabled)
        padding_map = {"sm": 6, "md": 10, "lg": 14}
        padding = padding_map.get(size, 10)
        if is_loading:
            self.setText("Loading…")
        if variant == "secondary":
            background = tokens.colors.surface_alt
            border = tokens.colors.border
        elif variant == "ghost":
            background = "transparent"
            border = tokens.colors.border
        else:
            background = tokens.colors.accent
            border = tokens.colors.border_active
        self.setStyleSheet(
            f"QPushButton#{self.objectName()} {{"
            f"background: {background};"
            f"border: 1px solid {border};"
            f"border-radius: {tokens.radius.md}px;"
            f"color: {tokens.colors.text_primary};"
            f"padding: {padding}px {padding * 2}px;"
            f"font-family: {tokens.typography.font_family};"
            "}"
            f"QPushButton#{self.objectName()}:hover {{"
            f"border-color: {tokens.colors.border_active};"
            f"box-shadow: 0 0 12px rgba(110, 231, 255, 0.4);"
            "}"
            f"QPushButton#{self.objectName()}:pressed {{"
            f"transform: translateY(1px);"
            "}"
            f"QPushButton#{self.objectName()}:disabled {{"
            "opacity: 0.5;"
            "}"
        )
