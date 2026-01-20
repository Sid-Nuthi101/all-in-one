import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
  QApplication,
  QFrame,
  QHBoxLayout,
  QLabel,
  QPushButton,
  QSplitter,
  QVBoxLayout,
  QWidget,
  QMainWindow,
  QSizePolicy,
)

from logic import get_status


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    self.setWindowTitle("")
    self.setWindowFlags(Qt.WindowMinMaxButtonsHint)

    self.setWindowOpacity(0.95)
    self.setUnifiedTitleAndToolBarOnMac(True)

    central = QWidget()
    self.setCentralWidget(central)

    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)

    self.splitter = QSplitter(Qt.Horizontal)
    self.splitter.setHandleWidth(6)

    # --- LEFT ---
    left_container = QWidget()
    left_container.setObjectName("leftContainer")
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(12, 12, 12, 12)
    left_layout.setSpacing(12)
    left_layout.setAlignment(Qt.AlignTop)

    chats = [
      {"name": "Alex Morgan", "time": "2:14 PM", "preview": "Did you see the new designs?", "initials": "AM"},
      {"name": "Jordan Lee", "time": "1:02 PM", "preview": "Let’s sync after the standup.", "initials": "JL"},
      {"name": "Priya Patel", "time": "12:47 PM", "preview": "Shipping the update in 10 minutes.", "initials": "PP"},
    ]

    self.chat_rows = []
    for chat in chats:
      row = self._build_chat_row(chat)
      self.chat_rows.append(row)
      left_layout.addWidget(row)
    left_layout.addStretch()

    # --- RIGHT ---
    right_container = QWidget()
    right_container.setObjectName("blackPanel")
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(0)

    # simple header row (top-left name + padding)
    header = QWidget()
    header.setObjectName("nameHeader")
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(12, 10, 12, 10)
    header_layout.setSpacing(8)

    self.name_label = QLabel("Alex Morgan")
    self.name_label.setObjectName("chatName")

    info_button = QPushButton("Info")
    info_button.setObjectName("infoButton")

    header_layout.addWidget(self.name_label)
    header_layout.addStretch()
    header_layout.addWidget(info_button)

    right_layout.addWidget(header)
    right_layout.addStretch()

    self.splitter.addWidget(left_container)
    self.splitter.addWidget(right_container)
    self.splitter.setStretchFactor(0, 0)
    self.splitter.setStretchFactor(1, 1)
    self.splitter.setSizes([360, 1000])

    layout.addWidget(self.splitter)
    if self.chat_rows:
      self._select_chat(chats[0], self.chat_rows[0])

    self.setStyleSheet(
      """
      #nameHeader {
        background-color: rgba(255,255,255, 0.1);
      }
      #leftContainer {
        border-radius: 10px;
      }
      QWidget#blackPanel {
        background-color: #000000;
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
      #chatRow{
        max-height: 56px;
        border-radius: 12px;
        padding: 6px;
      }
      #chatRow[selected="true"] {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
          stop:0 rgba(74, 108, 247, 0.8),
          stop:1 rgba(139, 92, 246, 0.8));
      }
      #chatRow[selected="true"] QLabel {
        color: #ffffff;
      }
      """
    )

  def on_run(self):
    self.output.append(get_status())

  def _build_chat_row(self, chat):
    row = QFrame()
    row.setObjectName("chatRow")
    row.setCursor(Qt.PointingHandCursor)
    row.setProperty("selected", False)
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(12)

    avatar = QLabel(chat["initials"])
    avatar.setAlignment(Qt.AlignCenter)
    avatar.setFixedSize(48, 48)

    text_container = QWidget()
    text_layout = QVBoxLayout(text_container)
    text_layout.setContentsMargins(0, 0, 0, 0)
    text_layout.setSpacing(4)

    top_row = QWidget()
    top_layout = QHBoxLayout(top_row)
    top_layout.setContentsMargins(0, 0, 0, 0)
    top_layout.setSpacing(8)

    name = QLabel(chat["name"])
    name.setObjectName("chatName")
    time = QLabel(chat["time"])

    top_layout.addWidget(name)
    top_layout.addStretch()
    top_layout.addWidget(time)

    preview = QLabel(chat["preview"])

    text_layout.addWidget(top_row)
    text_layout.addWidget(preview)

    row_layout.addWidget(avatar)
    row_layout.addWidget(text_container)

    row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    row.mousePressEvent = lambda event, chat=chat, row=row: self._on_chat_clicked(
      event,
      chat,
      row,
    )
    return row

  def _on_chat_clicked(self, event, chat, row):
    self._select_chat(chat, row)
    event.accept()

  def _select_chat(self, chat, row):
    self.name_label.setText(chat["name"])
    for chat_row in self.chat_rows:
      self._set_row_selected(chat_row, chat_row is row)

  def _set_row_selected(self, row, selected):
    row.setProperty("selected", selected)
    row.style().unpolish(row)
    row.style().polish(row)
    row.update()


def main():
  app = QApplication(sys.argv)
  w = MainWindow()
  w.setMinimumSize(1100, 600)
  w.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()
