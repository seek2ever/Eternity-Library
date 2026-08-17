# 列表视图卡顿修复方案 —— show_book_info() 主线程阻塞问题

> 问题：每次切换到列表视图时，界面都会有一瞬间的卡顿。
> 根因：`show_book_info()` 直接在**主线程**同步查询数据库 + 全量重建表格 + 重算列宽/行高。
>
> 本方案不新增任何类，完全复用项目里已有的 `BookQueryWorker` 后台线程链路，改动只集中在 `el_gui.py`。

---

## 1. 问题诊断

### 1.1 卡顿发生在哪

点击"切换到列表视图"后，调用链如下（**全部在主线程执行**）：

```
主线程:
_toggle_view_mode()                # el_gui.py:303  切换 QStackedWidget
  └→ show_book_info()              # el_gui.py:374
      ├→ self.db.get_all_books()   # ① 同步 SQLite 查询（主线程阻塞）
      ├→ 双重循环 new QTableWidgetItem  # ② 每本书 × 19 个字段控件
      └→ resizeRowsToContents()    # ③ 遍历每个单元格重算行高
         resizeColumnsToContents() # ④ 遍历每个单元格重算列宽（最慢）
```

### 1.2 三个主线程阻塞源

| # | 阻塞源 | 位置 | 耗时因素 |
|---|--------|------|----------|
| ① | 同步数据库查询 | el_gui.py:377 `self.db.get_all_books()`（database.py:271） | `SELECT *` 全量拉取 + 磁盘 I/O |
| ② | 逐格创建控件 | el_gui.py:386-389 双重循环 | 每本书 new 19 个 `QTableWidgetItem`，书多时上千个对象 |
| ③ | 全表尺寸重算 | el_gui.py:391-392 `resizeRowsToContents()` / `resizeColumnsToContents()` | 遍历所有单元格做布局测量，**通常是最慢的元凶** |

### 1.3 关键结论：已有的后台线程没被用上

你的项目其实**已经有**后台查询线程——`_setup_book_worker()`（el_gui.py:79）创建的 `_query_thread` + `BookQueryWorker`（database.py:316）。但它**只服务封面视图**：

```
refresh_cover_view() ──trigger_fetch 信号──▶ 后台线程执行 SQL
        ▲                                        │ books_ready 信号
        │                                        ▼
_on_books_loaded() ◀─────────────────────────── 回主线程
   └→ cover_model.set_books()   # 只更新封面模型
```

而列表视图的 `show_book_info()` 完全绕开了这条链路，自己同步查了一遍。所以切到列表视图时，主线程被"同步查询 + 建上千个 Item + resize"一起堵住，界面就卡一下。

> **一句话总结**：卡顿 = 不该在主线程做的事（数据库查询） + 不该每次都做重的事（重建表格 + 重算尺寸）。

---

## 2. 解决方案总览

**核心思路：把列表视图并入已有的后台查询链路，并且让表格只在"数据真正变化"时重建一次，而不是每次切换视图都重建。**

| 方案 | 解决的问题 | 改动点 |
|------|-----------|--------|
| A. 抽出 `_populate_table()` | 填表 + resize 逻辑与查询逻辑解耦 | `el_gui.py` 新增方法 |
| B. `show_book_info()` 不再直接查库 | 数据库查询阻塞主线程 | `el_gui.py` 改 `show_book_info()` |
| C. `_on_books_loaded()` 同时刷新两个视图 + 防重复重建 | 每次切换都重建表格 | `el_gui.py` 改 `_on_books_loaded()` |
| D. 附带清理 | 启动时多余同步查询、点击单元格重查、添加后缓存失效 | `el_gui.py` 顺带修改 |

> **推荐顺序**：A → B → C → D，每步都能独立运行验证。

---

## 3. 方案 A：抽出 `_populate_table(books)` 方法

把 `show_book_info()` 里"填表格"这段逻辑单独抽成一个方法，职责单一、便于复用。

