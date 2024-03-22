import sys
from books import ScanBookFiles
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication


class MyWindow(QMainWindow):
    def __init__(self):                         # 初始化窗口
        super().__init__()                      # 调用父类的初始化方法
        self.scanButton = None
        self.pushButton = None
        self.statusbar = None
        self.menubar = None
        self.setup_ui()                         # 设置窗口的属性

    def setup_ui(self):
        # 创建主窗口
        self.setObjectName("MainWindow")                                # 设置窗口的对象名称
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))        # 设置窗口的标题名称
        self.setGeometry(200, 200, 1920, 1080)                          # 设置窗口的位置和大小
        self.setWindowOpacity(1)                                        # 设置窗口的透明度

        # 设置图标
        icon = QtGui.QIcon()                                            # 创建一个图标对象
        icon.addPixmap(QtGui.QPixmap("images/book_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)                                        # 设置窗口的图标

        # 创建菜单栏
        self.menubar = QtWidgets.QMenuBar(self)                         # 创建一个菜单栏，分配实际的QtWidgets.QMenuBar对象
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))           # 设置菜单栏的位置和大小
        self.menubar.setObjectName("menubar")                           # 设置菜单栏的对象名称
        self.setMenuBar(self.menubar)                                   # 设置窗口的菜单栏

        # 创建状态栏
        self.statusbar = QtWidgets.QStatusBar(self)                     # 创建一个状态栏，分配实际的QtWidgets.QStatusBar对象
        self.statusbar.setObjectName("statusbar")                       # 设置状态栏的对象名称
        self.setStatusBar(self.statusbar)                               # 设置窗口的状态栏

        # 添加关闭按钮
        self.pushButton = QtWidgets.QPushButton(self)                   # 创建一个按钮，分配实际的QtWidgets.QPushButton对象
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 100, 40))      # 设置按钮的位置和大小
        self.pushButton.setObjectName("pushButton")                     # 设置按钮的对象名称
        self.pushButton.setText(self._translate("Close", "关闭"))    # 设置按钮的文本
        self.pushButton.clicked.connect(self.close)                     # 设置按钮的点击事件

        # 添加扫描文件按钮
        self.scanButton = QtWidgets.QPushButton(self)
        self.scanButton.setGeometry(QtCore.QRect(120, 10, 150, 40))
        self.scanButton.setObjectName("scanButton")
        self.scanButton.setText(self._translate("Scan Files", "扫描文件"))
        self.scanButton.clicked.connect(self.scan_books)                # 设置按钮的点击事件

    def _translate(self, context, text):
        """翻译标题栏文本"""
        return QCoreApplication.translate(context, text)

    def scan_books(self):
        """扫描文件按钮点击事件，调用ScanBookFiles类的select_directory方法"""
        scan_dialog = ScanBookFiles()                      # 创建ScanBookFiles类的实例
        scan_dialog.select_directory()                     # 调用select_directory方法


if __name__ == '__main__':
    app = QApplication(sys.argv)                           # sys.argv用于获取当前正在执行的命令行参数的参数列表
    window = MyWindow()                                    # 创建PyQt设计的窗口对象
    window.setup_ui()                                      # 设置窗口的属性
    window.show()                                          # 显示窗口
    sys.exit(app.exec_())                                  # 进入程序主循环，事件处理器，等待用户交互，直到用户关闭窗口或程序终止
