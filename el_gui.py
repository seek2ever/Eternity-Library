import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QMessageBox

from books import ScanBookFiles
from database import DatabaseManager


class MainWindow(QMainWindow):
    bookWidget: QtWidgets.QListWidget       # 添加类型注释，防止Pylance报错

    def __init__(self):
        super().__init__()
        self.clearButton = None
        self.showButton = None
        self.menubar = None
        self.statusbar = None
        self.closeButton = None
        self.scanButton = None
        self.setup_ui()
        self.db = DatabaseManager()
        self.db.duplicate_book.connect(self.handle_duplicate_book)
        self.db.add_book_result.connect(self.show_add_result)

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

        # 按钮之间的水平布局
        h_layout = QHBoxLayout()
        # 按钮和显示列表的垂直布局
        v_layout = QVBoxLayout()

        # 添加“关闭”按钮
        self.closeButton = QtWidgets.QPushButton(self)
        self.closeButton.setObjectName("pushButton")
        self.closeButton.setText(self._translate("Close", "关闭"))
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setFixedSize(80, 50)
        # 将按钮添加到布局
        h_layout.addWidget(self.closeButton)

        # 添加“显示书籍信息”按钮
        self.showButton = QtWidgets.QPushButton(self)
        self.showButton.setText(self._translate("Show books information.", "显示书籍信息"))
        self.showButton.setFixedSize(200, 50)
        self.showButton.clicked.connect(self.get_book_info)
        h_layout.addWidget(self.showButton)

        # 添加“取消显示”按钮
        self.clearButton = QtWidgets.QPushButton(self)
        self.clearButton.setText(self._translate("Not show", "取消显示"))
        self.clearButton.setFixedSize(140, 50)
        self.clearButton.clicked.connect(self.close_info)
        h_layout.addWidget(self.clearButton)

        # 添加“扫描文件”按钮
        self.scanButton = QtWidgets.QPushButton(self)
        self.scanButton.setObjectName("scanButton")
        self.scanButton.setText(self._translate("Scan Files", "扫描文件"))
        self.scanButton.clicked.connect(self.scan_books)
        self.scanButton.setFixedSize(140, 50)
        # 将按钮添加到布局
        h_layout.addWidget(self.scanButton)

        # 添加“书籍列表”显示框
        self.bookWidget = QtWidgets.QListWidget(self)
        self.bookWidget.setObjectName("listWidget")
        self.bookWidget.setViewMode(QtWidgets.QListView.ListMode)
        self.bookWidget.setWordWrap(True)
        self.bookWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.bookWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.bookWidget.itemClicked.connect(self.get_book_info)
        # 将布局添加到窗口
        v_layout.addLayout(h_layout)              # 如果在“书籍列表”添加布局后再将列表控件添加到布局中，则按钮会显示在显示框下方
        v_layout.addWidget(self.bookWidget)

        # 将布局添加到窗口
        main_layout = QtWidgets.QWidget()         # container作为局部变量，仅在当前方法中使用，因此不需要添加self变成实例属性
        main_layout.setLayout(v_layout)
        self.setCentralWidget(main_layout)

        # 设置按钮字号
        self.setStyleSheet("""
        QPushButton {
        font-size: 16pt;
        font-family: Microsoft YaHei;
        }
        """)

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
            QMessageBox.information(self, "提示", "书籍索引信息为空。")
        # 如果找到相关书籍信息，则展示在列表控件中
        else:
            self.bookWidget.clear()
            for book in books:
                if isinstance(book, tuple):
                    book_str = ', '.join([str(value) for value in book])
                    self.bookWidget.addItem(book_str)
                else:
                    QMessageBox.warning(self, "警告", f"书籍{book}的信息错误！")

        for i in range(self.bookWidget.count()):
            item = self.bookWidget.item(i)

    def handle_duplicate_book(self, book_name):
        """
        处理重复的书籍信息
        :param book_name:
        :return:
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"检测到重复书籍：{book_name}")
        msg.setStandbutton(
            QMessageBox.Yes |
            QMessageBox.No |
            QMessageBox.Ignore
        )
        msg.setButtonText(QMessageBox.Yes, "覆盖")
        msg.setBUttonText(QMessageBox.No, "重命名")
        msg.setBUttonText(QMessageBox.Ignore, "跳过")

        choice = msg.exec()
        if choice == QMessageBox.Yes:
            self.db.handle_duplicate_book("overwrite", book_name)
        elif choice == QMessageBox.No:
            self.db.handle_duplicate_book("rename", book_name)
        elif choice == QMessageBox.Ignore:
            self.db.handle_duplicate_book("skip", book_name)

    def close_info(self) -> None:
        """清除主界面的书籍信息"""
        self.bookWidget.clear()

    def show_add_result(self, success, message):
        """显示添加结果"""
        QMessageBox.information(self, "操作结果", message)


class Tips:
    def __init__(self, parent=None):
        self.parent = parent

    def question_msg(self, qmsg) -> None:
        """显示需要用户抉择的疑问性信息"""
        QMessageBox.question(
            self.parent, 
            "提示", 
            qmsg, 
            QMessageBox.Yes | QMessageBox.No
            )

    def information_msg(self, imsg) -> None:
        """显示一般性的通知信息"""
        QMessageBox.information(
            None, 
            "提示", 
            imsg, 
            QMessageBox.Ok
            )

    def warning_msg(self, wmsg) -> None:
        """显示警告信息"""
        # TODO 显示警告信息

    def critical_msg(self, cmsg) -> None:
        """显示严重错误信息"""
    # TODO 显示严重错误信息


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
