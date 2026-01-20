"""Label + input + help text row."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class FieldRow(QtWidgets.QFrame):
    def __init__(self, label: str, input_widget: QtWidgets.QWidget, help_text: str = "", *, class_name: str = "", tokens=None):
        super().__init__()
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "FieldRow")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label_widget = QtWidgets.QLabel(label)
        label_widget.setStyleSheet(
            f"color: {tokens.colors.text_secondary};"
            f"font-size: {tokens.typography.caption_size}px;"
        )
        layout.addWidget(label_widget)
        layout.addWidget(input_widget)
        if help_text:
            help_label = QtWidgets.QLabel(help_text)
            help_label.setStyleSheet(
                f"color: {tokens.colors.text_muted};"
                f"font-size: {tokens.typography.caption_size}px;"
            )
            layout.addWidget(help_label)
