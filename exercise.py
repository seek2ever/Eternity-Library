import sys

from PySide6.QtGui import QFont, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QWidget,
    QLabel,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QTextEdit,
)
from PySide6.QtCore import Qt, QEvent


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QMouseEvent示例')
        self.resize(800, 600)
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        self.label = QLabel("默认文本")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAcceptDrops(True)
        self.btn = QPushButton("点击我")

        self.text_box = QTextEdit()

        self.frame = QFrame()

        layout = QGridLayout(self)
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.btn, 0, 1)
        layout.addWidget(self.text_box, 1, 0)
        layout.addWidget(self.frame, 1, 1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        for w in (self.label, self.btn, self.text_box, self.frame):
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            w.setFont(QFont("Microsoft YaHei", 12))

    def dragEnterEvent(self, event):
        if event.type() == QEvent.DragEnter:
            pass

    def dragLeaveEvent(self, event):
        self.label.setText("鼠标移出")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())
