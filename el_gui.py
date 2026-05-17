import sys
from typing import Optional

from PySide6.QtCore import (
    QCoreApplication,
    Qt,
    QThread,
    Signal,
)
from PySide6 import (
    QtGui,
)

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from utils import Tips
from books import ScanBookFiles
from database import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 先初始化数据库和信号连接
        self.db = DatabaseManager()
        self.db.duplicate_book.connect(self.handle_duplicate_book)
        self.db.add_book_result.connect(self.show_add_result)

        # 声明所有将在子方法中创建的实例属性
        self.left_panel: Optional[QWidget] = None
        self.list_view: Optional[QWidget] = None
        self.cover_view: Optional[QScrollArea] = None
        self.right_stack: Optional[QStackedWidget] = None
        
        # 左侧面板组件
        self.toggle_view_btn: Optional[QPushButton] = None
        self.category_list: Optional[QListWidget] = None
        self.scan_button: Optional[QPushButton] = None
        self.show_button: Optional[QPushButton] = None
        self.clear_button: Optional[QPushButton] = None
        self.close_button: Optional[QPushButton] = None
        
        # 右侧视图组件
        self.book_list: Optional[QTableWidget] = None
        self.cover_grid: Optional[QVBoxLayout] = None
        self.cover_grid_area: Optional[QWidget] = None
        self.cover_grid_layout: Optional[QVBoxLayout] = None
        
        # 窗口组件
        self.menubar: Optional[QMenuBar] = None
        self.splitter: Optional[QSplitter] = None
        self.statusbar: Optional[QStatusBar] = None

        self.setup_ui()

    def setup_ui(self):
        # 设置窗口属性
        self.setObjectName("main_window")
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))
        self.setGeometry(120, 140, 1200, 600)
        self.setWindowOpacity(1)

        # 设置窗口图标
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("images/icons/book_icon.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.setWindowIcon(icon)

        # 添加菜单栏
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # 创建QSplitter作为左右分区的容器
        self.splitter = QSplitter(Qt.Horizontal)
        self.left_panel = self._create_left_panel()

        # 创建右侧视图容器
        self.right_stack = QStackedWidget()
        self.cover_view = self._create_cover_view()     # 封面视图
        self.list_view = self._create_list_view()       # 列表视图
        self.right_stack.addWidget(self.cover_view)
        self.right_stack.addWidget(self.list_view)
        self.right_stack.setCurrentIndex(1)             # 设置默认视图（当前默认为封面视图），索引顺序与添加的顺序一致

        # 将左右组件加入QSplitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_stack)
        self.splitter.setStretchFactor(0, 1)  # 左侧比例
        self.splitter.setStretchFactor(1, 3)  # 右侧比例（更大）

        self.setCentralWidget(self.splitter)

        # 添加状态栏
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("欢迎使用三木书斋")

        # 设置按钮字号
        self.setStyleSheet("""
        QPushButton {font-size: 11pt; font-family: Microsoft YaHei;}
        QListWidget {font-size: 11pt; font-family: Microsoft YaHei;}
        """)
        # 启动时显示书籍信息
        self.show_book_info()       # 列表模式
        self.refresh_cover_view()

    def _create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        panel.setFixedWidth(220)        # 设置左侧固定宽度
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # 视图切换区
        view_label = QLabel(self._translate("Views", "视图模式"))
        view_label.setAlignment(Qt.AlignCenter)
        view_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        self.toggle_view_btn = QPushButton("切换到列表视图")
        self.toggle_view_btn.setFixedHeight(36)
        self.toggle_view_btn.clicked.connect(self._toggle_view_mode)

        layout.addWidget(view_label)
        layout.addWidget(self.toggle_view_btn)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Raised)
        layout.addWidget(line)

        # 分类筛选区，后续计划改进为标签（类型名称）+拉下列表框的方式筛选
        filter_label = QLabel(self._translate("Filter", "分类筛选"))
        filter_label.setAlignment(Qt.AlignCenter)
        filter_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        self.category_list = QListWidget()
        self.category_list.addItems([
            "全部书籍",
            "按书籍类型",
            "按阅读状态",
            "按作者",
        ])
        self.category_list.setFixedHeight(140)
        self.category_list.currentRowChanged.connect(self._on_category_changed)

        layout.addWidget(filter_label)
        layout.addWidget(self.category_list)

        # 分隔线
        line_2 = QFrame()
        line_2.setFrameShape(QFrame.HLine)
        line_2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line_2)

        # 快捷操作区
        action_label = QLabel(self._translate("Actions", "快捷操作"))
        action_label.setAlignment(Qt.AlignCenter)
        action_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

        self.scan_button = QPushButton(self._translate("Scan Files", "扫描文件"))
        self.scan_button.setFixedHeight(36)
        self.scan_button.clicked.connect(self.scan_books)

        self.show_button = QPushButton(self._translate("Show books information.", "显示书籍信息"))
        self.show_button.setFixedHeight(36)
        self.show_button.clicked.connect(self.show_book_info)

        self.clear_button = QPushButton(self._translate("Not show", "取消显示"))
        self.clear_button.setFixedHeight(36)
        self.clear_button.clicked.connect(self.close_info)

        self.close_button = QPushButton(self._translate("Close", "关闭"))
        self.close_button.setFixedHeight(36)
        self.close_button.clicked.connect(self.close)

        layout.addWidget(action_label)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.show_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.close_button)
        # 弹簧：将内容推到顶部
        layout.addStretch()
        return panel

    def _create_cover_view(self):
        """创建封面视图模式"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 容器 widget
        container = QWidget()
        self.cover_grid = QVBoxLayout(container)
        self.cover_grid.setContentsMargins(16, 16, 16, 16)

        # 顶部工具栏
        toolbar = QHBoxLayout()
        mode_label = QLabel(self._translate("Views", "封面模式"))
        mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
        toolbar.addWidget(mode_label)
        self.cover_grid.addLayout(toolbar)
        toolbar.addStretch()

        # 封面网格容器
        self.cover_grid_area = QWidget()
        self.cover_grid_layout = QVBoxLayout(self.cover_grid_area)
        self.cover_grid_layout.setSpacing(12)
        self.cover_grid.addWidget(self.cover_grid_area)

        self.cover_grid.addStretch()
        scroll.setWidget(container)
        return scroll

    def _create_book_card(self, book_name, author, book_type):
        """创建单本书籍卡片"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setFixedSize(180, 260)
        card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QFrame.hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        # 封面占位图标（后续可用书籍封面缩略图替换）
        cover_label = QLabel()
        cover_label.setFixedSize(140, 180)
        cover_label.setAlignment(Qt.AlignCenter)
        cover_label.setStyleSheet("""
            background-color: #ced4da;
            border-radius: 4px;
            font-size: 48px;
        """)
        cover_label.setText("封面")
        cover_label.setObjectName("cover_" + book_name)

        # 书名标签
        name_label = QLabel(book_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(50)
        name_label.setStyleSheet("""
            font-size: 10pt;
            font-weight: bold;
        """)

        # 副信息
        info_label = QLabel(author if author else book_type)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 9pt; color: #6c757d;")

        layout.addWidget(cover_label)
        layout.addWidget(name_label)
        layout.addWidget(info_label)

        # 点击卡片打开书籍
        # card.mousePressEvent = lambda event, bn=book_name: self._on_book(bn)
        return card

    def _on_book(self, book_name: str) -> None:
        """点击书籍卡片，打开书籍信息（暂为占位）"""
        # QMessageBox.information(None,"提示",f"打开书籍：{book_name}")
        pass

    def _clear_layout(self, layout) -> None:
        """递归清空布局中的所有子项"""
        # 获取布局中的子项数（即只要存在控件或子布局，就一直执行）
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self._clear_layout(sub_layout)

    def _create_list_view(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)

        toolbar = QHBoxLayout()
        mode_label = QLabel(self._translate("Views", "列表模式"))
        mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
        toolbar.addWidget(mode_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 添加"书籍列表"表格
        self.book_list = QTableWidget()
        self.book_list.setObjectName("book_list")
        # 获取数据库中各列的标题信息，用于创建列
        books_data: list = self.db.get_all_books()
        if books_data:
            self.book_list.setRowCount(len(books_data))
            self.book_list.setColumnCount(len(books_data[0]))
        else:
            self.book_list.setRowCount(0)
            self.book_list.setColumnCount(0)
        self.book_list.setHorizontalHeaderLabels(self.db.transfer_title_type())  # 设置列标题
        self.book_list.clicked.connect(self.show_book_info)

        layout.addWidget(self.book_list)
        return container

    def _toggle_view_mode(self) -> None:
        """在封面模式和列表模式之间切换"""
        current = self.right_stack.currentIndex()
        if current == 0:
            # 当前是封面模式，切换到列表模式
            self.right_stack.setCurrentIndex(1)
            self.toggle_view_btn.setText(self._translate("Views", "切换到封面视图"))
            self.statusbar.showMessage(self._translate("Views", "已切换到列表视图"))
        else:
            # 当前是列表模式，切换到封面模式
            self.right_stack.setCurrentIndex(0)
            self.toggle_view_btn.setText(self._translate("Views", "切换到列表视图"))
            self.refresh_cover_view()  # 切换到封面时刷新
            self.statusbar.showMessage(self._translate("Views", "已切换到封面视图"))

    def _on_category_changed(self, row: int) -> None:
        """左侧分类选择变化时触发"""
        # TODO：目前此方法不方便同时进行多项筛选，后续需优化
        categories = ["全部", "按书籍类型", "按阅读状态", "按作者"]
        if row < 0 or row >= len(categories):
            return
        category = categories[row]
        self.statusbar.showMessage(self._translate("Views", f"已选择分类：{category}"))
        if category == "全部":
            books = self.db.get_all_books()
        elif category == "按书籍类型":
            books = self.db.get_books_by_type()
        elif category == "按阅读状态":
            books = self.db.get_books_by_status()
        elif category == "按作者":
            books = self.db.get_books_by_author()

        # 刷新封面和列表视图
        self.refresh_cover_view()

    def refresh_cover_view(self) -> None:
        """从数据库读取数据，刷新封面网格"""
        books = self.db.get_all_books()
        if not books:
            return

        # 清除旧卡片
        self._clear_layout(self.cover_grid_layout)
        # 每行显示4本书（可根据窗口宽度动态调整）
        cols = 4
        row_layout = None
        for i, book in enumerate(books):
            # 索引：1=book_name, 4=author, 11=book_type
            # TODO: 此处获取书籍信息的方法依赖于数据库中书籍信息的存在与否，需要对database.py中的delete_book()方法进行修改
            book_name = book[1] or "未知"
            author = book[3] or "未知"
            book_type = book[11] or "未知"

            # 每cols本新建一行
            if i % cols == 0:
                row_layout = QHBoxLayout()
                row_layout.setSpacing(16)
                self.cover_grid_layout.addLayout(row_layout)

            # 创建书籍卡片
            card = self._create_book_card(book_name, author, book_type)
            row_layout.addWidget(card)

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
            book_db: list = self.db.get_all_books()
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
                        item = QTableWidgetItem(str(book_data))
                        self.book_list.setItem(row, col, item)
                # 调整内容显示
                self.book_list.resizeRowsToContents()  # 调整行高
                self.book_list.resizeColumnsToContents()  # 调整列宽
                self.book_list.setAlternatingRowColors(True)  # 隔行交替颜色
        except Exception as e:
            Tips.information_msg(f"获取书籍信息时发生错误：{e}")

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
