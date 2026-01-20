"""Glass panel primitive."""
from PySide6 import QtCore, QtGui, QtWidgets

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
        enable_blur: bool = True,
    ) -> None:
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "GlassPanel")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{{glass_panel_style(tokens, radius=radius, is_active=is_active)}}}"
        )
        if enable_blur:
            shadow = QtWidgets.QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(tokens.blur.lg)
            shadow.setOffset(0, 12)
            shadow.setColor(QtGui.QColor(0, 0, 0, 140))
            self.setGraphicsEffect(shadow)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(
            tokens.spacing.lg,
            tokens.spacing.lg,
            tokens.spacing.lg,
            tokens.spacing.lg,
        )
        layout.setSpacing(tokens.spacing.md)
