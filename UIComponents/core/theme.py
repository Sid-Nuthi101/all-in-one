"""Theme handling for the UI kit."""
from dataclasses import dataclass
from typing import Optional

from .tokens import DARK_GLASS, DesignTokens, THEMES


@dataclass
class Theme:
    name: str = "DarkGlass"
    tokens: DesignTokens = DARK_GLASS

    @classmethod
    def from_name(cls, name: str) -> "Theme":
        tokens = THEMES.get(name, DARK_GLASS)
        return cls(name=name, tokens=tokens)


CURRENT_THEME: Theme = Theme()


def set_theme(name: str) -> Theme:
    global CURRENT_THEME
    CURRENT_THEME = Theme.from_name(name)
    return CURRENT_THEME


def get_theme() -> Theme:
    return CURRENT_THEME


def resolve_tokens(tokens: Optional[DesignTokens]) -> DesignTokens:
    return tokens or CURRENT_THEME.tokens
