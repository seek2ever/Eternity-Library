from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)


class BookTableModel(QAbstractTableModel):
    """表格视图的数据模型"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._table_books = []  # 存储书籍数据的列表，每个元素是一个字典，包含书籍的各个字段

    def rowCount(self, parent=QModelIndex()):
        """返回表格的行数，即书籍的数量"""
        return len(self._table_books)

    def columnCount(self, parent=QModelIndex()):
        """返回表格的列数"""
        pass

    def set_books(self, books):
        """设置表格的数据源"""
        self.beginResetModel()
        self._table_books = books
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
        """返回指定单元格的数据"""
        pass
