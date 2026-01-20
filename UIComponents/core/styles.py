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
  radius_value = radius if radius is not None else RADII.sm
  padding_value = padding if padding is not None else SPACING.lg

  border_width = EFFECTS.border_width_active if is_active else EFFECTS.border_width
  border_color = COLORS.border_active if is_active else COLORS.border

  base = COLORS.surface if variant == "primary" else COLORS.surface_alt

  # Key: extremely low opacity
  fill_alpha = 0.08 if not is_active else 0.12
  fill_alpha = 0.05 if is_disabled else fill_alpha

  border_alpha = 0.30 if not is_active else 0.50
  text_color = COLORS.text_secondary if is_disabled else COLORS.text_primary

  def rgba(hex_color: str, a: float) -> str:
    c = hex_color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return f"rgba({r},{g},{b},{a})"

  bg_top = rgba(base, fill_alpha + 0.03)
  bg_bottom = rgba(base, fill_alpha)
  border_rgba = rgba(border_color, border_alpha)

  return f"""
    QWidget {{
      background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {bg_top},
        stop:1 {bg_bottom}
      );
      border-radius: {radius_value}px;
      border: {border_width}px solid {border_rgba};
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
  if not widget.objectName():
    widget.setObjectName(widget.__class__.__name__)

  widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

  radius_value = radius if radius is not None else RADII.lg
  padding_value = padding if padding is not None else SPACING.lg
  border_width = EFFECTS.border_width_active if is_active else EFFECTS.border_width
  border_color = COLORS.border_active if is_active else COLORS.border
  background = COLORS.surface if variant == "primary" else COLORS.surface_alt
  text_color = COLORS.text_secondary if is_disabled else COLORS.text_primary

  name = widget.objectName()
  widget.setStyleSheet(
    f"""
    QWidget#{name} {{
      background: {background};
      border-radius: {radius_value}px;
      border: {border_width}px solid {border_color};
      color: {text_color};
      padding: {padding_value}px;
      font-family: {TYPOGRAPHY.font_family};
    }}
    """.strip()
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
    }}
  """.strip()
