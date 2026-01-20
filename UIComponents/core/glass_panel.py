from __future__ import annotations

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QWidget


def _qcolor(value: str, alpha: float) -> QColor:
  c = QColor(value)
  c.setAlphaF(max(0.0, min(1.0, alpha)))
  return c


def _blur_pixmap(src: QPixmap, downsample: int = 3) -> QPixmap:
  if src.isNull():
    return src
  ds = max(1, int(downsample))
  small = src.scaled(
    max(1, src.width() // ds),
    max(1, src.height() // ds),
    Qt.AspectRatioMode.IgnoreAspectRatio,
    Qt.TransformationMode.SmoothTransformation,
  )
  return small.scaled(
    src.width(),
    src.height(),
    Qt.AspectRatioMode.IgnoreAspectRatio,
    Qt.TransformationMode.SmoothTransformation,
  )


class GlassPanel(QWidget):
  def __init__(
    self,
    *,
    tint: str,
    tint_alpha: float,
    border: str,
    border_alpha: float,
    radius: int,
    downsample: int = 3,
    parent: QWidget | None = None,
  ):
    super().__init__(parent)
    self.tint = tint
    self.tint_alpha = tint_alpha
    self.border = border
    self.border_alpha = border_alpha
    self.radius = radius
    self.downsample = downsample

    self._cached_bg = QPixmap()
    self._capture_scheduled = False
    self._capture_parent = None

    self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    # Watch parent changes/resize/moves to refresh cache.
    self.set_capture_parent(parent)

  def set_capture_parent(self, parent: QWidget | None) -> None:
    if parent is self._capture_parent:
      return
    if self._capture_parent is not None:
      self._capture_parent.removeEventFilter(self)
    self._capture_parent = parent
    if parent is not None:
      parent.installEventFilter(self)

  def eventFilter(self, obj, event):
    t = event.type()
    if t in (
      QEvent.Type.Resize,
      QEvent.Type.Move,
      QEvent.Type.Paint,
      QEvent.Type.UpdateRequest,
    ):
      # Don’t capture on every paint synchronously; just schedule.
      self.schedule_capture()
    return super().eventFilter(obj, event)

  def schedule_capture(self) -> None:
    if self._capture_scheduled:
      return
    self._capture_scheduled = True
    QTimer.singleShot(0, self._capture_background)

  def _capture_background(self) -> None:
    self._capture_scheduled = False
    par = self.parentWidget()
    if par is None or not self.isVisible():
      return

    # IMPORTANT: we’re not in our paintEvent anymore (queued), so grab is safe.
    pm = par.grab(self.geometry())
    self._cached_bg = _blur_pixmap(pm, downsample=self.downsample)
    self.update()

  def showEvent(self, event):
    super().showEvent(event)
    self.schedule_capture()

  def resizeEvent(self, event):
    super().resizeEvent(event)
    self.schedule_capture()

  def moveEvent(self, event):
    super().moveEvent(event)
    self.schedule_capture()

  def paintEvent(self, event):
    p = QPainter(self)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    r = self.rect()
    if r.width() <= 1 or r.height() <= 1:
      return

    path = QPainterPath()
    path.addRoundedRect(r, self.radius, self.radius)
    p.setClipPath(path)

    if not self._cached_bg.isNull():
      p.drawPixmap(0, 0, self._cached_bg)

    # Tint overlay
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(_qcolor(self.tint, self.tint_alpha))
    p.drawRoundedRect(r, self.radius, self.radius)

    # Highlight edge
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(_qcolor("#FFFFFF", 0.10))
    p.drawRoundedRect(r.adjusted(1, 1, -1, -1), self.radius, self.radius)

    # Border
    p.setPen(_qcolor(self.border, self.border_alpha))
    p.drawRoundedRect(r.adjusted(0, 0, -1, -1), self.radius, self.radius)

    p.end()
