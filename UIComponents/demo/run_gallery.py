from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

if __package__ is None:
  sys.path.append(str(Path(__file__).resolve().parents[2]))
  from UIComponents.demo.gallery import ComponentGallery
else:
  from .gallery import ComponentGallery


def main() -> int:
  app = QApplication(sys.argv)
  gallery = ComponentGallery()
  gallery.resize(1200, 800)
  gallery.setWindowTitle("UIComponents Gallery")
  gallery.show()
  return app.exec()


if __name__ == "__main__":
  raise SystemExit(main())
