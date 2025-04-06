import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout

from books import ScanBookFiles
from database import DatabaseManager


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.menubar = None
        self.statusbar = None
        self.pushButton = None
        self.scanButton = None
        self.listWidget = None
        self.setup_ui()
        self.get_book_info()

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))
        self.setGeometry(200, 200, 1920, 1080)
        self.setWindowOpacity(1)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/book_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("欢迎使用三木书斋")

        layout = QVBoxLayout()

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText(self._translate("Close", "关闭"))
        self.pushButton.clicked.connect(self.close)
        self.pushButton.setFixedSize(60, 30)
        layout.addWidget(self.pushButton)
        self.scanButton = QtWidgets.QPushButton(self)
        self.scanButton.setObjectName("scanButton")
        self.scanButton.setText(self._translate("Scan Files", "扫描文件"))
        self.scanButton.clicked.connect(self.scan_books)
        self.scanButton.setFixedSize(80, 30)
        layout.addWidget(self.scanButton)
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget.setWordWrap(True)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.listWidget.itemClicked.connect(self.get_book_info)
        layout.addWidget(self.listWidget)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _translate(self, context, text):
        return QCoreApplication.translate(context, text)

    def scan_books(self):
        scan_dialog = ScanBookFiles()
        selected_files = scan_dialog.select_directory()

    def get_book_info(self, item=None):
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
                print(f"添加到 listWidget 的书籍信息: {book_str}")
            else:
                print(f"书籍信息格式错误: {book}")

        print(f"listWidget 项数: {self.listWidget.count()}")

        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            print(f"listWidget 项 {i}: {item.text()}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