### 3.1 新方法代码

```python
# ─────────────────────────────────────────────────────────────
# 新增方法：把书籍列表填充进表格（本方法只做 UI 填充，不做数据库查询）
# ─────────────────────────────────────────────────────────────
def _populate_table(self, books: list) -> None:
    """把书籍列表填充进列表视图的表格。

    核心优化：表格只在"数据确实变化"时重建。
    用 self._table_source 记住上次填充的是哪一份数据对象，
    如果这次要填的还是同一个对象（缓存命中场景），就直接跳过，
    避免每次切换视图都重复 new 上千个 Item 并重算尺寸。
    """
    # 同一份数据对象（Python 的 is 比较的是对象身份，不是内容）
    # 就说明表格内容没变，直接返回，不做任何重活
    if books is self._table_source:
        return
    # 记录本次数据源，下次填充时用于比对
    self._table_source = books

    # 清空表格中现有的数据（只清内容，保留列结构）
    self.book_table.clearContents()

    # 设置表格的行数 = 书籍数量；列数已在创建表格时定好
    self.book_table.setRowCount(len(books))

    # 双重循环：为每个单元格创建一个 QTableWidgetItem
    # 这里不可避免要创建大量控件，所以把它放在"数据真正变化"时才执行
    for row, book_row in enumerate(books):
        for col, book_data in enumerate(book_row):
            item = QTableWidgetItem(str(book_data))
            self.book_table.setItem(row, col, item)

    # resizeRowsToContents / resizeColumnsToContents 会遍历所有单元格做布局计算，
    # 是最耗时的一步。由于上面已经用 _table_source 挡住重复调用，
    # 这些重活只在数据变化时执行一次，切换视图时不会再触发。
    self.book_table.resizeRowsToContents()
    self.book_table.resizeColumnsToContents()
    self.book_table.setAlternatingRowColors(True)  # 隔行交替颜色
```

### 3.2 原理说明

- **`books is self._table_source`**：Python 的 `is` 比较的是两个变量是否指向**同一个对象**，不是比较内容。同一份缓存列表在 30 秒有效期内是同一个对象，所以切换视图时 `is` 判定为 `True`，直接跳过重建。
- **为什么能判定"内容没变"**：数据只来自两个地方——缓存（同一个对象）或后台线程新查询（新对象）。新查询产生新对象 → `is` 为 `False` → 重建；缓存命中 → 同一对象 → 跳过。

---

## 4. 方案 B：`show_book_info()` 不再直接查数据库

改造后，`show_book_info()` 只负责"确保数据已加载"，数据获取统一走已有的后台链路。

### 4.1 改造后的 `show_book_info()`

```python
# ─────────────────────────────────────────────────────────────
# 修改：show_book_info() 不再直接调用 self.db.get_all_books()
# ─────────────────────────────────────────────────────────────
def show_book_info(self) -> None:
    """获取书籍信息并展示。

    修改要点：这里不再直接执行数据库查询。
    数据获取统一交给 refresh_cover_view() → 后台线程 → _on_books_loaded()。
    好处：
      1. 数据库查询从主线程挪到后台线程，界面不再被 I/O 阻塞；
      2. 查询结果会同时刷新封面视图和列表视图，两处数据保持一致；
      3. 表格的填充由 _populate_table() 的防重复机制控制，
         切换视图时不会重复重建表格。
    """
    self.refresh_cover_view()
```

### 4.2 行为变化说明

| 场景 | 改造前 | 改造后 |
|------|--------|--------|
| 点击"显示书籍信息"按钮 | 主线程同步查询 → 填表 | 触发后台查询/使用缓存，界面不卡 |
| 切换到列表视图 | 每次全量重建表格 | 缓存命中则直接跳过，瞬间完成 |
| 数据库为空时 | 弹窗"书籍索引信息为空。" | 不再弹窗（表格自然为空） |

