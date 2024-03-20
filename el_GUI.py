import os
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QDesktopWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets


class MyWindow(object):
    def setup_ui(self, MainWindow):
        # 创建主窗口
        MainWindow.setObjectName("MainWindow")                     # 设置窗口的对象名称
        MainWindow.setWindowTitle("标题栏")                         # 设置窗口的标题名称
        MainWindow.setGeometry(1000, 700, 400, 200)                # 设置窗口的位置和大小
        # 创建菜单栏
        self.menubar = QtWidgets.QMenuBar(MainWindow)              # 创建一个菜单栏
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))      # 设置菜单栏的位置和大小
        self.menubar.setObjectName("menubar")                      # 设置菜单栏的对象名称
        MainWindow.setMenuBar(self.menubar)
        # 创建状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)          # 创建一个状态栏
        self.statusbar.setObjectName("statusbar")                  # 设置状态栏的对象名称
        MainWindow.setStatusBar(self.statusbar)                    # 设置窗口的状态栏


if __name__ == '__main__':
    app = QApplication(sys.argv)                           # sys.argv用于获取当前正在执行的命令行参数的参数列表
    MainWindow = QtWidgets.QMainWindow()                   # 创建一个窗口对象
    window = MyWindow()                                    # 创建一个窗口对象
    window.setup_ui(MainWindow)                            # 设置窗口的属性
    MainWindow.show()                                      # 显示窗口
    sys.exit(app.exec_())                                  # 进入程序主循环，事件处理器，等待用户交互，直到用户关闭窗口或程序终止
