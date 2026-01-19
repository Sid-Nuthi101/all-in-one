import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit

from logic import get_status


class MainWindow(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("My Mac App")

    layout = QVBoxLayout()

    self.output = QTextEdit()
    self.output.setReadOnly(True)

    btn = QPushButton("Run Python logic")
    btn.clicked.connect(self.on_run)

    layout.addWidget(btn)
    layout.addWidget(self.output)
    self.setLayout(layout)

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
