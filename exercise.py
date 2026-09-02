import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFileDialog,
    QMenu,
)
from PySide6.QtGui import (
    QPixmap,
    QPainter,
)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.setAcceptDrops(True)
        self.resize(600, 400)
        self.pixmap = QPixmap()

    def contextMenuEvent(self, event, /):
        contextMenu = QMenu(self)
        contextMenu.addAction("Open").triggered.connect(self.actionOpen_triggered)
        contextMenu.addSeparator()
        contextMenu.addAction("Exit").triggered.connect(self.close)
        contextMenu.exec(event.globalPos())

    def paintEvent(self, event, /):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    def mouseDoubleClickEvent(self, event, /):
        self.actionOpen_triggered()

    def actionOpen_triggered(self):
        fileDialog = QFileDialog(self)
        fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if fileDialog.exec():
            self.pixmap.load(fileDialog.selectedFiles()[0])
            self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
