"""Top-level app shell layout."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens
from UIComponents.primitives.glass_panel import GlassPanel


class AppShell(QtWidgets.QFrame):
    def __init__(self, *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "AppShell")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)
        layout.setSpacing(tokens.spacing.lg)
        self.sidebar = GlassPanel(tokens=tokens, class_name="AppShellSidebar")
        self.content = GlassPanel(tokens=tokens, class_name="AppShellContent", is_active=True)
        layout.addWidget(self.sidebar, 1)
        layout.addWidget(self.content, 4)
        self.setStyleSheet(
            f"QFrame#{self.objectName()} {{"
            f"background: transparent;"
            "}}"
        )
