import sys

from PySide6.QtCore import QRect, Qt, QPoint, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QPushButton,
)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.btn = QPushButton("拖拽我", self)
        self.btn.setGeometry(QRect(100, 100, 100, 30))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_hotspot = event.position().toPoint()
            drag = QDrag(self)
            drag.setHotSpot(self._drag_hotspot)

            mime = QMimeData()
            mime.setText()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
