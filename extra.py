import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtCore import Qt, QPoint


class MyPushButton(QPushButton):
    """
    自定义QPushButton类，支持按住左键直接拖动按钮。

    不用 QDrag 的原因：QDrag 启动拖拽期间，Qt 会把源控件（按钮）隐藏起来，
    直到松开鼠标才重新显示，所以拖动过程中按钮会"消失"。
    这里改用鼠标事件手动移动按钮，按钮本体始终可见、跟随鼠标。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("push_button")
        self._dragging = False
        # 记录按下瞬间鼠标相对按钮左上角的偏移，保证拖动时按钮不跳动
        self._drag_offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            # position() 返回鼠标相对按钮左上角的坐标，作为偏移量保存
            self._drag_offset = event.position().toPoint()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 按住左键拖动时，让按钮跟随鼠标移动
        if self._dragging:
            self._move_to(event.globalPosition().toPoint())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _move_to(self, global_pos):
        # 先把鼠标全局坐标换算成父窗口坐标系，再减去偏移量，即为按钮左上角的新位置
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.mapFromGlobal(global_pos) - self._drag_offset)


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.resize(600, 400)

        self.btn = MyPushButton(self)
        self.btn.setText("拖拽按钮")
        self.btn.setGeometry(50, 50, 200, 100)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
