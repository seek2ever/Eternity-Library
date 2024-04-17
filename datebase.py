import sqlite3
import random


class DatabaseManager:
    def __init__(self, db_name='books_information.db'):
        self.db_name = db_name  # 数据库名称
        self.connection = sqlite3.connect(self.db_name)  # 连接到数据库
        self.cursor = self.connection.cursor()  # 创建一个Cursor（游标）对象，用于执行SQL语句

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books_information (
                book_id INTEGER,
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
        """
        添加书籍信息
        :param kwargs: 书籍信息
        """
        columns = ', '.join(kwargs.keys())  # 以逗号分隔的列名
        placeholders = ', '.join(['?'] * len(kwargs))  # 以逗号分隔的占位符
        sql = f"INSERT INTO books_information ({columns}) VALUES ({placeholders})"  # SQL语句
        self.cursor.execute(sql, tuple(kwargs.values()))  # 执行SQL语句
        self.connection.commit()  # 提交事务

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
                # 查询数据库中是否已经存在该书籍对应的ID
                check_sql = "SELECT 1 FROM books_information WHERE book_id=?"
                self.cursor.execute(check_sql, (book_id,))
                existing_id_result = self.cursor.fetchone()

                # 如果不存在，则使用新生成的ID并更新数据库，退出循环
                if existing_id_result is None:
                    break

            update_sql = "UPDATE books_information SET book_id=? WHERE book_name=?"
            self.cursor.execute(update_sql, (book_id, book_name))
            self.connection.commit()

    def delete_book(self, book_name):
        """
        删除书籍信息
        :param book_name: 书籍名称
        """
        sql = "DELETE FROM books_information WHERE book_name=?"
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

        sql = f"UPDATE books_information SET {columns} WHERE book_name=?"
        self.cursor.execute(sql, values)
        self.connection.commit()

    def get_books(self, book_name):
        """
        获取所有书籍信息
        :return: 书籍信息列表
        """
        sql = "SELECT * FROM books_information WHERE book_name=?"
        self.cursor.execute(sql, (book_name,))
        books = self.cursor.fetchall()
        print(books)

    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    db = DatabaseManager()
    db.create_table()
    db.set_book_id(
        book_name='活着'
    )
    db.get_books('活着')
    db.close()                  # 必须调用close方法关闭Cursor对象和Connection对象，否则会造成资源泄露
