"""Reusable style builders."""
from typing import Optional

from .tokens import DesignTokens
from .theme import resolve_tokens


def glass_panel_style(
    tokens: Optional[DesignTokens] = None,
    *,
    radius: Optional[int] = None,
    is_active: bool = False,
) -> str:
    tokens = resolve_tokens(tokens)
    colors = tokens.colors
    radius = radius or tokens.radius.lg
    border_color = colors.border_active if is_active else colors.border
    return (
        f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        f"stop:0 {colors.surface}, stop:1 {colors.surface_alt});"
        f"border: 1px solid {border_color};"
        f"border-radius: {radius}px;"
        f"color: {colors.text_primary};"
    )


def neon_border_style(
    tokens: Optional[DesignTokens] = None,
    *,
    intensity: float = 0.6,
    radius: Optional[int] = None,
) -> str:
    tokens = resolve_tokens(tokens)
    colors = tokens.colors
    radius = radius or tokens.radius.md
    glow_color = colors.accent
    return (
        f"border: 1px solid rgba(110, 231, 255, {intensity});"
        f"border-radius: {radius}px;"
        f"box-shadow: 0 0 12px rgba(110, 231, 255, {intensity});"
        f"color: {colors.text_primary};"
        f"background: transparent;"
    )


def gradient_background_style(
    tokens: Optional[DesignTokens] = None,
    *,
    direction: str = "vertical",
) -> str:
    tokens = resolve_tokens(tokens)
    colors = tokens.colors
    if direction == "horizontal":
        return (
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {colors.background}, stop:1 {colors.surface_alt});"
        )
    return (
        f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        f"stop:0 {colors.background}, stop:1 {colors.surface_alt});"
    )
