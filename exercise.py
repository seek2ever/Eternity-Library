from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt


class MyModel(QStandardItemModel):
	def __init__(self):
		super().__init__()
		self._data = []  # 存储数据的列表

<<<<<<< HEAD
	def rowCount(self, parent=None):
		return len(self._data)

	def data(self, index, role):
		if not index.isValid():
			return None
		row = index.row()
		if row < 0 or row >= len(self._data):
			return None
		item = self._data[row]
		if role == Qt.DisplayRole:
			return item.get("name", "")
		elif role == Qt.ToolTipRole:
			return item.get("name", "")
		elif role == Qt.UserRole + 1:
			return item.get("id")
		elif role == Qt.UserRole + 2:
			return item.get("name", "")
		elif role == Qt.UserRole + 3:
			return item.get("author", "")
		elif role == Qt.UserRole + 4:
			return item.get("type", "")
		elif role == Qt.UserRole + 5:
			return item.get("cover_path")
		return None
=======
N = 50_000_000
>>>>>>> 63617214c93afcdbe826ecb4932da964ddc9291a

	def setDataList(self, data_list):
		"""设置数据列表，并刷新模型"""
		self.beginResetModel()
		self._data = data_list
		self.endResetModel()

<<<<<<< HEAD
	def sort(self, column, order=Qt.AscendingOrder):
		"""按指定列排序"""
		if column == 0:  # 按 name 排序
			self._data.sort(key=lambda x: x.get("name", ""), reverse=(order == Qt.DescendingOrder))
		elif column == 1:  # 按 author 排序
			self._data.sort(key=lambda x: x.get("author", ""), reverse=(order == Qt.DescendingOrder))
		elif column == 2:  # 按 type 排序
			self._data.sort(key=lambda x: x.get("type", ""), reverse=(order == Qt.DescendingOrder))
		self.layoutChanged.emit()  # 通知视图数据已更改
=======
# 多线程：约 6.4 秒（没有并行加速，GIL 限制了执行）
start = time.perf_counter()
t1 = threading.Thread(target=cpu_heavy_work, args=(N,))
t2 = threading.Thread(target=cpu_heavy_work, args=(N,))
t1.start()
t2.start()
t1.join()
t2.join()
print(f"多线程耗时: {time.perf_counter() - start:.2f} 秒")
# 输出：多线程耗时：6.38 秒（几乎没有加速）
>>>>>>> 63617214c93afcdbe826ecb4932da964ddc9291a
