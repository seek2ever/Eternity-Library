import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication

from books import ScanBookFiles
from database import DatabaseManager


class MyWindow(QMainWindow):
    def __init__(self):                         # 初始化窗口
        super().__init__()                      # 调用父类的初始化方法
        self.menubar = None
        self.statusbar = None
        self.pushButton = None
        self.scanButton = None
        self.listWidget = None
        self.setup_ui()                         # 设置窗口的属性
        self.get_book_info()

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
        self.statusbar.showMessage("欢迎使用三木书斋")

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

        # 添加列表框
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(10, 60, 1900, 900))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget.setWordWrap(True)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)     # 设置列表框的选中模式
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)       # 设置列表框的选中行为
        self.listWidget.itemClicked.connect(self.get_book_info)     # TODO：列表框无法正确显示，待修复

        self.listWidget.setVisible(True)
        self.listWidget.raise_()            # 确保listWidget显示在最前面
        print(f"listWidget 几何位置: {self.listWidget.geometry()}")  # 调试信息
        print(f"listWidget 是否可见: {self.listWidget.isVisible()}")  # 调试信息

        # 确认 listWidget 的父窗口是否正确
        print(f"listWidget 的父窗口: {self.listWidget.parent()}")  # 调试信息

    def _translate(self, context, text):
        """
        翻译标题栏文本
        :param context:
        :param text:
        """
        return QCoreApplication.translate(context, text)

    def scan_books(self):
        """扫描文件按钮点击事件，调用ScanBookFiles类的select_directory方法"""
        scan_dialog = ScanBookFiles()                      # 创建ScanBookFiles类的实例
        selected_files = scan_dialog.select_directory()    # 调用select_directory方法

    def get_book_info(self, item=None):
        """获取书籍信息并显示在列表框中"""
        book_db = DatabaseManager()
        books = book_db.get_all_books()
        if not books:
            print("没有找到书籍信息")
            return

        self.listWidget.clear()
        for book in books:
            print(f"processing books:{book}")
            if isinstance(book, tuple):
                book_str = ', '.join([str(value) for value in book])
                self.listWidget.addItem(book_str)
                print(f"添加到 listWidget 的书籍信息: {book_str}")  # 调试信息
            else:
                print(f"书籍信息格式错误: {book}")

        print(f"listWidget 项数: {self.listWidget.count()}")  # 调试信息

        # 检查 listWidget 的内容
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            print(f"listWidget 项 {i}: {item.text()}")


if __name__ == '__main__':
    app = QApplication(sys.argv)                           # sys.argv用于获取当前正在执行的命令行参数的参数列表
    window = MyWindow()                                    # 创建PyQt设计的窗口对象
    window.setup_ui()                                      # 设置窗口的属性
    window.show()                                          # 显示窗口
    sys.exit(app.exec_())                                  # 进入程序主循环，事件处理器，等待用户交互，直到用户关闭窗口或程序终止
