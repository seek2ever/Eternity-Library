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
        self.setAcceptDrops(True)
        self.btn = QPushButton("拖拽我", self)
        self.btn.setGeometry(QRect(100, 100, 100, 30))
        self.btn.setObjectName("my_btn")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_hotspot = event.position().toPoint()
            drag = QDrag(self)
            drag.setHotSpot(self._drag_hotspot)

            mime = QMimeData()
            mime.setText("my_btn")
            drag.setMimeData(mime)
            drag.exec(Qt.MoveAction)
    
    def dropEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
