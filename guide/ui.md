# UI 改进方案：封面浏览模式 + 左侧面板布局

## 概述

目前的界面是"单按钮栏 + 完整数据表"的原始布局。改进目标是：

- **左侧面板**：放置分类筛选、视图切换、快捷操作
- **右侧主区域**：书籍展示区，支持"封面模式"和"列表模式"切换
- **保留现有功能**：扫描、添加、删除等业务逻辑不动

---

## 一、整体布局结构

```
+----------------------------------------------------------+
|  菜单栏 (MenuBar)                                          |
+----------+-----------------------------------------------+
| 左侧面板  |  右侧主区域                                    |
| (QWidget) |                                               |
|           |   +---------------------------------------+   |
|  [视图切换] |   |  模式切换工具栏                         |   |
|  封面/列表  |   |  [封面视图] 或 [列表视图]               |   |
|           |   |                                       |   |
|  [分类筛选] |   |                                       |   |
|  全部书籍   |   |  书籍卡片网格 / 表格                     |   |
|  按类型     |   |                                       |   |
|  按阅读状态  |   |                                       |   |
|           |   |                                       |   |
|  [快捷操作]  |   |                                       |   |
|  扫描...    |   |                                       |   |
|           |   +---------------------------------------+   |
+----------+-----------------------------------------------+
|  状态栏 (StatusBar)                                       |
+----------------------------------------------------------+
```

### 使用的 Qt 布局组件

- `QSplitter` — 分隔左侧面板和右侧区域，用户可拖动调整宽度
- `QListWidget` 或 `QTreeWidget` — 左侧分类列表
- `QStackedWidget` — 右侧模式切换容器（封面模式 / 列表模式）
- `QScrollArea` — 包裹封面网格，支持滚动
- `QTableWidget` — 列表模式（复用现有 `self.book_list`）

> **为什么要用 QSplitter 而不是固定布局？**
> QSplitter 让用户可以自由拖动左右面板的分隔线，适应不同屏幕宽度。
> 不像固定比例布局，QSplitter 是 Qt 专门为"可调整左右/上下分区"设计的控件。

---

## 二、分步实现步骤

### 第 1 步：引入新控件

在 `el_gui.py` 顶部或 `setup_ui` 方法中引入以下类：

```python
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMessageBox, QPushButton, QStatusBar,
    QTableWidget,              # 已有
    QSplitter,                 # 新增：左右分隔
    QWidget,                   # 已有
    QListWidget,               # 新增：左侧分类列表
    QStackedWidget,            # 新增：右侧视图切换容器
    QScrollArea,               # 新增：封面视图的滚动区域
    QLabel,                    # 新增：封面卡片
    QToolButton,               # 新增：切换按钮（图标+文字）
    QFrame,                    # 新增：卡片边框
)
```

### 第 2 步：改造 setup_ui 方法

将 `setup_ui` 中的布局逻辑改为如下结构：

```python
def setup_ui(self):
    self.setObjectName("main_window")
    self.setWindowTitle(self._translate("Eternity Library", "三木书斋"))
    self.setGeometry(150, 150, 1400, 900)

    # 窗口图标（不动）
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("images/icons/book_icon.png"),
                   QtGui.QIcon.Normal, QtGui.QIcon.Off)
    self.setWindowIcon(icon)

    # 菜单栏（不动）
    self.menubar = QMenuBar(self)
    self.menubar.setObjectName("menubar")
    self.setMenuBar(self.menubar)

    # ===== 核心布局改造从这里开始 =====

    # 1. 创建 QSplitter 作为左右分区的容器
    self.splitter = QSplitter(Qt.Horizontal)

    # 2. 创建左侧面板
    self.left_panel = self._create_left_panel()

    # 3. 创建右侧视图容器（QStackedWidget）
    self.right_stack = QStackedWidget()
    self.cover_view = self._create_cover_view()  # 封面模式
    self.list_view = self._create_table_view()  # 列表模式（复用现有表格）
    self.right_stack.addWidget(self.cover_view)  # index 0
    self.right_stack.addWidget(self.list_view)  # index 1
    self.right_stack.setCurrentIndex(0)  # 默认显示封面模式

    # 4. 将左右组件加入 QSplitter
    self.splitter.addWidget(self.left_panel)
    self.splitter.addWidget(self.right_stack)
    self.splitter.setStretchFactor(0, 1)  # 左侧比例
    self.splitter.setStretchFactor(1, 3)  # 右侧比例（更大）

    # 5. 将 splitter 设置为中心组件
    self.setCentralWidget(self.splitter)

    # 状态栏（不动）
    self.statusbar = QStatusBar(self)
    self.statusbar.setObjectName("statusbar")
    self.setStatusBar(self.statusbar)
    self.statusbar.showMessage("欢迎使用三木书斋")

    # 样式（后续可单独抽到 QSS 文件）
    self.setStyleSheet("""
    QPushButton { font-size: 11pt; font-family: Microsoft YaHei; }
    QListWidget { font-size: 11pt; font-family: Microsoft YaHei; }
    """)
```

