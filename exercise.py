import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFrame,
    QHBoxLayout,
)
from PySide6.QtGui import QDrag
from PySide6.QtCore import (
    QMimeData,
    Qt,
    QPoint,
)


class MyPushButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 确保每个按钮有唯一的 objectName，便于拖放时标识
        if not self.objectName():
            self.setObjectName(f"pushbutton_{id(self)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录鼠标点击时相对于控件（即按钮）左上角的偏移量，用于拖拽时保持光标与按钮的相对位置
            self._drag_hotspot = event.position().toPoint()
            # 用event.position().toPoint()获取的坐标作为拖拽图像下的“指针对齐点”
            drag = QDrag(self)
            drag.setHotSpot(event.position().toPoint())
            # 用mime携带当前按钮的objectName作为标识，拖动时用来找到当前拖动的是哪一个按钮
            mime = QMimeData()
            mime.setText(self.objectName())
            drag.setMimeData(mime)
            # 启动拖动，使用Move动作（表示移动而非复制）
            drag.exec(Qt.MoveAction)
        else:
            # 非左键交给父类默认处理（如点击行为）
            super().mousePressEvent(event)


class MyFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.Box)

        self.btn_1 = MyPushButton(self)
        self.btn_1.setText("push button 1")
        self.btn_1.move(100, 100)

        self.btn_2 = MyPushButton(self)
        self.btn_2.setText("push button 2")
        self.btn_2.move(200, 200)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        name = event.mimeData().text()
        widget = self.findChild(QPushButton, name)
        if widget:
            hotspot = getattr(widget, "_drag_hotspot", QPoint(0, 0))
            widget.move(event.position().toPoint() - hotspot)
            event.acceptProposedAction()
        else:
            event.ignore()


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.resize(600, 400)
        self.setAcceptDrops(True)

    def setupUi(self):
        self.frame_1 = MyFrame(self)
        self.frame_2 = MyFrame(self)
        h = QHBoxLayout(self)
        h.addWidget(self.frame_1)
        h.addWidget(self.frame_2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
