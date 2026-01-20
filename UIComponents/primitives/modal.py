"""Modal shell."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class ModalShell(QtWidgets.QDialog):
    def __init__(self, title: str, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "ModalShell")
        self.setModal(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)
        panel = GlassPanel(tokens=tokens, is_active=True)
        panel_layout = panel.layout()
        header = QtWidgets.QLabel(title)
        header.setStyleSheet(
            f"color: {tokens.colors.text_primary};"
            f"font-size: {tokens.typography.h2_size}px;"
            f"font-weight: 600;"
        )
        panel_layout.addWidget(header)
        layout.addWidget(panel)
