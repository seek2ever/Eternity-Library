import sqlite3


class DatabaseManager:
    def __init__(self, db_name='books_info.db'):
        self.db_name = db_name  # 数据库名称
        self.connection = sqlite3.connect(self.db_name)  # 连接到数据库
        self.cursor = self.connection.cursor()  # 创建一个Cursor（游标）对象，用于执行SQL语句

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books_info (
                book_name TEXT NOT NULL,
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

    def add_book(self, **kwargs):  # 以关键字参数的形式接收书籍信息
        columns = ', '.join(kwargs.keys())  # 以逗号分隔的列名
        placeholders = ', '.join(['?'] * len(kwargs))  # 以逗号分隔的占位符
        sql = f'INSERT INTO books_info ({columns}) VALUES ({placeholders})'  # SQL语句
        self.cursor.execute(sql, tuple(kwargs.values()))  # 执行SQL语句
        self.connection.commit()  # 提交事务

    def delete_book(self, book_name):
        """
        删除书籍信息
        :param book_name: 书籍名称
        """
        sql = 'DELETE FROM books_info WHERE book_name=?'
        self.cursor.execute(sql, (book_name,))
        self.connection.commit()

    def update_book(self, book_name, **kwargs):
        """
        更新书籍信息
        :param book_name: 书籍名称
        :param kwargs: 更新的书籍信息
        """
        columns = ', '.join([f'{key}=?' for key in kwargs.keys()])  # 以逗号分隔的列名
        values = tuple(kwargs.values()) + (book_name,)

        sql = f'UPDATE books_info SET {columns} WHERE book_name=?'
        self.cursor.execute(sql, values)

    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    db = DatabaseManager()
    db.create_table()
    db.delete_book(
        book_name='活着'
    )
    db.close()  # 必须调用close方法关闭Cursor对象和Connection对象，否则会造成资源泄露
