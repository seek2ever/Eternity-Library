import sys
import time
from typing import Optional

from PySide6 import QtGui
from PySide6.QtCore import (
    QCoreApplication,
    QSize,
    QThread,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from books import ScanBookFiles
from database import (
    BookQueryWorker,
    DatabaseManager,
)
from utils import Tips
from cover_model import CoverCardModel
from cover_delegate import CoverCardDelegate


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化数据库和信号连接
        self.db = DatabaseManager()
        self.db.duplicate_book.connect(self.handle_duplicate_book)
        self.db.add_book_result.connect(self.show_add_result)

        self._setup_book_worker()

        # 声明所有将在子方法中创建的实例属性
        self.left_panel: Optional[QWidget] = None
        self.list_view: Optional[QWidget] = None
        self.cover_view: Optional[QWidget] = None
        self.right_stack: Optional[QStackedWidget] = None

        self.cover_model = CoverCardModel()
        self.cover_delegate = CoverCardDelegate()

        # 左侧面板组件
        self.toggle_view_btn: Optional[QPushButton] = None
        self.category_list: Optional[QListWidget] = None
        self.scan_button: Optional[QPushButton] = None
        self.show_button: Optional[QPushButton] = None
        self.clear_button: Optional[QPushButton] = None
        self.close_button: Optional[QPushButton] = None

        # 右侧视图组件
        self.book_table: Optional[QTableWidget] = None
        self.cover_list_view: Optional[QListView] = None

        # 窗口组件
        self.menubar: Optional[QMenuBar] = None
        self.splitter: Optional[QSplitter] = None
        self.statusbar: Optional[QStatusBar] = None

        self.setup_ui()

    def _setup_book_worker(self):
        """初始化后台查询线程、缓存变量"""
        # 缓存最后一次查询结果
        self._books_cache = None
        self._cache_timestamp = 0  # 缓存时间戳

        # 创建后台查询线程
        self._query_thread = QThread()
        # 创建Worker（传入数据库文件名，不传连接对象）
        self._book_worker = BookQueryWorker(self.db.db_name)
        # 把 Worker 移到工作线程（此后Worker的所有槽函数在工作线程执行）
        self._book_worker.moveToThread(self._query_thread)
        # 连接信号和槽
        self._book_worker.books_ready.connect(self._on_books_loaded)
        self._book_worker.query_error.connect(self._on_query_error)
        # trigger_fetch → fetch_all_books：跨线程自动 QueuedConnection
        self._book_worker.trigger_fetch.connect(self._book_worker.fetch_all_books)
        # 启动工作线程
        self._query_thread.start()

    def setup_ui(self):
        # 设置窗口属性
        self.setObjectName("main_window")
        self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))
        self.setGeometry(120, 140, 1080, 620)
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
        self.list_view = self._create_table_view()      # 列表视图
        self.right_stack.addWidget(self.cover_view)
        self.right_stack.addWidget(self.list_view)
        # 设置默认视图（当前默认为封面视图），索引顺序与添加的顺序一致
        self.right_stack.setCurrentIndex(0)

        # 将左右组件加入QSplitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_stack)
        self.splitter.setStretchFactor(0, 1)    # 左侧比例
        self.splitter.setStretchFactor(1, 3)    # 右侧比例（更大）

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

        self.refresh_cover_view()

    def _create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        panel.setFixedWidth(220)  # 设置左侧固定宽度
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
        """创建封面视图 —— QListView + Delegate 虚拟化绘制"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)

        toolbar = QHBoxLayout()
        mode_label = QLabel(self._translate("Views", "封面模式"))
        mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
        toolbar.addWidget(mode_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.cover_list_view = QListView()
        self.cover_list_view.setModel(self.cover_model)
        self.cover_list_view.setItemDelegate(self.cover_delegate)

        self.cover_list_view.setViewMode(QListView.IconMode)
        self.cover_list_view.setMovement(QListView.Static)
        self.cover_list_view.setResizeMode(QListView.Adjust)
        self.cover_list_view.setWrapping(True)
        self.cover_list_view.setSpacing(4)
        self.cover_list_view.setGridSize(QSize(
            CoverCardDelegate.CARD_W + 16,
            CoverCardDelegate.CARD_H + 10,
        ))
        self.cover_list_view.setUniformItemSizes(True)

        self.cover_list_view.setFrameShape(QFrame.NoFrame)
        self.cover_list_view.setBackgroundRole(QtGui.QPalette.Base)
        self.cover_list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cover_list_view.setVerticalScrollMode(QListView.ScrollPerPixel)

        self.cover_list_view.clicked.connect(self._on_cover_card_clicked)

        layout.addWidget(self.cover_list_view)
        return container

    def _on_cover_card_clicked(self, index):
        """点击封面卡片"""
        book = self.cover_model.get_book(index.row())
        if book:
            self.statusbar.showMessage(f"选中：{book['name']}")

    def _create_table_view(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)

        toolbar = QHBoxLayout()
        mode_label = QLabel(self._translate("Table View", "列表模式"))
        mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
        toolbar.addWidget(mode_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 添加"书籍列表"表格
        self.book_table = QTableWidget()
        self.book_table.setObjectName("book_table")
        # 获取数据库中各列的标题信息，用于创建列
        books_data: list = self.db.get_all_books()
        if books_data:
            self.book_table.setRowCount(len(books_data))
            self.book_table.setColumnCount(len(books_data[0]))
        else:
            self.book_table.setRowCount(0)
            self.book_table.setColumnCount(0)
        self.book_table.setHorizontalHeaderLabels(self.db.transfer_title_type())  # 设置列标题
        self.book_table.clicked.connect(self.show_book_info)

        layout.addWidget(self.book_table)
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
            if self._books_cache is None or (time.time() - self._cache_timestamp) >= 30:
                self.refresh_cover_view()
            self.toggle_view_btn.setText(self._translate("Views", "切换到列表视图"))
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
        """触发后台查询，若存在有效缓存则直接使用"""
        # 缓存有效时直接渲染，不走数据库
        # 缓存有效（30秒内），直接渲染，不走数据库
        if self._books_cache is not None and (time.time() - self._cache_timestamp) < 30:
            self._on_books_loaded(self._books_cache)
            return

        # 缓存过期或不存在 → 触发后台线程查询
        self._book_worker.trigger_fetch.emit()

    def _on_books_loaded(self, books: list):
        """收到后台查询结果（在主线程执行），直接喂给 Model，View 自动刷新"""
        if not books:
            return
        self._books_cache = books
        self._cache_timestamp = time.time()
        self.cover_model.set_books(books)
        self.statusbar.showMessage(
            self._translate("Views", f"封面视图已刷新，共 {len(books)} 本书")
        )

    def _on_query_error(self, error_msg: str):
        """查询出错时的处理"""
        Tips.information_msg(f"数据库查询失败：{error_msg}")

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
            self.book_table.clearContents()
            # 如果没有找到相关书籍信息，则弹出提示框
            if not book_db:
                Tips.information_msg("书籍索引信息为空。")
                return
            # 如果找到相关书籍信息，则展示在列表控件中
            else:
                for row, book_row in enumerate(book_db):
                    for col, book_data in enumerate(book_row):
                        item = QTableWidgetItem(str(book_data))
                        self.book_table.setItem(row, col, item)

                self.book_table.resizeRowsToContents()          # 调整行高
                self.book_table.resizeColumnsToContents()       # 调整列宽
                self.book_table.setAlternatingRowColors(True)   # 隔行交替颜色
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
        self.book_table.clearContents()

    def show_add_result(self, success, message):
        """显示添加结果"""
        if success:
            Tips.information_msg(message)
            self.show_book_info()
            self.refresh_cover_view()
            self.statusbar.showMessage(self._translate(
                "success",
                "已成功添加书籍"),
                3000)
        else:
            Tips.information_msg(message)

    def closeEvent(self, event):
        """窗口关闭时安全退出后台线程"""
        self._query_thread.quit()  # 退出线程的事件循环
        self._query_thread.wait(3000)  # 等待线程结束（最多 3 秒）
        self.db.close()  # 关闭数据库连接
        event.accept()

    @staticmethod
    def _translate(context, text):
        return QCoreApplication.translate(context, text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
