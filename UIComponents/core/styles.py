"""Reusable style helpers for glassmorphism UI components."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, QObject, QPointer, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from shiboken6 import isValid

from .glass_panel import GlassPanel
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


def _color_to_hex_alpha(value: str) -> tuple[str, float]:
  color = QColor(value)
  return color.name(), color.alphaF()


def _glass_tint_from_color(value: str, *, lighten: int = 135, alpha_scale: float = 0.35) -> tuple[str, float]:
  color = QColor(value)
  color = color.lighter(lighten)
  return color.name(), max(0.0, min(1.0, color.alphaF() * alpha_scale))


class _GlassOverlayBinder(QObject):
  def __init__(self, widget: QWidget, overlay: GlassPanel):
    super().__init__(widget)
    self.widget = QPointer(widget)
    self.overlay = overlay
    self.parent = QPointer(widget.parentWidget()) if widget.parentWidget() is not None else QPointer()
    widget.installEventFilter(self)
    if self.parent:
      self.parent.installEventFilter(self)
    widget.destroyed.connect(self._on_widget_destroyed)
    self.sync()

  def eventFilter(self, obj, event):
    widget = self.widget
    if not isValid(widget):
      return False
    t = event.type()
    if obj is widget and t in (
      QEvent.Type.Move,
      QEvent.Type.Resize,
      QEvent.Type.Show,
      QEvent.Type.Hide,
      QEvent.Type.ParentChange,
    ):
      self.sync()
    elif isValid(self.parent) and obj is self.parent and t in (
      QEvent.Type.Resize,
      QEvent.Type.Move,
    ):
      self.sync()
    return super().eventFilter(obj, event)

  def _on_widget_destroyed(self) -> None:
    self.overlay.hide()
    self.overlay.set_capture_parent(None)
    self.overlay.setParent(None)

  def sync(self) -> None:
    widget = self.widget
    if not isValid(widget):
      self.overlay.hide()
      self.overlay.set_capture_parent(None)
      self.overlay.setParent(None)
      return
    parent = widget.parentWidget()
    if parent is None:
      self.overlay.hide()
      self.overlay.set_capture_parent(None)
      self.overlay.setParent(None)
      return
    if not isValid(self.parent) or self.parent is not parent:
      if isValid(self.parent):
        self.parent.removeEventFilter(self)
      self.parent = QPointer(parent)
      self.parent.installEventFilter(self)
    if self.overlay.parentWidget() is not parent:
      self.overlay.setParent(parent)
      self.overlay.set_capture_parent(parent)
    self.overlay.setGeometry(widget.geometry())
    self.overlay.stackUnder(widget)
    if widget.isVisible():
      self.overlay.show()
      self.overlay.schedule_capture()
    else:
      self.overlay.hide()

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
  border_color = COLORS.border_active if is_active else COLORS.border
  background = COLORS.surface if variant == "primary" else COLORS.surface_alt
  text_color = COLORS.text_secondary if is_disabled else COLORS.text_primary

  name = widget.objectName()
  widget.setStyleSheet(
    f"""
    QWidget#{name} {{
      background: transparent;
      border-radius: {radius_value}px;
      border: none;
      color: {text_color};
      padding: {padding_value}px;
      font-family: {TYPOGRAPHY.font_family};
    }}
    """.strip()
  )
  widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

  tint_color, tint_alpha = _glass_tint_from_color(background)
  border_hex, border_alpha = _color_to_hex_alpha(border_color)
  if is_active:
    tint_alpha = min(1.0, tint_alpha + 0.05)
  if is_disabled:
    tint_alpha *= 0.7
    border_alpha *= 0.6

  overlay = getattr(widget, "_glass_overlay", None)
  if overlay is None:
    overlay = GlassPanel(
      tint=tint_color,
      tint_alpha=tint_alpha,
      border=border_hex,
      border_alpha=border_alpha,
      radius=radius_value,
      parent=widget.parentWidget(),
    )
    widget._glass_overlay = overlay
  else:
    overlay.tint = tint_color
    overlay.tint_alpha = tint_alpha
    overlay.border = border_hex
    overlay.border_alpha = border_alpha
    overlay.radius = radius_value

  glow = QGraphicsDropShadowEffect()
  glow.setBlurRadius(EFFECTS.blur_radius)
  glow.setOffset(0, 0)
  glow.setColor(QColor(COLORS.glow if is_active else COLORS.border))
  overlay.setGraphicsEffect(glow)

  binder = getattr(widget, "_glass_overlay_binder", None)
  if binder is None:
    widget._glass_overlay_binder = _GlassOverlayBinder(widget, overlay)
  else:
    binder.sync()


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