> `refresh_cover_view()` 这个名字目前暗示"只刷封面"，改造后它实际会刷新两个视图。可以保留原名（改动最小），也可以顺手改名为 `refresh_views`（不强制）。

---

## 5. 方案 C：`_on_books_loaded()` 同时刷新两个视图

改造后，后台查询结果到达主线程时，封面模型和表格一起更新。

### 5.1 改造后的 `_on_books_loaded()`

```python
# ─────────────────────────────────────────────────────────────
# 修改：收到后台查询结果后，同时刷新封面视图和列表视图
# ─────────────────────────────────────────────────────────────
def _on_books_loaded(self, books: list) -> None:
    """收到后台查询结果（在主线程执行），同时喂给封面模型和列表表格。

    之前这里只更新封面模型，现在加上了 _populate_table(books)，
    列表视图的数据也由同一次查询结果驱动，两处永远一致。
    """
    if not books:
        # 数据库为空：清空表格并复位防重建标记，
        # 否则下次查询到新数据时会因为 _table_source 残留而跳过重建
        self.book_table.setRowCount(0)
        self._table_source = None
        return

    self._books_cache = books            # 缓存本次结果
    self._cache_timestamp = time.time()  # 记录缓存时间

    # 封面视图：喂给模型，View 自动重绘
    self.cover_model.set_books(books)

    # 列表视图：填充表格（内部有防重复机制，数据没变会自动跳过）
    self._populate_table(books)

    self.statusbar.showMessage(
        self._translate("Views", f"已刷新，共 {len(books)} 本书")
    )
```

> 注意状态栏文案从"封面视图已刷新"改成了"已刷新"，因为现在两个视图都被刷新了。

### 5.2 初始化 `_table_source`

在 `_setup_book_worker()`（el_gui.py:79）里，和其他缓存变量一起初始化：

```python
def _setup_book_worker(self):
    """初始化后台查询线程、缓存变量"""
    # 缓存最后一次查询结果
    self._books_cache = None
    self._cache_timestamp = 0  # 缓存时间戳

    # ===== 新增：列表表格上次填充的数据对象（用于防重复重建）=====
    self._table_source = None
    # ... 其余线程初始化代码保持不变 ...
```

---

## 6. 方案 D：附带清理（顺带消除其他主线程浪费）

以下问题不是本次卡顿的主因，但顺手处理掉，避免埋雷。

### 6.1 `_create_table_view()` 去掉启动时的同步查询

el_gui.py:290 在创建表格时调用了一次 `self.db.get_all_books()`，但结果只用到了**行数**——而行数在 `_populate_table()` 里会被重新设置，这个查询完全多余。

```python
# ─────────────────────────────────────────────────────────────
# 修改：创建表格时不再查询数据库
# ─────────────────────────────────────────────────────────────
def _create_table_view(self) -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(16, 16, 16, 16)

    toolbar = QHBoxLayout()     # 列表视图最上方的标签行
    mode_label = QLabel(self._translate("Table View", "列表模式"))
    mode_label.setStyleSheet("font-size: 13pt; font-weight: bold;")
    toolbar.addWidget(mode_label)
    toolbar.addStretch()
    layout.addLayout(toolbar)

    # 添加"书籍列表"表格
    self.book_table = QTableWidget()
    self.book_table.setObjectName("book_table")

    # 列数 = 标题数；行数先设为 0，等数据加载后再由 _populate_table() 设置
    # 原来这里调用 self.db.get_all_books() 做同步查询，但行数后续会被
    # _populate_table() 重新设置，所以这个查询完全可以去掉。
    titles = self.db.transfer_title_type()
    self.book_table.setRowCount(0)
    self.book_table.setColumnCount(len(titles))
    self.book_table.setHorizontalHeaderLabels(titles)  # 设置列标题

    # 移除：self.book_table.clicked.connect(self.show_book_info)
    # 原因：点击任意单元格都会触发一次全表重新加载，纯属浪费。
    # 表格数据由后台查询统一驱动，不需要点击时再手动刷新。

    layout.addWidget(self.book_table)
    return container
```

