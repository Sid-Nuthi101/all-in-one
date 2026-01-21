import sys
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtWidgets import (
  QApplication,
  QCompleter,
  QFrame,
  QHBoxLayout,
  QLabel,
  QPushButton,
  QComboBox,
  QScrollArea,
  QSplitter,
  QVBoxLayout,
  QWidget,
  QMainWindow,
  QSizePolicy,
  QLineEdit,
)

from contacts import ContactsConnector
from messages import MessageBridge
from logic import get_status


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
    left_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
    left_outer_layout = QVBoxLayout(left_container)
    left_outer_layout.setContentsMargins(0, 0, 0, 0)
    left_outer_layout.setSpacing(0)

    left_header = QWidget()
    left_header.setObjectName("leftHeader")
    left_header_layout = QHBoxLayout(left_header)
    left_header_layout.setContentsMargins(12, 12, 12, 8)
    left_header_layout.setSpacing(8)

    self.note_button = QPushButton("✨ Note")
    self.note_button.setObjectName("sparklyNoteButton")
    self.note_button.setCursor(Qt.PointingHandCursor)
    self.note_button.clicked.connect(self._toggle_note_overlay)

    left_header_layout.addWidget(self.note_button)
    left_header_layout.addStretch()
    left_outer_layout.addWidget(left_header)

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

    self.left_layout = left_layout
    self.left_scroll_contents = left_scroll_contents
    self.left_container = left_container

    self.note_overlay = QFrame(left_container)
    self.note_overlay.setObjectName("noteOverlay")
    self.note_overlay.setVisible(False)
    self.note_overlay_layout = QVBoxLayout(self.note_overlay)
    self.note_overlay_layout.setContentsMargins(16, 16, 16, 16)
    self.note_overlay_layout.setSpacing(10)

    overlay_header = QWidget()
    overlay_header_layout = QHBoxLayout(overlay_header)
    overlay_header_layout.setContentsMargins(0, 0, 0, 0)
    overlay_header_layout.setSpacing(8)

    overlay_title = QLabel("Sparkly note")
    overlay_title.setObjectName("noteOverlayTitle")

    self.note_overlay_close = QPushButton("✕")
    self.note_overlay_close.setObjectName("noteOverlayClose")
    self.note_overlay_close.setCursor(Qt.PointingHandCursor)
    self.note_overlay_close.clicked.connect(self._hide_note_overlay)

    overlay_header_layout.addWidget(overlay_title)
    overlay_header_layout.addStretch()
    overlay_header_layout.addWidget(self.note_overlay_close)

    self.note_recipient_dropdown = QComboBox()
    self.note_recipient_dropdown.setObjectName("noteRecipientDropdown")
    self.note_recipient_dropdown.setEditable(True)
    self.note_recipient_dropdown.setInsertPolicy(QComboBox.NoInsert)
    dropdown_line_edit = self.note_recipient_dropdown.lineEdit()
    dropdown_line_edit.setPlaceholderText("Search chats")
    completer = self.note_recipient_dropdown.completer()
    if completer is None:
      completer = QCompleter(self.note_recipient_dropdown.model(), self.note_recipient_dropdown)
      self.note_recipient_dropdown.setCompleter(completer)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setFilterMode(Qt.MatchContains)

    self.note_text_input = QLineEdit()
    self.note_text_input.setObjectName("noteTextInput")
    self.note_text_input.setPlaceholderText("What is it you'd like to send?")

    self.note_generate_button = QPushButton("Generate")
    self.note_generate_button.setObjectName("noteGenerateButton")
    self.note_generate_button.setCursor(Qt.PointingHandCursor)

    self.note_overlay_layout.addWidget(overlay_header)
    self.note_overlay_layout.addWidget(self.note_recipient_dropdown)
    self.note_overlay_layout.addWidget(self.note_text_input)
    self.note_overlay_layout.addWidget(self.note_generate_button)

    self.bridge = MessageBridge()
    chats = self._load_chats()

    self.chat_rows = []
    self.chat_list_snapshot = [(chat["id"], chat["name"], chat["preview"], chat["time"]) for chat in chats]
    self.chat_name_snapshot = []
    self._load_recipient_choices(chats)
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
    self.current_chat = None
    self.current_message_snapshot = []
    if self.chat_rows:
      self._select_chat(chats[0], self.chat_rows[0])

    self.poll_timer = QTimer(self)
    self.poll_timer.setInterval(5000)
    self.poll_timer.timeout.connect(self._poll_for_updates)
    self.poll_timer.start()

    app = QApplication.instance()
    if app:
      app.installEventFilter(self)

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
      QLabel#senderName {
        color: rgba(255, 255, 255, 0.75);
        font-size: 12px;
        font-weight: 500;
      }
      QLabel#senderAvatar {
        background-color: rgba(255, 255, 255, 0.18);
        color: #ffffff;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
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
      QLabel#participantNames {
        color: rgba(255, 255, 255, 0.6);
        font-size: 12px;
      }
      QWidget#leftHeader {
        background-color: rgba(255, 255, 255, 0.04);
      }
      QPushButton#sparklyNoteButton {
        background-color: rgba(139, 92, 246, 0.25);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #ffffff;
        border-radius: 12px;
        padding: 6px 12px;
        font-weight: 600;
      }
      QPushButton#sparklyNoteButton:hover {
        background-color: rgba(139, 92, 246, 0.4);
      }
      QPushButton#noteGenerateButton {
        background-color: rgba(139, 92, 246, 0.25);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #ffffff;
        border-radius: 12px;
        padding: 6px 12px;
        font-weight: 600;
      }
      QPushButton#noteGenerateButton:hover {
        background-color: rgba(139, 92, 246, 0.4);
      }
      QFrame#noteOverlay {
        background-color: rgba(20, 20, 24, 0.96);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
      }
      QLabel#noteOverlayTitle {
        color: #ffffff;
        font-weight: 600;
      }
      QPushButton#noteOverlayClose {
        background-color: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        font-size: 14px;
        padding: 2px 4px;
      }
      QPushButton#noteOverlayClose:hover {
        color: #ffffff;
      }
      QComboBox#noteRecipientDropdown,
      QLineEdit#noteTextInput {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        border-radius: 10px;
        padding: 6px 10px;
      }
      QComboBox#noteRecipientDropdown::drop-down {
        border: none;
        width: 20px;
      }
      QComboBox#noteRecipientDropdown QAbstractItemView {
        background-color: rgba(20, 20, 24, 0.98);
        color: #ffffff;
        selection-background-color: rgba(139, 92, 246, 0.5);
      }
      """
    )

  def resizeEvent(self, event):
    super().resizeEvent(event)
    self._position_note_overlay()

  def eventFilter(self, obj, event):
    if event.type() == QEvent.MouseButtonPress and self.note_overlay.isVisible():
      clicked_widget = QApplication.widgetAt(event.globalPosition().toPoint())
      if clicked_widget and self._is_overlay_related(clicked_widget):
        return super().eventFilter(obj, event)
      self._hide_note_overlay()
    return super().eventFilter(obj, event)

  def _is_overlay_related(self, widget):
    current = widget
    while current:
      if current in (self.note_overlay, self.note_button):
        return True
      current = current.parentWidget()
    return False

  def _position_note_overlay(self):
    if not self.note_overlay:
      return
    left_width = self.left_container.width()
    overlay_width = max(220, left_width - 24)
    self.note_overlay.setFixedWidth(overlay_width)
    self.note_overlay.adjustSize()
    self.note_overlay.move(12, 52)

  def _toggle_note_overlay(self):
    is_visible = self.note_overlay.isVisible()
    self.note_overlay.setVisible(not is_visible)
    if not is_visible:
      self.note_overlay.raise_()
      self._position_note_overlay()

  def _hide_note_overlay(self):
    if self.note_overlay.isVisible():
      self.note_overlay.setVisible(False)

  def _load_recipient_choices(self, chats):
    chat_names = []
    for chat in chats:
      name = chat.get("name")
      if name and name not in chat_names:
        chat_names.append(name)
    if chat_names == self.chat_name_snapshot:
      return
    self.chat_name_snapshot = chat_names
    current_text = self.note_recipient_dropdown.currentText()
    self.note_recipient_dropdown.blockSignals(True)
    self.note_recipient_dropdown.clear()
    self.note_recipient_dropdown.addItems(chat_names)
    self.note_recipient_dropdown.setCurrentIndex(-1)
    self.note_recipient_dropdown.blockSignals(False)
    if current_text:
      self.note_recipient_dropdown.setEditText(current_text)

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

    participants = chat.get("participants") or []
    participant_label = None
    if len(participants) > 1:
      participant_label = ElidedLabel(", ".join(participants))
      participant_label.setObjectName("participantNames")

    preview = ElidedLabel(chat["preview"])

    text_layout.addWidget(top_row)
    if participant_label:
      text_layout.addWidget(participant_label)
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
    self.current_chat = chat
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

  def _build_message_bubble(self, message, avatar_slot_width):
    wrapper = QWidget()
    wrapper_layout = QHBoxLayout(wrapper)
    wrapper_layout.setContentsMargins(0, 0, 0, 0)
    wrapper_layout.setSpacing(8)

    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(4)

    if message.get("show_sender_name"):
      sender = QLabel(message.get("sender_name", "Unknown"))
      sender.setObjectName("senderName")
      content_layout.addWidget(sender)

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
    content_layout.addWidget(bubble)

    avatar = None
    if message.get("show_avatar"):
      avatar = QLabel(message.get("avatar_initials", "?"))
      avatar.setObjectName("senderAvatar")
      avatar.setAlignment(Qt.AlignCenter)
      avatar.setFixedSize(32, 32)

    if message["is_from_me"]:
      wrapper_layout.addStretch()
      wrapper_layout.addWidget(content)
    else:
      if avatar:
        wrapper_layout.addWidget(avatar)
      else:
        spacer = QWidget()
        spacer.setFixedSize(avatar_slot_width, avatar_slot_width)
        wrapper_layout.addWidget(spacer)
      wrapper_layout.addWidget(content)
      wrapper_layout.addStretch()

    return wrapper

  def _get_message_snapshot(self, rows):
    return [(date_val, is_from_me, text, handle) for date_val, is_from_me, text, handle, _kind in rows]

  def _build_message_payload(self, rows):
    messages = []
    for date_val, is_from_me, text, handle, _kind in reversed(rows):
      normalized_text = (text or "").strip()
      if not normalized_text:
        normalized_text = "Shared an attachment."
      messages.append(
        {
          "text": text or normalized_text,
          "is_from_me": bool(is_from_me),
          "handle": handle,
          "date": date_val,
        }
      )
    return messages

  def _load_messages(self, chat):
    messages = []
    participants = chat.get("participants") or []
    is_group_chat = len(participants) > 1
    if self.bridge and "id" in chat:
      chat_id = int(chat["id"])
      rows = self.bridge.last_messages_in_chat(chat_id, limit=60)  # load messages
      self.current_message_snapshot = self._get_message_snapshot(rows)
      messages = self._build_message_payload(rows)
    self._render_messages(messages)

  def _render_messages(self, messages):
    self._clear_layout(self.message_layout)
    for message in messages:
      self.message_layout.addWidget(self._build_message_bubble(message, 32))
    self.message_layout.addStretch()
    QTimer.singleShot(0, self._scroll_messages_to_bottom)

  def _scroll_messages_to_bottom(self):
    scroll_bar = self.message_scroll.verticalScrollBar()
    scroll_bar.setValue(scroll_bar.maximum())

  def _refresh_chat_list(self):
    chats = self._load_chats()
    snapshot = [(chat["id"], chat["name"], chat["preview"], chat["time"]) for chat in chats]
    if snapshot == self.chat_list_snapshot:
      self._load_recipient_choices(chats)
      return chats

    self.chat_list_snapshot = snapshot
    self._load_recipient_choices(chats)
    self._clear_layout(self.left_layout)
    self.chat_rows = []
    for chat in chats:
      row = self._build_chat_row(chat)
      self.chat_rows.append(row)
      self.left_layout.addWidget(row)
      if self.current_chat and chat["id"] == self.current_chat.get("id"):
        self._set_row_selected(row, True)
    return chats

  def _poll_for_updates(self):
    chats = self._refresh_chat_list()
    if not self.current_chat:
      return

    current_chat_id = self.current_chat.get("id")
    if current_chat_id is None:
      return

    updated_chat = next((chat for chat in chats if chat["id"] == current_chat_id), None)
    if updated_chat:
      self.current_chat = updated_chat
      self.name_label.setText(updated_chat["name"])

    rows = self.bridge.last_messages_in_chat(int(current_chat_id), limit=60)
    snapshot = self._get_message_snapshot(rows)
    if snapshot != self.current_message_snapshot:
      self.current_message_snapshot = snapshot
      messages = self._build_message_payload(rows)
      self._render_messages(messages)

  def _load_chats(self):
    bridge = MessageBridge()
    chats = bridge.top_chats(limit=50)
    return chats


def main():
  app = QApplication(sys.argv)
  w = MainWindow()
  w.setMinimumSize(1100, 600)
  w.show()
  sys.exit(app.exec())


if __name__ == "__main__":
  main()
