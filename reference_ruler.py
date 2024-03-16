import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint


class Ruler(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(75, 1100)
        self.setStyleSheet("background-color: lightblue; border: 1px solid black;")

        self.dragging = False
        self.offset = QPoint()

    def keyPressEvent(self, event):
        step = 10  # 移动步长
        if event.key() == Qt.Key_Up:
            self.move(self.x(), self.y() - step)
        elif event.key() == Qt.Key_Down:
            self.move(self.x(), self.y() + step)
        elif event.key() == Qt.Key_Left:
            self.move(self.x() - step, self.y())
        elif event.key() == Qt.Key_Right:
            self.move(self.x() + step, self.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ruler = Ruler()
    ruler.show()
    sys.exit(app.exec_())
