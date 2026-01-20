from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from UIComponents.core.styles import apply_glass_panel
from UIComponents.core.tokens import SPACING


class SplitPane(QWidget):
  """Resizable split pane wrapper (render-only)."""

  def __init__(self, left: QWidget, right: QWidget, *, class_name: str = ""):
    super().__init__()
    self.setObjectName(class_name)
    apply_glass_panel(self, padding=SPACING.sm)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(left)
    splitter.addWidget(right)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 2)
    splitter.setHandleWidth(4)

    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(splitter)
    self.setLayout(layout)
