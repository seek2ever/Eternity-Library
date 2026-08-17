import random
import sqlite3
from typing import Union
from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)


class DatabaseManager(QObject):
    # 信号必须在类层级定义，不能在__init__中定义
    duplicate_book = Signal(str)  # 发送重复书籍名称
    add_book_result = Signal(bool, str)  # 返回处理结果（成功状态，消息）

    def __init__(self, db_name='books_information.db'):
        super().__init__()
        self.db_name = db_name  # 数据库名称
        self.connection = sqlite3.connect(self.db_name)  # 连接到数据库
        self.cursor = self.connection.cursor()  # 创建一个Cursor（游标）对象，用于执行SQL语句
        self.pending_book = None  # 临时存储待处理的书籍数据

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books_information (
                book_id INTEGER,
                book_name TEXT NOT NULL,
                book_path TEXT,
                add_time TEXT,
                author TEXT,
                nationality TEXT,
                translator TEXT,
                publisher TEXT,
                publication_date TEXT,
                level TEXT,
                read_status TEXT,
                book_type TEXT,
                isbn INTEGER,
                pages INTEGER,
                read_progress TEXT,
                read_time REAL,
                read_date TEXT,
                read_link TEXT,
                introduction TEXT
        )
        """)
        self.connection.commit()

    def column_titles(self) -> list:
        """
        获取列的标题信息
        """
        titles = self.cursor.execute("PRAGMA table_info(books_information)").fetchall()
        translations = [
            {titles[0]: '书籍ID'},
            {titles[1]: '书籍名称'},
            {titles[2]: '书籍路径'},
            {titles[3]: '添加时间'},
            {titles[4]: '作者'},
            {titles[5]: '国籍'},
            {titles[6]: '译者'},
            {titles[7]: '出版社'},
            {titles[8]: '出版日期'},
            {titles[9]: '书籍等级'},
            {titles[10]: '阅读状态'},
            {titles[11]: '书籍类型'},
            {titles[12]: 'ISBN'},
            {titles[13]: '页数'},
            {titles[14]: '阅读进度'},
            {titles[15]: '阅读时间'},
            {titles[16]: '阅读日期'},
            {titles[17]: '阅读链接'},
            {titles[18]: '简介'}
        ]
        return titles

    def column_titles_translation(self):
        """
        获取列的标题信息并翻译
        """
        # TODO: translations内容采用键值对考虑是否比元组形式更好？
        titles = self.column_titles()

    def transfer_title_type(self) -> list:
        """获取并提取标题列信息中的“标题”，用于设置显示在控件中的表格各列标题"""
        titles = self.column_titles()
        return [title[1] for title in titles]

    def add_column(self, table_name, column_name, column_type='TEXT'):
        """
        添加新的列
        :param table_name: 表名
        :param column_name: 列名
        :param column_type: 列类型
        """
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        self.cursor.execute(sql)
        self.connection.commit()

    def _gen_new_name(self, old_name):
        """
        生成唯一的书籍名称，如果书籍名称与已存在书籍重复，自动为其添加数字后缀进行重命名。
        :param old_name: 初始书籍名称
        :return: 生成的唯一书籍名称
        """
        suffix = 1
        while True:
            sql = "SELECT COUNT(*) FROM books_information WHERE book_name = ?"
            new_name = f"{old_name}({suffix})" if suffix > 1 else old_name  # TODO 待修复：重命名逻辑存在问题，无法自动添加后缀
            self.cursor.execute(sql, (new_name,))

            count = self.cursor.fetchone()[0]
            if count == 0:
                return new_name

            suffix += 1

    def add_book(self, **kwargs):  # 以关键字参数的形式接收书籍信息
        """
        添加书籍信息，如果书籍名称与已存在书籍重复，自动跳过该书籍的录入步骤。
        :param kwargs: 书籍信息
        """
        self.pending_book = kwargs  # 将待处理的书籍数据存储在类的属性中
        old_name = kwargs['book_name']
        sql_pass = 'SELECT * FROM books_information WHERE book_name=?'
        self.cursor.execute(sql_pass, (old_name,))
        # 如果数据库中已经存在同名书籍
        if self.cursor.fetchall():
            self.duplicate_book.emit(old_name)  # 发送信号，通知主窗口书籍已存在，请选择是否继续添加
        else:
            self._insert_book(kwargs)  # 执行插入操作

    def handle_duplicate_book(self, choice: str, original_name: str):
        """
        处理用户选择的重复书籍操作
        :param choice: 'skip'/'overwrite'/'rename'
        :param original_name: 原始书名
        """
        # 发送信号，通知主窗口已跳过重复书籍
        if choice == 'skip':
            self.add_book_result.emit(False, "已跳过重复书籍")

        # 执行覆盖操作
        elif choice == 'overwrite':
            self.delete_book(original_name)
            self._insert_book(self.pending_book)

        # 执行重命名操作
        elif choice == 'rename':
            new_name = self._gen_new_name(original_name)
            self.pending_book['book_name'] = new_name
            self._insert_book(self.pending_book)

    def _insert_book(self, book_data):
        """实际插入数据的内部方法"""
        try:
            columns = ', '.join(book_data.keys())
            placeholders = ', '.join(['?'] * len(book_data))
            sql = f"INSERT INTO books_information ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, tuple(book_data.values()))
            self.set_book_id(book_data['book_name'])
            self.connection.commit()
        except Exception as e:
            self.add_book_result.emit(False, f"书籍添加失败！错误信息：{e}")
            self.add_book_result.emit(True, f"书籍添加成功！")

    def set_book_id(self, book_name):
        """
        为添加到数据库中的书籍设置唯一的书籍ID（由随机生成的10位整数组成）
        :param book_name: 需要设置ID的书籍名称
        :return:
        """
        # 查询数据库中是否已经存在该书籍对应的ID
        sql = "SELECT book_id FROM books_information WHERE book_name=?"
        self.cursor.execute(sql, (book_name,))
        result = self.cursor.fetchone()
        # 如果存在匹配的记录，将查询结果的第一个元素赋值给变量result；否则，将变量result设为None
        result = result[0] if result else None

        # 如果不存在，则生成新的ID
        if result is None:
            while True:
                book_id = random.randint(1000000000, 9999999999)
                # 查询数据库中是否已经存在相同ID，确保生成的ID不与数据库中已有的ID重复
                check_sql = "SELECT 1 FROM books_information WHERE book_id=?"
                self.cursor.execute(check_sql, (book_id,))
                existing_id = self.cursor.fetchone()

                # 如果不存在重复ID，则使用新生成的ID，退出循环
                if existing_id is None:
                    break

            # 更新书籍的ID
            update_sql = "UPDATE books_information SET book_id=? WHERE book_name=?"
            self.cursor.execute(update_sql, (book_id, book_name))
            self.connection.commit()

    def delete_book(self, book_name, book_id=None):
        """
        删除书籍信息
        :param book_id：书籍ID
        :param book_name: 书籍名称
        """
        sql = "DELETE FROM books_information WHERE book_name=?"
        self.cursor.execute(sql, (book_name,))
        self.connection.commit()

    def _delete_all_books(self):
        """
        删除所有书籍信息
        """
        sql = "DELETE FROM books_information"
        self.cursor.execute(sql)
        self.connection.commit()

    def update_book(self, book_name, **kwargs):
        """
        更新书籍信息(增加、修改或删除相关信息)
        :param book_name: 书籍名称
        :param kwargs: 更新的书籍信息
        """
        columns = ', '.join([f'{key}=?' for key in kwargs.keys()])  # 以逗号分隔的列名
        values = tuple(kwargs.values()) + (book_name,)

        sql = f"UPDATE books_information SET {columns} WHERE book_name=?"
        self.cursor.execute(sql, values)
        self.connection.commit()
        # TODO: 用户修改本地文件名称时，自动更新数据库中的书籍名称

    def check_book_info(self, book_name) -> str:
        """
        检查书籍是否存在于数据库中
        :param book_name: 书籍名称
        :return: 如果书籍存在，返回True；否则，返回提示
        """
        sql = "SELECT * FROM books_information WHERE book_name=?"
        self.cursor.execute(sql, (book_name,))
        if not None:
            return self.cursor.fetchone()
        else:
            return f"未找到名为{book_name}的书籍"

    def get_book(self, book_name, columns=None) -> Union[list, str]:
        """
        获取指定书籍的部分信息（默认返回所有信息）
        :param book_name：书籍名称
        :param columns：指定要获取的列名列表，默认为None，表示获取书籍的所有信息
        :return: 书籍信息列表，元素只有一个元组，元组中的元素为书籍的各项信息，
        如 [(4071916953, '学术规范导论', 'F:/Books', '2024年04月18日 23:49:50', None, ..., None)]
        """
        try:
            sql_check = f"SELECT * FROM books_information WHERE book_name=?"
            self.cursor.execute(sql_check, (book_name,))
        except sqlite3.OperationalError:
            return f'没有查询到名为"{book_name}"的书籍，请重试。'
        else:
            # 如果指定了要获取的列名(即columns不为空)，则根据指定的列名查询书籍信息
            if columns is not None:
                sql = f"SELECT {columns} FROM books_information WHERE book_name=?"
                self.cursor.execute(sql, (book_name,))
                books = self.cursor.fetchall()
                return books

            # 如果没有指定要获取的列名，则查询书籍的所有信息
            else:
                sql = f"SELECT * FROM books_information WHERE book_name=?"
                self.cursor.execute(sql, (book_name,))
                books = self.cursor.fetchall()
                return books

    def get_all_books(self) -> list:
        """
        :return: 所有书籍的信息列表，每个元素都是一个元组
        例如：(7965672015, '中国科学技术史 天文学卷', 'F:/Books', '2024年04月18日 23:49:50', None, ..., None)
        """
        sql = "SELECT * FROM books_information"
        self.cursor.execute(sql)
        books = self.cursor.fetchall()
        return books

    def get_books_by_type(self, book_type):
        """
        根据书籍类型获取书籍信息
        :param book_type: 书籍类型
        :return: 所有书籍信息列表，元素是一个元组
        """
        sql = "SELECT * FROM books_information WHERE book_type=?"
        self.cursor.execute(sql, (book_type,))
        return self.cursor.fetchall()

    def get_books_by_status(self, status):
        """
        根据书籍状态获取书籍信息
        :param status: 书籍状态
        :return: 所有书籍信息列表，元素是一个元组
        """
        sql = "SELECT * FROM books_information WHERE status=?"
        self.cursor.execute(sql, (status,))
        return self.cursor.fetchall()

    def get_books_by_author(self, author):
        """
        根据作者获取书籍信息
        :param author: 作者名称
        :return: 所有书籍信息列表，元素是一个元组
        """
        sql = "SELECT * FROM books_information WHERE author=?"
        self.cursor.execute(sql, (author,))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()


class BookQueryWorker(QObject):
    """在后台线程中执行数据库查询，避免阻塞 UI 主线程

    关键设计：
    - __init__ 只接收 db_name（字符串），不接收连接/游标对象
    - 每次查询在自己的线程内创建独立 sqlite3 连接，查完即关
    - 这是 SQLite 线程安全的基本要求：连接不能跨线程共享
    """
    books_ready = Signal(list)  # 查询成功，携带书籍列表
    query_error = Signal(str)  # 查询失败，携带错误信息
    trigger_fetch = Signal()  # 触发 fetch_all_books 在后台线程执行

    def __init__(self, db_name: str):
        """
        :param db_name: 数据库文件（如 'books_information.db'）
        """
        super().__init__()
        self.db_name = db_name

    def _execute_query(self, sql: str, params: tuple = ()):
        """在工作线程中执行查询，创建独立连接，查完即关"""
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchall()
            cursor.close()
            self.books_ready.emit(result)
        except Exception as e:
            self.query_error.emit(str(e))
        finally:
            conn.close()

    @Slot()     # 把方法注册到 Qt的元对象系统，确保跨线程排队调用时正确识别执行
    def fetch_all_books(self):
        """查询全部书籍（在工作线程中执行）"""
        self._execute_query("SELECT * FROM books_information")

    def fetch_books_by_type(self, book_type: str):
        """按类型查询（预留，待后续接入分类筛选功能）"""
        self._execute_query(
            "SELECT * FROM books_information WHERE book_type=?", (book_type,)
        )

    def fetch_books_by_status(self, status: str):
        """按阅读状态查询（预留）"""
        self._execute_query(
            "SELECT * FROM books_information WHERE read_status=?", (status,)
        )

    def fetch_books_by_author(self, author: str):
        """按作者查询（预留）"""
        self._execute_query(
            "SELECT * FROM books_information WHERE author=?", (author,)
        )


if __name__ == '__main__':
    db = DatabaseManager()
    res = db.column_titles()
    num = 0
    for i in res:
        num += 1
        print(i.values())
    db.close()  # 必须调用close方法关闭Cursor对象和Connection对象，否则会造成资源泄露
