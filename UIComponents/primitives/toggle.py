"""Toggle primitives."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class GlassToggle(QtWidgets.QCheckBox):
    def __init__(
        self,
        label: str = "",
        *,
        size: str = "md",
        class_name: str = "",
        is_disabled: bool = False,
        tokens=None,
    ) -> None:
        super().__init__(label)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassToggle")
        self.setDisabled(is_disabled)
        self.setStyleSheet(
            f"QCheckBox#{self.objectName()} {{"
            f"color: {tokens.colors.text_primary};"
            f"font-family: {tokens.typography.font_family};"
            "}"
            f"QCheckBox#{self.objectName()}::indicator {{"
            f"width: 40px;"
            f"height: 22px;"
            f"border-radius: 11px;"
            f"background: {tokens.colors.surface};"
            f"border: 1px solid {tokens.colors.border};"
            "margin-right: 6px;"
            "}"
            f"QCheckBox#{self.objectName()}::indicator:checked {{"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {tokens.colors.accent}, stop:1 {tokens.colors.accent_secondary});"
            f"border: 1px solid {tokens.colors.border_active};"
            "}"
            f"QCheckBox#{self.objectName()}::indicator:disabled {{"
            "opacity: 0.5;"
            "}"
        )


class SegmentedControl(QtWidgets.QWidget):
    def __init__(
        self,
        options: list[str],
        *,
        size: str = "md",
        class_name: str = "",
        tokens=None,
    ) -> None:
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "SegmentedControl")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(tokens.spacing.xs)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = []
        for option in options:
            button = QtWidgets.QPushButton(option)
            button.setCheckable(True)
            button.setStyleSheet(
                f"QPushButton {{"
                f"background: {tokens.colors.surface_alt};"
                f"border: 1px solid {tokens.colors.border};"
                f"border-radius: {tokens.radius.sm}px;"
                f"padding: {tokens.spacing.xs}px {tokens.spacing.sm}px;"
                f"color: {tokens.colors.text_secondary};"
                "}"
                f"QPushButton:checked {{"
                f"background: {tokens.colors.accent};"
                f"color: {tokens.colors.text_primary};"
                "}"
                f"QPushButton:hover {{"
                f"border-color: {tokens.colors.border_active};"
                "}"
            )
            self.buttons.append(button)
            layout.addWidget(button)
