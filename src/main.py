import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
  QApplication,
  QGraphicsBlurEffect,
  QHBoxLayout,
  QLabel,
  QPushButton,
  QSplitter,
  QStackedLayout,
  QTextEdit,
  QVBoxLayout,
  QWidget,
)

from logic import get_status


class MainWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("My Mac App")
    self.setAttribute(Qt.WA_TranslucentBackground)
    self.setAttribute(Qt.WA_NoSystemBackground)
    self.setWindowOpacity(0.9)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)

    splitter = QSplitter(Qt.Horizontal)
    splitter.setHandleWidth(6)

    left_container = QWidget()
    left_layout = QStackedLayout(left_container)
    left_layout.setStackingMode(QStackedLayout.StackAll)

    background = QWidget()
    background.setObjectName("glassBackground")

    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(24, 24, 24, 24)

    glass_panel = QWidget()
    glass_panel.setObjectName("glassPanel")
    glass_layout = QVBoxLayout(glass_panel)
    glass_layout.setContentsMargins(24, 24, 24, 24)
    glass_layout.setSpacing(16)

    blur = QGraphicsBlurEffect()
    blur.setBlurRadius(18)
    glass_panel.setGraphicsEffect(blur)

    self.output = QTextEdit()
    self.output.setReadOnly(True)

    btn = QPushButton("Run Python logic")
    btn.clicked.connect(self.on_run)

    glass_layout.addWidget(btn)
    glass_layout.addWidget(self.output)
    content_layout.addWidget(glass_panel)
    left_layout.addWidget(background)
    left_layout.addWidget(content)

    right_container = QWidget()
    right_container.setObjectName("blackPanel")
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(0)

    right_header = QWidget()
    right_header.setObjectName("rightHeader")
    header_layout = QHBoxLayout(right_header)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(8)

    name_label = QLabel("Alex Morgan")
    name_label.setObjectName("chatName")
    info_button = QPushButton("Info")
    info_button.setObjectName("infoButton")

    header_layout.addWidget(name_label)
    header_layout.addStretch()
    header_layout.addWidget(info_button)
    right_layout.addWidget(right_header)
    right_layout.addStretch()

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setSizes([320, 180])
    layout.addWidget(splitter)

    self.setStyleSheet(
      """
      QWidget#glassBackground {
        background-color: rgba(255, 255, 255, 0.02);
      }
      QWidget#blackPanel {
        background-color: #000000;
      }
      QWidget#rightHeader {
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
      }
      QLabel#chatName {
        color: #ffffff;
        font-weight: 600;
      }
      QPushButton#infoButton {
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: #ffffff;
        border-radius: 10px;
        padding: 6px 10px;
      }
      QPushButton#infoButton:hover {
        background-color: rgba(255, 255, 255, 0.25);
      }
      QWidget#glassPanel {
        background-color: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 18px;
      }
      QTextEdit {
        background-color: rgba(255, 255, 255, 0.35);
        border-radius: 12px;
        padding: 8px;
      }
      QPushButton {
        background-color: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.45);
        border-radius: 12px;
        padding: 10px 14px;
      }
      QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.55);
      }
      """
    )

  def on_run(self):
    self.output.append(get_status())


def main():
  app = QApplication(sys.argv)
  w = MainWindow()
  w.resize(500, 350)
  w.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()
