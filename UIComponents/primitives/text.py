"""Typography components."""
from PySide6 import QtWidgets

from UIComponents.core.theme import resolve_tokens


class TextBase(QtWidgets.QLabel):
    def __init__(self, text: str, *, size: int, weight: int = 400, class_name: str = "", tokens=None):
        super().__init__(text)
        tokens = resolve_tokens(tokens)
        self.setObjectName(class_name or "TextBase")
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{"
            f"color: {tokens.colors.text_primary};"
            f"font-size: {size}px;"
            f"font-weight: {weight};"
            f"font-family: {tokens.typography.font_family};"
            "}}"
        )


class H1(TextBase):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        tokens_resolved = resolve_tokens(tokens)
        super().__init__(text, size=tokens_resolved.typography.h1_size, weight=600, class_name=class_name, tokens=tokens)


class H2(TextBase):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        tokens_resolved = resolve_tokens(tokens)
        super().__init__(text, size=tokens_resolved.typography.h2_size, weight=600, class_name=class_name, tokens=tokens)


class H3(TextBase):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        tokens_resolved = resolve_tokens(tokens)
        super().__init__(text, size=tokens_resolved.typography.h3_size, weight=600, class_name=class_name, tokens=tokens)


class Body(TextBase):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        tokens_resolved = resolve_tokens(tokens)
        super().__init__(text, size=tokens_resolved.typography.body_size, weight=400, class_name=class_name, tokens=tokens)


class Caption(TextBase):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        tokens_resolved = resolve_tokens(tokens)
        super().__init__(text, size=tokens_resolved.typography.caption_size, weight=400, class_name=class_name, tokens=tokens)


class Code(TextBase):
    def __init__(self, text: str, *, class_name: str = "", tokens=None):
        tokens_resolved = resolve_tokens(tokens)
        super().__init__(text, size=tokens_resolved.typography.code_size, weight=500, class_name=class_name, tokens=tokens)
        self.setStyleSheet(
            f"QLabel#{self.objectName()} {{"
            f"color: {tokens_resolved.colors.text_secondary};"
            f"font-size: {tokens_resolved.typography.code_size}px;"
            f"font-family: {tokens_resolved.typography.mono_family};"
            "}}"
        )