> `QSplitter(Qt.Horizontal)` 中的 `Qt.Horizontal` 表示水平分割。
> `setStretchFactor(索引, 比例)` 用于控制分割后各部分的初始大小比例。

### 第 3 步：创建左侧面板

左侧面板包含：视图切换按钮、分类筛选列表、快捷操作按钮。

```python
def _create_left_panel(self):
    """创建左侧面板"""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(12)

    # --- 视图切换区 ---
    view_label = QLabel("视图模式")
    view_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

    self.toggle_view_btn = QPushButton("切换到列表视图")
    self.toggle_view_btn.setFixedHeight(36)
    self.toggle_view_btn.clicked.connect(self._toggle_view_mode)

    layout.addWidget(view_label)
    layout.addWidget(self.toggle_view_btn)

    # --- 分隔线 ---
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)

    # --- 分类筛选区 ---
    filter_label = QLabel("分类筛选")
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

    # --- 分隔线 ---
    line2 = QFrame()
    line2.setFrameShape(QFrame.HLine)
    line2.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line2)

    # --- 快捷操作区 ---
    action_label = QLabel("快捷操作")
    action_label.setStyleSheet("font-weight: bold; font-size: 12pt;")

    self.scanButton = QPushButton("扫描文件")
    self.scanButton.setFixedHeight(36)
    self.scanButton.clicked.connect(self.scan_books)

    self.showButton = QPushButton("显示书籍信息")
    self.showButton.setFixedHeight(36)
    self.showButton.clicked.connect(self.show_book_info)

    self.clearButton = QPushButton("取消显示")
    self.clearButton.setFixedHeight(36)
    self.clearButton.clicked.connect(self.close_info)

    self.closeButton = QPushButton("关闭")
    self.closeButton.setFixedHeight(36)
    self.closeButton.clicked.connect(self.close)

    layout.addWidget(action_label)
    layout.addWidget(self.scanButton)
    layout.addWidget(self.showButton)
    layout.addWidget(self.clearButton)
    layout.addWidget(self.closeButton)

    # 弹簧：将内容推到顶部
    layout.addStretch()

    panel.setFixedWidth(220)
    return panel
```

### 第 4 步：创建封面视图

封面视图用 `QScrollArea` 包一个网格布局，每个书籍封面用单独的卡片 `QFrame` 表示。

