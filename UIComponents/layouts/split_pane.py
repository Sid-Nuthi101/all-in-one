from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter


class SplitPane(QWidget):
  def __init__(self, left, right, class_name=None):
    super().__init__()
    if class_name:
      self.setObjectName(class_name)

    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(layout)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(left)
    splitter.addWidget(right)
    splitter.setSizes([300, 700])
    splitter.setHandleWidth(4)

    layout.addWidget(splitter)
