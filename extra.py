# 简单图像查看器示例（PySide6）
#
# 功能：
#   1. 菜单"文件 -> 打开"或双击窗口，选择图片（png/jpeg/jpg）
#   2. 按住 Ctrl + 鼠标左键拖拽：平移图片
#   3. 按住 Ctrl + 滚动鼠标滚轮：缩放图片
#
# Qt 的绘制机制：窗口内容不是"画一次就永远留在屏幕上"，
# 而是在需要时由系统反复调用 paintEvent() 重新绘制。
# 所以"移动/缩放"其实只是修改了记录位置的变量，再调用 update()
# 请求一次重绘，paintEvent 里就会用新位置重新画。

import sys

from PySide6.QtCore import QRect, Qt, QPoint
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import (
    QFileDialog,
    QMenuBar,
    QWidget,
    QApplication,
)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)

        # ---------- 图片状态变量 ----------
        self.pixmap = QPixmap()            # 存放图片的对象；空 QPixmap 表示还没打开图片
        self.pix_width = 0                 # 图片绘制区域的半宽（完整宽度 = 2 * pix_width）
        self.pix_height = 0                # 图片绘制区域的半高（完整高度 = 2 * pix_height）
        self.translate_x = 0               # x 方向平移量，paintEvent 里叠加到 center 上
        self.translate_y = 0               # y 方向平移量
        self.pixmap_scale_x = 0.0          # 缩放时 x 方向分配的比例（按图片长宽比计算）
        self.pixmap_scale_y = 0            # 缩放时 y 方向分配的比例
        self.start = QPoint(0, 0)          # 记录鼠标按下时的位置，用于计算拖拽位移
        # 图片中心点，初始设在窗口中央（此时窗口是 600x600，中心即 300,300）
        self.center = QPoint(int(self.width() / 2), int(self.height() / 2))

        # ---------- 菜单栏 ----------
        menuBar = QMenuBar(self)
        menuFile = menuBar.addMenu("文件(&F)")
        menuFile.addAction("打开(&O)").triggered.connect(self.actionOpen_triggered)
        menuFile.addSeparator()
        menuFile.addAction("退出(&E)").triggered.connect(self.close)

    def paintEvent(self, event):
        """窗口绘制函数：窗口首次显示、尺寸变化或调用 update() 时由 Qt 自动调用"""
        # 把记录的平移量累加到中心点，实现"拖拽移动图片"
        self.center = QPoint(self.center.x() + self.translate_x, self.center.y() + self.translate_y)
        # 以中心点为中心，按半宽/半高算出图片绘制区域的左上角和右下角
        point_1 = QPoint(self.center.x() - self.pix_width, self.center.y() - self.pix_height)
        point_2 = QPoint(self.center.x() + self.pix_width, self.center.y() + self.pix_height)
        rect = QRect(point_1, point_2)          # 图片最终绘制到窗口上的矩形区域

        painter = QPainter(self)                # QPainter：负责在窗口上画图的对象
        painter.drawPixmap(rect, self.pixmap)   # 把图片拉伸填满 rect（rect 变化 = 缩放/平移）

    def mousePressEvent(self, event):
        """鼠标按下：记住按下位置，作为拖拽位移的计算基准"""
        self.start = event.position()      # 鼠标当前位置

    def mouseMoveEvent(self, event):
        """鼠标移动：Ctrl + 左键按住时进入"平移模式"""
        if event.modifiers() == Qt.ControlModifier and event.buttons() == Qt.LeftButton:
            # 用"当前位置 - 按下位置"算出本次的移动量
            self.translate_x = event.position().x() - self.start.x()
            self.translate_y = event.position().y() - self.start.y()
            self.start = event.position()  # 更新基准点，下次移动时继续累加
            self.update()                  # 请求重绘，paintEvent 里会把平移量应用上

    def wheelEvent(self, event):
        """滚轮：按住 Ctrl + 滚动时缩放图片"""
        if event.modifiers() == Qt.ControlModifier:
            # 限制最小尺寸（10px）防止缩没了；向上滚（y>0）允许放大，向下滚时受此限制
            if (self.pix_width > 10 and self.pix_height > 10) or event.angleDelta().y() > 0:
                # 滚轮刻度 delta 折算成像素增量，再按长宽比例分别加到宽高上
                self.pix_width = self.pix_width + int(event.angleDelta().y() / 10 * self.pixmap_scale_x)
                self.pix_height = self.pix_height + int(event.angleDelta().y() / 10 * self.pixmap_scale_y)
                self.update()              # 请求重绘，paintEvent 会以新尺寸绘制

    def mouseDoubleClickEvent(self, event):
        """双击：直接弹出打开文件对话框"""
        self.actionOpen_triggered()

    def actionOpen_triggered(self):
        """打开图片：弹对话框选文件，加载后初始化尺寸和缩放比例"""
        fileDialog = QFileDialog(self)
        fileDialog.setNameFilter("图像文件( * .png * .jpeg * .jpg)")
        fileDialog.setFileMode(QFileDialog.ExistingFile)   # 只能选择已存在的单个文件
        if fileDialog.exec():              # 弹出对话框；用户点"打开"时返回 True
            self.pixmap.load(fileDialog.selectedFiles()[0])   # 从磁盘文件加载图片
            self.pix_width = int(self.pixmap.width() / 2)     # 半宽 = 图片真实宽度的一半
            self.pix_height = int(self.pixmap.height() / 2)   # 半高 = 图片真实高度的一半
            # 缩放比例按图片长宽比分配：长边缩得多、短边缩得少，保持比例不变形
            self.pixmap_scale_x = self.pix_width / (self.pix_width + self.pix_height)
            self.pixmap_scale_y = self.pix_height / (self.pix_width + self.pix_height)
            # 中心点重置回窗口中央，让新图片从中间显示
            self.center = QPoint(int(self.width() / 2), int(self.height() / 2))
            self.update()                  # 请求重绘，把图片画出来

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()  # 接受拖入的文件
        else:
            event.ignore()  # 忽略其他类型的拖入事件

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        fileName = urls[0].toLocalFile()  # 获取拖入的第一个文件路径
        self.pixmap.load(fileName)        # 从磁盘文件加载图片
        self.pix_width = int(self.pixmap.width() / 2)     # 半宽 = 图片真实宽度的一半
        self.pix_height = int(self.pixmap.height() / 2)   # 半高 = 图片真实高度的一半
        # 缩放比例按图片长宽比分配：长边缩得多、短边缩得少，保持比例不变形
        self.pixmap_scale_x = self.pix_width / (self.pix_width + self.pix_height)
        self.pixmap_scale_y = self.pix_height / (self.pix_width + self.pix_height)
        # 中心点重置回窗口中央，让新图片从中间显示
        self.center = QPoint(int(self.width() / 2), int(self.height() / 2))
        self.update()                      # 请求重绘，把图片画出来


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()                          # 显示窗口，同时触发第一次 paintEvent
    sys.exit(app.exec())