```python
def _create_cover_view(self):
    """创建封面模式视图"""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # 容器 widget
    container = QWidget()
    self.cover_grid = QVBoxLayout(container)
    self.cover_grid.setSpacing(16)
    self.cover_grid.setContentsMargins(16, 16, 16, 16)

    # 顶部工具栏
    toolbar = QHBoxLayout()
    mode_label = QLabel("封面模式")
    mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
    toolbar.addWidget(mode_label)
    toolbar.addStretch()
    self.cover_grid.addLayout(toolbar)

    # 封面网格容器
    self.cover_grid_area = QWidget()
    self.cover_grid_layout = QVBoxLayout(self.cover_grid_area)
    self.cover_grid_layout.setSpacing(12)
    self.cover_grid.addWidget(self.cover_grid_area)

    # 弹簧
    self.cover_grid.addStretch()

    scroll.setWidget(container)
    return scroll


def refresh_cover_view(self):
    """从数据库读取数据，刷新封面网格"""
    books = self.db.get_all_books()
    if not books:
        return

    # 清除旧卡片
    self._clear_layout(self.cover_grid_layout)

    # 每行显示 4 本书（可根据窗口宽度动态调整）
    cols = 4
    row_layout = None

    for i, book in enumerate(books):
        # book 是一个元组，按数据库字段顺序排列
        # 这里假设索引：1=book_name, 3=author, 11=book_type
        book_name = book[1] if len(book) > 1 else "未知"
        author = book[4] if len(book) > 4 else ""
        book_type = book[11] if len(book) > 11 else ""

        # 每 cols 本新建一行
        if i % cols == 0:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(16)
            self.cover_grid_layout.addLayout(row_layout)

        # 创建书籍卡片
        card = self._create_book_card(book_name, author, book_type)
        row_layout.addWidget(card)


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
        QFrame:hover {
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
    cover_label.setText("📖")
    cover_label.setObjectName("cover_" + book_name)

    # 书名
    name_label = QLabel(book_name)
    name_label.setAlignment(Qt.AlignCenter)
    name_label.setWordWrap(True)
    name_label.setMaximumHeight(50)
    name_label.setStyleSheet("font-size: 10pt; font-weight: bold;")

    # 副信息
    info_label = QLabel(author if author else book_type)
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setStyleSheet("font-size: 9pt; color: #6c757d;")

    layout.addWidget(cover_label)
    layout.addWidget(name_label)
    layout.addWidget(info_label)

    # 点击卡片打开书籍
    card.mousePressEvent = lambda event, bn=book_name: self._open_book(bn)

    return card


def _open_book(self, book_name):
    """点击书籍卡片的响应（暂为占位）"""
    QMessageBox.information(self, "打开书籍", f"准备打开：{book_name}")
    # 后续：打开书籍文件或显示详情弹窗


def _clear_layout(self, layout):
    """递归清空布局中的所有子项"""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
        else:
            sub_layout = item.layout()
            if sub_layout:
                self._clear_layout(sub_layout)
```

> `QScrollArea` 是一个可滚动的视口，当你内容超出可见区域时会自动出现滚动条。
> `QFrame` 设置了 `StyledPanel` + `border-radius` 来实现卡片圆角效果。
> 鼠标事件 `mousePressEvent` 用 lambda 来传递 book_name，避免循环变量捕获问题。

### 第 5 步：创建列表视图

列表视图复用现有的表格，用 `QWidget` 包裹一下即可放入 `QStackedWidget`。

```python
def _create_list_view(self):
    """创建列表模式视图（复用现有表格）"""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(16, 16, 16, 16)

    # 顶部工具栏
    toolbar = QHBoxLayout()
    mode_label = QLabel("列表模式")
    mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
    toolbar.addWidget(mode_label)
    toolbar.addStretch()
    layout.addLayout(toolbar)

    # 复用现有的 book_table 表格
    self.book_table = QTableWidget()
    self.book_table.setObjectName("book_table")

    # 加载数据
    books_data = self.db.get_all_books()
    if books_data:
        self.book_table.setRowCount(len(books_data))
        self.book_table.setColumnCount(len(books_data[0]))
    else:
        self.book_table.setRowCount(0)
        self.book_table.setColumnCount(0)

    self.book_table.setHorizontalHeaderLabels(self.db.transfer_title_type())
    self.book_table.clicked.connect(self.show_book_info)

    layout.addWidget(self.book_table)

    return container
```

### 第 6 步：实现视图切换

```python
def _toggle_view_mode(self):
    """在封面模式和列表模式之间切换"""
    current = self.right_stack.currentIndex()
    if current == 0:  # 当前是封面，切换到列表
        self.right_stack.setCurrentIndex(1)
        self.toggle_view_btn.setText("切换到封面视图")
        self.statusbar.showMessage("已切换为列表模式")
    else:  # 当前是列表，切换到封面
        self.right_stack.setCurrentIndex(0)
        self.toggle_view_btn.setText("切换到列表视图")
        self.refresh_cover_view()  # 切换到封面时刷新
        self.statusbar.showMessage("已切换为封面模式")
```