### 6.2 `show_add_result()` 成功后强制刷新缓存

添加新书后，如果缓存还在 30 秒有效期内，`refresh_cover_view()` 会返回**过期的旧数据**，导致新书 30 秒内不显示。需要在成功添加后让缓存立即失效。

```python
# ─────────────────────────────────────────────────────────────
# 修改：添加成功后先让缓存失效，再触发查询
# ─────────────────────────────────────────────────────────────
def show_add_result(self, success, message) -> None:
    """显示添加结果"""
    if success:
        Tips.information_msg(message)
        # 新书已入库，旧缓存失效，强制下次查询重新走后台线程
        self._books_cache = None
        self._cache_timestamp = 0
        self.show_book_info()          # 触发后台查询，两个视图一起刷新
        self.statusbar.showMessage(self._translate(
            "success",
            "已成功添加书籍"),
            3000)
    else:
        Tips.information_msg(message)
```

> 注意：原来这里同时调用了 `show_book_info()` 和 `refresh_cover_view()`，改造后两者行为一致，只需调用 `show_book_info()` 一个即可。

### 6.3 `close_info()` 复位防重建标记

"取消显示"按钮只清空表格内容，但 `_table_source` 还指向旧数据。如果不清掉，下次切换视图时会被防重复机制挡住，表格永远空着。

```python
# ─────────────────────────────────────────────────────────────
# 修改：清空表格的同时复位防重建标记
# ─────────────────────────────────────────────────────────────
def close_info(self) -> None:
    """清除主界面的书籍信息"""
    self.book_table.clearContents()
    self.book_table.setRowCount(0)
    self._table_source = None   # 复位标记，下次加载数据时才会重建表格
```

---

## 7. 原理学习（理解为什么这样改）

> 项目要求引入新知识时附解释，以下为本方案涉及的几个核心概念。

### 7.1 Qt 主线程与事件循环

- Qt 程序有且只有一个 **主线程（GUI 线程）**，窗口绘制、鼠标键盘事件、动画都在这里排队处理。
- 如果主线程被一段长时间运行的代码占住（比如同步查数据库、循环创建上千个控件），事件循环就没机会处理新的绘制请求，**界面表现为卡死/卡顿**。
- 所以原则是：**耗时操作放后台线程，UI 操作留在主线程**。

### 7.2 后台线程怎么把结果传回来（信号槽）

你项目里 `_setup_book_worker()` 已经实现了标准做法：

1. 建一个 `QThread`，再建一个 `BookQueryWorker`（QObject 子类）；
2. `moveToThread()` 把 Worker 挪到工作线程，之后 Worker 里的槽函数都在工作线程执行；
3. 用信号跨线程通信：主线程发 `trigger_fetch` → Worker 在工作线程跑 SQL → Worker 发 `books_ready` → 主线程的 `_on_books_loaded()` 收到结果。
4. **跨线程信号自动走 QueuedConnection**（排队），槽函数会在接收方线程的事件循环里执行，天然线程安全。

### 7.3 为什么 SQLite 查询不能在主线程做

- SQLite 查询是磁盘 I/O，耗时不确定，最差情况能阻塞主线程数百毫秒到秒级。
- 你的 `BookQueryWorker` 在工作线程里**独立创建 sqlite3 连接**（database.py:335），查完即关。这是 SQLite 的线程安全要求——连接不能跨线程共享。

### 7.4 为什么"切换视图"本身应该是瞬间的

`QStackedWidget` 切换只是换一个子控件显示（隐藏一个、显示一个），本身就是轻量操作。真正拖慢切换的是切换时顺带做的**数据加载和表格重建**。本方案让"切换"和"加载"解耦：切换只换页，加载在后台完成、完成后通知两个视图。

