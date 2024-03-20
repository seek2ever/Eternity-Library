import os
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QDesktopWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5 import QtCore, QtGui, QtWidgets


class MyWindow(QMainWindow):
    def __init__(self):                         # 初始化窗口
        super().__init__()                      # 调用父类的初始化方法
        self.statusbar = None
        self.menubar = None
        self.setup_ui()                         # 设置窗口的属性

    def setup_ui(self):
        # 创建主窗口
        self.setObjectName("MainWindow")                                    # 设置窗口的对象名称
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))  # 设置窗口的标题名称
        self.setGeometry(200, 200, 1920, 1080)                              # 设置窗口的位置和大小
        # 创建菜单栏
        self.menubar = QtWidgets.QMenuBar(self)                         # 创建一个菜单栏，分配实际的QtWidgets.QMenuBar对象
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))           # 设置菜单栏的位置和大小
        self.menubar.setObjectName("menubar")                           # 设置菜单栏的对象名称
        self.setMenuBar(self.menubar)                                   # 设置窗口的菜单栏
        # 创建状态栏
        self.statusbar = QtWidgets.QStatusBar(self)                     # 创建一个状态栏，分配实际的QtWidgets.QStatusBar对象
        self.statusbar.setObjectName("statusbar")                       # 设置状态栏的对象名称
        self.setStatusBar(self.statusbar)                               # 设置窗口的状态栏

    def _translate(self, context, text):
        """翻译标题栏文本"""
        return QCoreApplication.translate(context, text)


if __name__ == '__main__':
    app = QApplication(sys.argv)                           # sys.argv用于获取当前正在执行的命令行参数的参数列表
    window = MyWindow()                                    # 创建PyQt设计的窗口对象
    window.setup_ui()                                      # 设置窗口的属性
    window.show()                                          # 显示窗口
    sys.exit(app.exec_())                                  # 进入程序主循环，事件处理器，等待用户交互，直到用户关闭窗口或程序终止