> `QStackedWidget` 就像一个卡片容器，`setCurrentIndex(0)` 显示第 0 页（封面），
> `setCurrentIndex(1)` 显示第 1 页（列表）。切换只是隐藏/显示对应子控件，非常轻量。

### 第 7 步：分类筛选（骨架）

目前数据库已经有 `book_type`、`read_status`、`author` 字段，可以直接用来做筛选。

```python
def _on_category_changed(self, row):
    """左侧分类选择变化时触发"""
    categories = ["全部", "按书籍类型", "按阅读状态", "按作者"]
    if row < 0 or row >= len(categories):
        return
    category = categories[row]
    self.statusbar.showMessage(f"筛选：{category}")

    if category == "全部":
        books = self.db.get_all_books()
    elif category == "按书籍类型":
        books = self.db.get_books_by_type(...)   # 需要在 database.py 新增方法
    elif category == "按阅读状态":
        books = self.db.get_books_by_status(...)  # 需要在 database.py 新增方法
    elif category == "按作者":
        books = self.db.get_books_by_author(...)  # 需要在 database.py 新增方法

    # 刷新封面和列表视图
    self.refresh_cover_view()
    # 也刷新列表视图（略）
```

需要在 `database.py` 中增加的查询方法示例：

```python
def get_books_by_type(self, book_type):
    sql = "SELECT * FROM books_information WHERE book_type=?"
    self.cursor.execute(sql, (book_type,))
    return self.cursor.fetchall()

def get_books_by_status(self, status):
    sql = "SELECT * FROM books_information WHERE read_status=?"
    self.cursor.execute(sql, (status,))
    return self.cursor.fetchall()

def get_books_by_author(self, author):
    sql = "SELECT * FROM books_information WHERE author=?"
    self.cursor.execute(sql, (author,))
    return self.cursor.fetchall()
```

对于更复杂的筛选（如点击"按类型"后弹出二级选项），需要添加子分类弹窗或使用 `QComboBox`，这可以放到后续迭代中。

---

## 三、需要新增的文件

| 文件 | 用途 |
|------|------|
| 修改 `el_gui.py` | 重构布局，新增左侧面板、封面视图、视图切换 |
| 修改 `database.py` | 新增 `get_books_by_type/status/author` 等筛选方法 |
| `styles.qss`（可选） | 将样式表从 `setStyleSheet` 字符串提取为独立文件，便于统一管理 |

> QSS（Qt Style Sheets）语法和 CSS 几乎一样。用独立 `.qss` 文件的好处是
> 修改样式不需要改动 Python 代码。加载方式：
> ```python
> with open("styles.qss", "r", encoding="utf-8") as f:
>     self.setStyleSheet(f.read())
> ```

---

## 四、实施顺序建议

```
第 1 步：在 el_gui.py 引入新控件类  →  5 分钟
第 2 步：改造 setup_ui 为 splitter 结构  →  15 分钟
第 3 步：实现 _create_left_panel  →  15 分钟
第 4 步：实现 _create_cover_view（封面卡片）  →  30 分钟
第 5 步：实现 _create_list_view（包裹现有表格）  →  10 分钟
第 6 步：实现 _toggle_view_mode  →  5 分钟
第 7 步：在 database.py 新增筛选方法  →  10 分钟
```

建议每次完成一步就运行 `python el_gui.py` 测试，不要等全部写完再测。

---

## 五、后续可扩展的方向

这些是本次改进 **暂时不做** 但可以留作后续迭代的点：

1. **真实封面缩略图**：PDF 书籍可以用 PyMuPDF 提取首页作为封面图，代替占位图标
2. **详情弹窗**：点击卡片后弹出 `QDialog` 显示书籍完整信息（作者、简介、阅读进度等），而非简单的 QMessageBox
3. **右键菜单**：卡片/表格行上右键弹出操作菜单（编辑信息、删除、打开文件位置等）
4. **搜索框**：左侧面板顶部加一个 `QLineEdit`，输入书名实时过滤
5. **拖拽调整卡片大小**：封面网格的列数随窗口宽度自适应
6. **深色模式**：通过 QSS 切换