### 7.5 `is` 身份比较为什么够用

- 缓存命中时，`refresh_cover_view()` 把同一个缓存对象传给 `_on_books_loaded()`，`books is self._table_source` 为 `True` → 跳过重建。
- 后台线程新查询返回的是**新对象**，`is` 为 `False` → 重建一次。
- 30 秒缓存过期 → 必然走新查询 → 数据永远能跟上数据库变化（配合方案 D.2 的缓存失效逻辑更稳妥）。

---

## 8. 改动清单

| 文件 | 操作 | 改动内容 |
|------|------|---------|
| `el_gui.py` | 修改 | `_setup_book_worker()` 加一行 `self._table_source = None` |
| `el_gui.py` | 修改 | `show_book_info()` 方法体替换为 `self.refresh_cover_view()` |
| `el_gui.py` | 修改 | `_on_books_loaded()` 增加 `_populate_table()` 调用和空数据清理 |
| `el_gui.py` | 新增 | `_populate_table(books)` 私有方法 |
| `el_gui.py` | 修改 | `_create_table_view()` 去掉同步查询和 `clicked` 连接 |
| `el_gui.py` | 修改 | `show_add_result()` 成功分支让缓存失效 |
| `el_gui.py` | 修改 | `close_info()` 复位 `_table_source` |
| `database.py` | 无需修改 | 现有 `BookQueryWorker` 直接复用 |

**不新增任何文件，不改动 `database.py`。**

---

## 9. 实施步骤与验证

### 9.1 实施步骤

1. 方案 A：添加 `_populate_table()` 方法（目前没有调用者，先不生效）。
2. 方案 B：改 `show_book_info()` 为 `self.refresh_cover_view()`。
3. 方案 C：改 `_on_books_loaded()` 调用 `_populate_table()`；在 `_setup_book_worker()` 初始化 `_table_source`。
4. 方案 D：依次改 `_create_table_view()`、`show_add_result()`、`close_info()`。
5. 运行 `python el_gui.py` 验证。

### 9.2 验证方法

1. 确保数据库有数据（扫描一个含 50+ 本书的目录，或用 SQLite 工具插入测试数据）。
2. 启动程序，反复点击"切换到列表视图"/"切换到封面视图"按钮。
3. **验证点**：
   - 点击切换按钮后界面立即响应，不再卡顿；
   - 首次加载时列表数据后台异步填充，加载期间界面可操作；
   - 快速反复切换时，表格内容不会闪烁重建；
   - 添加新书后，新书能立即出现在列表里（缓存失效生效）；
   - 点击"取消显示"后再切换视图，表格能重新填充（`_table_source` 复位生效）；
   - 数据库为空时启动程序不报错、表格为空。

---

## 10. 常见问题

**Q1: 改造后首次切到列表视图会看到空白，正常吗？**
正常。首次查询走后台线程，数据到达前表格是空的（毫秒到几十毫秒级）。这是"界面不卡"的代价，远比卡顿可接受。后续切换因为缓存命中，几乎是瞬时的。

**Q2: 为什么不用 `threading.Thread` 而是 QThread？**
Python 的 `threading` 也能起线程，但无法把结果安全地"跨线程送回 UI 线程并让 Qt 控件更新"。QThread + 信号槽的 QueuedConnection 会自动把槽调度回主线程事件循环，天然安全。

**Q3: 表格重建一次仍然可能慢，怎么办？**
如果书非常多（几千本），一次 `_populate_table` 仍可能让主线程卡一下。届时可参考封面视图的思路，把 QTableWidget 换成 `QTableView + QAbstractTableModel`（模型-视图架构，View 只绘制可见行）。这是后续优化方向，本次不必做。

**Q4: 封面视图和列表视图数据会不一致吗？**
不会。两边的数据都来自同一次后台查询结果（`_on_books_loaded` 里的 `books`），是同一份数据喂给两个视图。
