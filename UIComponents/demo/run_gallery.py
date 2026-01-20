from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from UIComponents.demo.gallery import ComponentGallery


def main() -> int:
  app = QApplication(sys.argv)
  gallery = ComponentGallery()
  gallery.resize(1200, 800)
  gallery.setWindowTitle("UIComponents Gallery")
  gallery.show()
  return app.exec()


if __name__ == "__main__":
  raise SystemExit(main())
