import sys
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
  QApplication,
  QFrame,
  QHBoxLayout,
  QDialog,
  QLabel,
  QLineEdit,
  QProgressBar,
  QPushButton,
  QScrollArea,
  QSplitter,
  QVBoxLayout,
  QWidget,
  QMainWindow,
  QSizePolicy,
)

import os

from messages import MessageBridge
from logic import get_status
import auth
import login
import session


class ElidedLabel(QLabel):
  def __init__(self, text="", parent=None):
    super().__init__(text, parent)
    self._full_text = text
    self.setWordWrap(False)

  def setText(self, text):
    self._full_text = text
    self._update_elide()

  def resizeEvent(self, event):
    super().resizeEvent(event)
    self._update_elide()

  def _update_elide(self):
    metrics = self.fontMetrics()
    elided = metrics.elidedText(self._full_text, Qt.ElideRight, max(self.width(), 10))
    super().setText(elided)


class TrainingDialog(QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Training")
    self.setModal(True)
    self.setFixedWidth(360)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    self.label = QLabel("Training your model for the first time…")
    self.label.setWordWrap(True)
    layout.addWidget(self.label)

    self.progress = QProgressBar()
    self.progress.setRange(0, 0)
    self.progress.setTextVisible(False)
    layout.addWidget(self.progress)


class TrainingWorker(QThread):
  completed = Signal(object)
  failed = Signal(Exception)

  def __init__(self, training_fn: Callable[[], object]):
    super().__init__()
    self._training_fn = training_fn

  def run(self):
    try:
      result = self._training_fn()
      self.completed.emit(result)
    except Exception as exc:
      self.failed.emit(exc)


class LoginDialog(QDialog):
  def __init__(self, on_login: Callable[[str], str], parent=None):
    super().__init__(parent)
    self.setWindowTitle("Login Required")
    self.setModal(True)
    self.setFixedWidth(360)
    self._on_login = on_login

    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    label = QLabel("Sign in with Apple to continue.")
    label.setWordWrap(True)
    layout.addWidget(label)

    self.input = QLineEdit()
    self.input.setPlaceholderText("Paste Apple authorization code")
    layout.addWidget(self.input)

    self.error = QLabel("")
    self.error.setWordWrap(True)
    self.error.setStyleSheet("color: #cc0000;")
    layout.addWidget(self.error)

    button_row = QHBoxLayout()
    button_row.addStretch()
    cancel_btn = QPushButton("Cancel")
    ok_btn = QPushButton("Continue")
    button_row.addWidget(cancel_btn)
    button_row.addWidget(ok_btn)
    layout.addLayout(button_row)

    cancel_btn.clicked.connect(self.reject)
    ok_btn.clicked.connect(self._accept_if_valid)

  def _accept_if_valid(self):
    code = self.input.text().strip()
    if not code:
      return
    try:
      user_id = self._on_login(code)
    except Exception as exc:
      self.error.setText(str(exc))
      return
    self.input.setText(user_id)
    self.accept()

  def user_id(self) -> str:
    return self.input.text().strip()


class MainWindow(QMainWindow):
  def __init__(
    self,
    user_id: str,
    training_fn: Optional[Callable[[], object]] = None,
  ):
    super().__init__()
    self._training_dialog: Optional[TrainingDialog] = None
    self._training_worker: Optional[TrainingWorker] = None
    self._user_id = user_id

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
    left_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
    left_outer_layout = QVBoxLayout(left_container)
    left_outer_layout.setContentsMargins(0, 0, 0, 0)
    left_outer_layout.setSpacing(0)

    left_scroll = QScrollArea()
    left_scroll.setObjectName("leftScroll")
    left_scroll.setWidgetResizable(True)
    left_scroll.setFrameShape(QFrame.NoFrame)
    left_outer_layout.addWidget(left_scroll)

    left_scroll_contents = QWidget()
    left_scroll.setWidget(left_scroll_contents)

    left_layout = QVBoxLayout(left_scroll_contents)
    left_layout.setContentsMargins(12, 12, 12, 12)
    left_layout.setSpacing(12)
    left_layout.setAlignment(Qt.AlignTop)

    self.bridge = MessageBridge()
    chats = self._load_chats()

    self.chat_rows = []
    for chat in chats:
      row = self._build_chat_row(chat)
      self.chat_rows.append(row)
      left_layout.addWidget(row)

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

    self.message_scroll = QScrollArea()
    self.message_scroll.setObjectName("messageScroll")
    self.message_scroll.setWidgetResizable(True)
    self.message_scroll.setFrameShape(QFrame.NoFrame)
    right_layout.addWidget(self.message_scroll)

    self.message_scroll_contents = QWidget()
    self.message_scroll.setWidget(self.message_scroll_contents)

    self.message_layout = QVBoxLayout(self.message_scroll_contents)
    self.message_layout.setContentsMargins(20, 16, 20, 16)
    self.message_layout.setSpacing(12)
    self.message_layout.setAlignment(Qt.AlignTop)

    self.splitter.addWidget(left_container)
    self.splitter.addWidget(right_container)
    self.splitter.setStretchFactor(0, 1)
    self.splitter.setStretchFactor(1, 3)
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
      QScrollArea#messageScroll {
        background-color: transparent;
      }
      QScrollArea#messageScroll QWidget {
        background-color: transparent;
      }
      QFrame#messageBubble {
        background-color: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 16px;
        padding: 8px 12px;
      }
      QFrame#messageBubble[fromMe="true"] {
        background-color: rgba(74, 108, 247, 0.35);
        border: 1px solid rgba(139, 92, 246, 0.5);
      }
      QLabel#messageText {
        color: #ffffff;
      }
      #chatRow{
        max-height: 56px;
        border-radius: 6px;
        padding: 10px 12px;
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

    if training_fn is not None:
      self.run_training_with_popup(training_fn)

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

    preview = ElidedLabel(chat["preview"])

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
    self._load_messages(chat)

  def _set_row_selected(self, row, selected):
    row.setProperty("selected", selected)
    row.style().unpolish(row)
    row.style().polish(row)
    row.update()

  def _clear_layout(self, layout):
    while layout.count():
      item = layout.takeAt(0)
      widget = item.widget()
      if widget is not None:
        widget.deleteLater()
      spacer = item.spacerItem()
      if spacer is not None:
        del spacer

  def _build_message_bubble(self, message):
    wrapper = QWidget()
    wrapper_layout = QHBoxLayout(wrapper)
    wrapper_layout.setContentsMargins(0, 0, 0, 0)
    wrapper_layout.setSpacing(0)

    bubble = QFrame()
    bubble.setObjectName("messageBubble")
    bubble.setProperty("fromMe", message["is_from_me"])

    bubble_layout = QVBoxLayout(bubble)
    bubble_layout.setContentsMargins(12, 8, 12, 8)
    bubble_layout.setSpacing(4)

    text = QLabel(message["text"])
    text.setObjectName("messageText")
    text.setWordWrap(True)
    text.setTextInteractionFlags(Qt.TextSelectableByMouse)
    text.setMaximumWidth(420)

    bubble_layout.addWidget(text)

    if message["is_from_me"]:
      wrapper_layout.addStretch()
      wrapper_layout.addWidget(bubble)
    else:
      wrapper_layout.addWidget(bubble)
      wrapper_layout.addStretch()

    return wrapper

  def _load_messages(self, chat):
    self._clear_layout(self.message_layout)
    messages = []
    if self.bridge and "id" in chat:
      chat_id = int(chat["id"])
      rows = self.bridge.last_messages_in_chat(chat_id, limit=60) # load messages
      for date_val, is_from_me, text, handle, kind in reversed(rows):
        normalized_text = (text or "").strip()
        if not normalized_text:
          normalized_text = "Shared an attachment."
        messages.append(
          {
            "text": text or "",
            "is_from_me": bool(is_from_me),
            "handle": handle,
            "date": date_val,
          }
        )
    for message in messages:
      self.message_layout.addWidget(self._build_message_bubble(message))
    self.message_layout.addStretch()

  def _load_chats(self):
    bridge = MessageBridge()
    chats = bridge.top_chats(limit=50)
    return chats

  def show_training_popup(self):
    if self._training_dialog is None:
      self._training_dialog = TrainingDialog(self)
    self._training_dialog.show()
    self._training_dialog.raise_()
    self._training_dialog.activateWindow()

  def hide_training_popup(self):
    if self._training_dialog is not None:
      self._training_dialog.close()

  def run_training_with_popup(self, training_fn: Callable[[], object]):
    self.show_training_popup()
    worker = TrainingWorker(training_fn)
    worker.completed.connect(lambda _: self.hide_training_popup())
    worker.failed.connect(lambda _: self.hide_training_popup())
    self._training_worker = worker
    worker.start()


