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
            # drag.setHotSpot(self._drag_hotspot)

            mime = QMimeData()
            # 设置拖动数据为按钮的objectName，便于在dropEvent中识别拖动的按钮
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
        self.setFrameShape(QFrame.NoFrame)

        self.btn = MyPushButton(self)
        self.btn.setText("拖拽按钮")
        self.btn.setGeometry(50, 50, 200, 100)

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
        """
        处理拖拽移动事件，拖拽过程中重复判断拖拽的数据类型是否为文本类型。
        :param event: QDragMoveEvent类的实例对象
        :return: None
        """
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        处理拖拽释放事件，当拖拽的按钮被释放时，找到按钮并计算新位置，随后更新按钮坐标。
        :param event: QDropEvent类的实例对象
        :return: None
        """
        # 1. 从拖拽数据中读取被拖动按钮的objectName
        # 在 mousePressEvent 中，mime.setText(self.objectName())
        # 所以这里拿到的就是被拖动按钮的唯一标识，例如 "pushbutton_1234"
        name = event.mimeData().text()

        # 2. 在self的子控件中查找一个QPushButton的objectName等于name的控件
        btn = self.findChild(QPushButton, name)

        if btn:
            # 3. getattr()解释：获取拖动开始时的偏移量_drag_hotspot；若不存在，否则返回默认坐标值QPoint(0, 0)
            hotspot = getattr(btn, "_drag_hotspot", QPoint(0, 0))

            # 4. 计算按钮的新位置
            # 事件中鼠标当前位置是 event.position().toPoint()
            # 按钮左上角应该放在 "鼠标位置 - hotspot"，这样拖拽时不会发生跳动。
            btn.move(event.position().toPoint() - hotspot)
            btn.show()

            # 5. 通知 Qt：本次拖放操作已处理完成
            event.acceptProposedAction()
        else:
            # 目标控件中没有找到对应按钮，说明不是当前拖放对象，忽略事件
            event.ignore()


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.resize(600, 400)
        self.setAcceptDrops(True)

    def setupUi(self):
        self.frame = MyFrame(self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
