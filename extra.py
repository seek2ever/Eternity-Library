import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QMenu,
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtCore import QRect


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 300)
        self.setup_ui()

    def setup_ui(self):
        self.local_label = QLabel(self)
        self.local_label.setFont(QFont("Arial", 30))
        self.local_label.setGeometry(QRect(200, 0, 200, 100))
        self.local_label.setText("hello")

        self.global_label = QLabel(self)
        self.global_label.setFont(QFont("Arial", 30))
        self.global_label.setGeometry(QRect(200, 100, 200, 100))
        self.global_label.setText("global")

    def contextMenuEvent(self, event):
        local_pos = event.pos()
        global_pos = event.globalPos()
        context_menu = QMenu(self)
        context_menu.addAction("获取指针在窗口的坐标").triggered.connect(lambda: self.left_btn(local_pos))
        context_menu.addAction("获取鼠标在全局的坐标").triggered.connect(lambda: self.right_btn(global_pos))
        context_menu.exec(event.globalPos())

    def left_btn(self, pos):
        self.local_label.setText(f"{pos.x()}, {pos.y()}")

    def right_btn(self, pos):
        self.global_label.setText(f"{pos.x()}, {pos.y()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
