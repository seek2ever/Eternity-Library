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
    """
    自定义QPushButton类，作为源对象，负责发起拖拽
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 确保每个按钮有唯一的 objectName，便于拖放时标识
        if not self.objectName():
            self.setObjectName(f"pushbutton_{id(self)}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            """
                self._drag_hotspot用于记录鼠标点击时相对于按钮左上角的偏移量（存储在按钮上），
                没有self._drag_hotspot的话，松手的一瞬间按钮会从"跟随鼠标"突然变成"左上角对齐鼠标"，
                因为这个"偏差"（hotspot）才是维持按下时相对位置的关键。
            """
            self._drag_hotspot = event.position().toPoint()
            drag = QDrag(self)
            # 影响拖拽过程中按钮和鼠标的相对位置，确保拖动时按钮不会跳到鼠标左上角
            drag.setHotSpot(self._drag_hotspot)

            mime = QMimeData()
            # 设置拖动数据为按钮的 objectName，便于在 dropEvent 中识别拖动的按钮
            mime.setText(self.objectName())
            drag.setMimeData(mime)
            # 启动拖动，使用Move动作（表示移动而非复制）
            drag.exec(Qt.MoveAction)
        else:
            # 非左键交给父类默认处理（如点击行为）
            super().mousePressEvent(event)


class MyFrame(QFrame):
    """
    自定义QFrame类，作为目标对象，负责接收拖拽
    """
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
        """
        处理拖拽进入事件，判断拖拽的数据类型是否为文本类型。
        :param event: QDragEnterEvent类的实例对象
        :return: None
        """
        # 继承关系：QDropEvent -> QDragMoveEvent -> QDragEnterEvent，mimeData()方法属于QDropEvent类
        # mimeData()方法返回一个QMimeData对象，包含拖拽的数据类型和数据内容，hasText()方法判断是否包含文本类型的数据
        if event.mimeData().hasText():
            # 如果拖拽的数据类型为文本类型，则接受拖拽事件，允许拖拽操作继续进行
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
