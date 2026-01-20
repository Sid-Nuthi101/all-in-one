"""Aurora gradient background component."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class AuroraGradientBackground(QtWidgets.QFrame):
    def __init__(self, palette=None, motion_level: float = 0.5, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        palette = palette or [tokens.colors.accent, tokens.colors.accent_secondary]
        self.setObjectName(class_name or "AuroraGradientBackground")
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {palette[0]}, stop:1 {palette[1]});"
            f"opacity: {0.4 + motion_level * 0.2};"
            "}}"
        )
