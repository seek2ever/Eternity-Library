import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QMessageBox

from utils import Tips
from books import ScanBookFiles
from database import DatabaseManager


class MainWindow(QMainWindow):
    bookWidget: QtWidgets.QListWidget       # 添加类型注释，防止Pylance报错

    def __init__(self):
        super().__init__()
        self.book_list = None
        self.clearButton = None
        self.showButton = None
        self.menubar = None
        self.statusbar = None
        self.closeButton = None
        self.scanButton = None
        self.db = DatabaseManager()
        self.db.duplicate_book.connect(self.handle_duplicate_book)
        self.db.add_book_result.connect(self.show_add_result)
        self.setup_ui()

    def setup_ui(self):
        # 设置窗口属性
        self.setObjectName("main_window")
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))
        self.setGeometry(150, 150, 2350, 1250)
        self.setWindowOpacity(1)

        # 设置窗口图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/book_icon.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        # self.showButton.clicked.connect(self.get_book_info)
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

        # 添加“书籍列表”表格
        self.book_list = QtWidgets.QTableWidget()
        self.book_list.setObjectName("book_list")
        # 获取数据库中各列的标题信息，用于创建列
        books_data = self.db.get_all_books()
        if books_data and len(books_data) > 0:
            self.book_list.setRowCount(len(books_data))
            self.book_list.setColumnCount(len(books_data[0]))
        else:
            self.book_list.setRowCount(0)
            self.book_list.setColumnCount(0)
        # header_labels = self.db.transfer_title_type()
        self.book_list.setHorizontalHeaderLabels(self.db.transfer_title_type())  # 设置列标题
        self.book_list.clicked.connect(self.show_book_info)

        # 将布局添加到窗口
        v_layout.addLayout(h_layout)
        # 如果在“书籍列表”添加布局后再将列表控件添加到布局中，则按钮会显示在显示框下方
        v_layout.addWidget(self.book_list)

        # 将布局添加到窗口
        main_layout = QtWidgets.QWidget()
        main_layout.setLayout(v_layout)
        self.setCentralWidget(main_layout)

        # 设置按钮字号
        self.setStyleSheet("""
        QPushButton {
        font-size: 11pt;
        font-family: Microsoft YaHei;
        }
        """)

    def scan_books(self):
        """
        调用books模块中的ScanBookFiles类扫描书籍
        :return:
        """
        scan_dialog = ScanBookFiles()
        selected_files = scan_dialog.select_directory()

    def show_book_info(self):
        """获取书籍信息并展示"""
        try:
            book_db = self.db.get_all_books()
            # 清空列表中现有的数据
            self.book_list.clearContents()
            # 如果没有找到相关书籍信息，则弹出提示框
            if not book_db:
                Tips.information_msg("书籍索引信息为空。")
                return
            # 如果找到相关书籍信息，则展示在列表控件中
            else:
                for row, book_row in enumerate(book_db):
                    for col, book_data in enumerate(book_row):
                        item = QtWidgets.QTableWidgetItem(str(book_data))
                        self.book_list.setItem(row, col, item)
                # 调整内容显示
                self.book_list.resizeRowsToContents()               # 调整行高
                self.book_list.resizeColumnsToContents()            # 调整列宽
                self.book_list.setAlternatingRowColors(True)        # 隔行交替颜色
        except Exception as e:
            Tips.information_msg(f"获取书籍信息时发生错误：{e}")

    # def get_book_info(self, item=None):
    #     """
    #     获取书籍信息并展示在列表控件（QListWidget）
    #     :return:
    #     """
    #     book_db = DatabaseManager()
    #     books = book_db.get_all_books()
    #     # 如果没有找到相关书籍信息，则弹出提示框
    #     if not books:
    #         Tips.information_msg("书籍索引信息为空。")
    #     # 如果找到相关书籍信息，则展示在列表控件中
    #     else:
    #         self.bookWidget.clear()
    #         for book in books:
    #             if isinstance(book, tuple):
    #                 book_str = ', '.join([str(value) for value in book])
    #                 self.bookWidget.addItem(book_str)
    #             else:
    #                 QMessageBox.warning(self, "警告", f"书籍{book}的信息错误！")
    #
    #     for i in range(self.bookWidget.count()):
    #         item = self.bookWidget.item(i)

    def handle_duplicate_book(self, book_name):
        """
        处理重复的书籍信息
        :param book_name:
        :return:
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"检测到重复书籍：{book_name}")
        msg.setStandardButtons(
            QMessageBox.Yes |
            QMessageBox.No |
            QMessageBox.Ignore
        )
        msg.setButtonText(QMessageBox.Yes, "覆盖")
        msg.setButtonText(QMessageBox.No, "重命名")
        msg.setButtonText(QMessageBox.Ignore, "跳过")

        choice = msg.exec()
        if choice == QMessageBox.Yes:
            self.db.handle_duplicate_book("overwrite", book_name)
        elif choice == QMessageBox.No:
            self.db.handle_duplicate_book("rename", book_name)
        elif choice == QMessageBox.Ignore:
            self.db.handle_duplicate_book("skip", book_name)

    def close_info(self) -> None:
        """清除主界面的书籍信息"""
        # self.bookWidget.clear()
        self.book_list.clearContents()

    def show_add_result(self, success, message):
        """显示添加结果"""
        QMessageBox.information(self, "操作结果", message)

    @staticmethod
    def _translate(context, text):
        return QCoreApplication.translate(context, text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
