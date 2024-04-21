import os
import sqlite3
import random


class DatabaseManager:
    def __init__(self, db_name='books_information.db'):
        self.db_name = db_name                              # 数据库名称
        self.connection = sqlite3.connect(self.db_name)     # 连接到数据库
        self.cursor = self.connection.cursor()              # 创建一个Cursor（游标）对象，用于执行SQL语句

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

    def add_column(self, table_name, column_name, column_type='TEXT'):
        """
        添加新的列
        :param table_name：表名
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
        base_name, ext = os.path.splitext(old_name)  # 分离文件名和扩展名（假设书籍名称包含扩展名）

        while True:
            new_name = f"{base_name}_{suffix}{ext}" if suffix > 1 else old_name
            sql = "SELECT COUNT(*) FROM books_information WHERE book_name = ?"
            self.cursor.execute(sql, (new_name,))
            count = self.cursor.fetchone()[0]

            if count == 0:
                return new_name

            suffix += 1

    def add_book(self, **kwargs):   # 以关键字参数的形式接收书籍信息
        """
        添加书籍信息，如果书籍名称与已存在书籍重复，自动跳过该书籍的录入步骤。
        :param kwargs: 书籍信息
        """
        book_name = kwargs['book_name']
        sql_pass = 'SELECT * FROM books_information WHERE book_name=?'
        self.cursor.execute(sql_pass, (book_name,))
        if self.cursor.fetchall():
            print(f"书籍： {book_name} 已存在于数据库中。")
        else:
            columns = ', '.join(kwargs.keys())                  # 以逗号分隔的列名
            placeholders = ', '.join(['?'] * len(kwargs))       # 以逗号分隔的占位符
            sql = f"INSERT INTO books_information ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, tuple(kwargs.values()))    # 执行SQL语句
            self.set_book_id(book_name)
            self.connection.commit()                            # 提交事务

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

    # def delete_all_books(self):
    #     """
    #     删除所有书籍信息
    #     """
    #     sql = "DELETE FROM books_information"
    #     self.cursor.execute(sql)
    #     self.connection.commit()

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

    def check_book_info(self, book_name):
        """
        检查书籍是否存在于数据库中
        :param book_name: 书籍名称
        :return: 如果书籍存在，返回True；否则，返回False
        """
        sql = "SELECT * FROM books_information WHERE book_name=?"
        self.cursor.execute(sql, (book_name,))
        return self.cursor.fetchone() is not None

    def get_book(self, book_name, columns=None):
        """
        获取指定书籍的部分信息（默认返回所有信息）
        :param book_name：书籍名称
        :param columns：指定要获取的列名列表，默认为None，表示获取书籍的所有信息
        :return: 书籍信息列表
        """
        try:
            sql_check = f"SELECT {book_name} FROM books_information WHERE book_name=?"
            self.cursor.execute(sql_check, (book_name,))
        except sqlite3.OperationalError:
            return f'没有查询到名为"{book_name}"的书籍，请重试。'
        else:
            # 如果指定了要获取的列名，则根据指定的列名查询书籍信息
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

    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    db = DatabaseManager()
    s = db.get_book('学术规范导论.pdf')
    print(s)
    db.close()                  # 必须调用close方法关闭Cursor对象和Connection对象，否则会造成资源泄露
