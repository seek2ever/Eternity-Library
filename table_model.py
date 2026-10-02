from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)


class BookTableModel(QAbstractTableModel):
    """表格视图的数据模型"""

    # 自定义 data role
    BookIdRole = Qt.UserRole + 1  # book_id
    BookNameRole = Qt.UserRole + 2  # book_name
    AuthorRole = Qt.UserRole + 3  # author
    BookTypeRole = Qt.UserRole + 4  # book_type
    CoverPathRole = Qt.UserRole + 5  # 封面图片路径（预留）

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_books = []  # 存储书籍数据的列表，每个元素是一个字典，包含书籍的各个字段

    def set_data(self, books):
        """设置表格的数据源"""
        self.beginResetModel()
        self._table_books = books
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        """返回表格的行数，即书籍的数量"""
        return len(self._table_books)

    def columnCount(self, parent=QModelIndex()):
        """返回表格的列数"""
        return len(self._table_books[0]) if self._table_books else 0

    def data(self, index, role=Qt.DisplayRole):
        """返回指定单元格的数据"""
        if not index.isValid():
            return None

        # TODO：从数据库返回的数据为元组形式，但自定义Role中使用了.get()，delegate后续使用这些Role会出错
        if role == Qt.DisplayRole:
            return self._table_books[index.row()][index.column()]
        elif role == self.BookIdRole:
            return self._table_books[index.row()].get("id")
        elif role == self.BookNameRole:
            return self._table_books[index.row()].get("name", "")
        elif role == self.AuthorRole:
            return self._table_books[index.row()].get("author", "")
        elif role == self.BookTypeRole:
            return self._table_books[index.row()].get("type", "")
        elif role == self.CoverPathRole:
            return self._table_books[index.row()].get("cover_path")

        return None

    def headerData(self, section, orientation, /, role=...):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["ID", "书名", "路径", "添加日期", "作者"][section]
            else:
                return str(section + 1)
        return None
