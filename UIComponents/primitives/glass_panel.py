"""Glass panel primitive."""
from PySide6 import QtWidgets

from UIComponents.core.styles import glass_panel_style
from UIComponents.core.theme import resolve_tokens


class GlassPanel(QtWidgets.QFrame):
    def __init__(
        self,
        *,
        class_name: str = "",
        tokens=None,
        is_active: bool = False,
        radius: int | None = None,
    ) -> None:
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassPanel")
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{{glass_panel_style(tokens, radius=radius, is_active=is_active)}}}"
        )
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(
            tokens.spacing.lg,
            tokens.spacing.lg,
            tokens.spacing.lg,
            tokens.spacing.lg,
        )
        layout.setSpacing(tokens.spacing.md)
