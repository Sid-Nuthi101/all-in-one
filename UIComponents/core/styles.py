"""Reusable style helpers for glassmorphism UI components."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from .tokens import COLORS, EFFECTS, RADII, SHADOWS, SPACING, TYPOGRAPHY


def glass_panel_style(
  *,
  variant: str = "primary",
  is_active: bool = False,
  is_disabled: bool = False,
  radius: Optional[int] = None,
  padding: Optional[int] = None,
) -> str:
  radius_value = radius if radius is not None else RADII.lg
  padding_value = padding if padding is not None else SPACING.lg
  border_width = EFFECTS.border_width_active if is_active else EFFECTS.border_width
  border_color = COLORS.border_active if is_active else COLORS.border
  background = COLORS.surface if variant == "primary" else COLORS.surface_alt
  text_color = COLORS.text_secondary if is_disabled else COLORS.text_primary
  return f"""
    QWidget {{
      background: {background};
      border-radius: {radius_value}px;
      border: {border_width}px solid {border_color};
      color: {text_color};
      padding: {padding_value}px;
      font-family: {TYPOGRAPHY.font_family};
    }}
  """.strip()


def apply_glass_panel(
  widget: QWidget,
  *,
  variant: str = "primary",
  is_active: bool = False,
  is_disabled: bool = False,
  radius: Optional[int] = None,
  padding: Optional[int] = None,
) -> None:
  widget.setStyleSheet(
    glass_panel_style(
      variant=variant,
      is_active=is_active,
      is_disabled=is_disabled,
      radius=radius,
      padding=padding,
    )
  )
  widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
  glow = QGraphicsDropShadowEffect()
  glow.setBlurRadius(EFFECTS.blur_radius)
  glow.setOffset(0, 0)
  glow.setColor(QColor(COLORS.glow if is_active else COLORS.border))
  widget.setGraphicsEffect(glow)


def pill_button_style(is_active: bool = False, is_disabled: bool = False) -> str:
  background = COLORS.surface_light if is_active else COLORS.surface
  border_color = COLORS.border_active if is_active else COLORS.border
  text_color = COLORS.text_secondary if is_disabled else COLORS.text_primary
  return f"""
    QPushButton {{
      background: {background};
      border-radius: {RADII.md}px;
      border: {EFFECTS.border_width}px solid {border_color};
      padding: {SPACING.sm}px {SPACING.lg}px;
      color: {text_color};
    }}
    QPushButton:hover {{
      border: {EFFECTS.border_width_active}px solid {COLORS.border_active};
      box-shadow: {SHADOWS.glow};
    }}
  """.strip()


def input_style(is_error: bool = False) -> str:
  border_color = COLORS.error if is_error else COLORS.border
  return f"""
    QLineEdit, QTextEdit {{
      background: {COLORS.surface_alt};
      border-radius: {RADII.md}px;
      border: {EFFECTS.border_width}px solid {border_color};
      padding: {SPACING.sm}px {SPACING.md}px;
      color: {COLORS.text_primary};
    }}
    QLineEdit:focus, QTextEdit:focus {{
      border: {EFFECTS.border_width_active}px solid {COLORS.border_active};
      box-shadow: {SHADOWS.glow};
    }}
  """.strip()