def _login_with_apple(code: str) -> str:
  client_id = os.environ.get("APPLE_CLIENT_ID")
  client_secret = os.environ.get("APPLE_CLIENT_SECRET")
  redirect_uri = os.environ.get("APPLE_REDIRECT_URI")
  project_id = os.environ.get("FIREBASE_PROJECT_ID")
  if not client_id or not client_secret or not redirect_uri or not project_id:
    raise ValueError("Missing Apple or Firebase configuration environment variables.")

  try:
    from google.cloud import firestore
  except Exception as exc:  # pragma: no cover - dependency optional in tests
    raise ValueError("google-cloud-firestore is required for Apple login.") from exc

  firestore_client = firestore.Client(project=project_id)
  result = login.login_with_apple(
    code=code,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    firebase_client=firestore_client,
    token_exchange=lambda **kwargs: auth.exchange_code_for_tokens(
      token_url=login.APPLE_TOKEN_URL,
      code=kwargs["code"],
      client_id=kwargs["client_id"],
      client_secret=kwargs["client_secret"],
      redirect_uri=kwargs["redirect_uri"],
      code_verifier=kwargs.get("code_verifier"),
    ),
    jwt_decoder=auth.decode_jwt_without_verification,
  )
  return result["apple_sub"]


def main():
  app = QApplication(sys.argv)
  user_id = session.load_user_id()
  if not user_id:
    dialog = LoginDialog(_login_with_apple)
    if dialog.exec() != QDialog.Accepted:
      sys.exit(0)
    user_id = dialog.user_id()
    session.save_user_id(user_id)

  w = MainWindow(user_id=user_id)
  w.setMinimumSize(1100, 600)
  w.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()
