import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QMessageBox

from books import ScanBookFiles
from database import DatabaseManager


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showButton = None
        self.menubar = None
        self.statusbar = None
        self.pushButton = None
        self.scanButton = None
        self.listWidget = None
        self.setup_ui()

    def setup_ui(self):
        # 设置窗口属性
        self.setObjectName("MainWindow")
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))
        self.setGeometry(200, 200, 1920, 1080)
        self.setWindowOpacity(1)

        # 设置窗口图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/book_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # 添加菜单栏
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # 添加状态栏
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("欢迎使用三木书斋")

        # 创建布局
        layout = QVBoxLayout()

        # 添加“关闭”按钮
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText(self._translate("Close", "关闭"))
        self.pushButton.clicked.connect(self.close)
        self.pushButton.setFixedSize(60, 30)
        # 将按钮添加到布局
        layout.addWidget(self.pushButton)

        self.showButton = QtWidgets.QPushButton(self)
        self.showButton.setText(self._translate("Show books information.", "显示书籍信息"))
        self.showButton.setFixedSize(120, 30)
        self.showButton.clicked.connect(self.get_book_info)
        layout.addWidget(self.showButton)

        # 添加“扫描文件”按钮
        self.scanButton = QtWidgets.QPushButton(self)
        self.scanButton.setObjectName("scanButton")
        self.scanButton.setText(self._translate("Scan Files", "扫描文件"))
        self.scanButton.clicked.connect(self.scan_books)
        self.scanButton.setFixedSize(80, 30)
        # 将按钮添加到布局
        layout.addWidget(self.scanButton)

        # 添加“书籍列表”显示框
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget.setWordWrap(True)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.listWidget.itemClicked.connect(self.get_book_info)
        # 将布局添加到窗口
        layout.addWidget(self.listWidget)

        # 将布局添加到窗口
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _translate(self, context, text):
        return QCoreApplication.translate(context, text)

    def scan_books(self):
        """
        调用books模块中的ScanBookFiles类扫描书籍
        :return:
        """
        scan_dialog = ScanBookFiles()
        selected_files = scan_dialog.select_directory()

    def get_book_info(self, item=None):
        """
        获取书籍信息并展示在列表控件（QListWidget）
        :return:
        """
        book_db = DatabaseManager()
        books = book_db.get_all_books()
        # 如果没有找到相关书籍信息，则弹出提示框
        if not books:
            QMessageBox.information(self, "提示", "未找到相关书籍信息，请重试。")
        # 如果找到相关书籍信息，则展示在列表控件中
        else:
            self.listWidget.clear()
            for book in books:
                if isinstance(book, tuple):
                    book_str = ', '.join([str(value) for value in book])
                    self.listWidget.addItem(book_str)
                else:
                    QMessageBox.warning(self, "警告", f"书籍{book}的信息错误！")

        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
