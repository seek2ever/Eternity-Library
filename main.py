import time


class Books:
    """
    关于各种书籍的类，基本属性包括：书籍名称、作者、国籍、译者、出版单位、
    出版日期、评分（1至5⭐）、页数、书籍类型（专业书籍、其它专著、文学作品、课外读物）、ISBN码、
    阅读状态(尚未阅读、正在阅读、暂停阅读、阅读完成）、阅读进度、阅读时长、内容简介
    """

    def __init__(self, book_name, author, publisher="", publication_date="", pages="", grade="",
                 isbn="", translator="", nationality="", book_type="",
                 reading_status="", reading_time="", reading_progress="", introduction=""):
        self.book_name = book_name
        self.author = author
        self.publisher = publisher
        self.publication_date = publication_date
        self.pages = pages
        self.grade = grade
        self.isbn = isbn
        self.translator = translator
        self.nationality = nationality
        self.book_type = book_type
        self.reading_status = reading_status
        self.reding_time = reading_time
        self.reading_progress = reading_progress
        self.introduction = introduction

        print(f"书籍名称：{self.book_name}\n作者：{self.author}\n出版社：{self.publisher}\n评分：{self.grade}")

    def book_animation(self):
        """控制电子书打开、关闭、翻页时的动画效果"""
        pass

    def reading_duration(self):
        """统计书籍的阅读时长，包括阅读的天数、阅读的小时数"""
        add_time = time.time()              # 添加书籍到书库时获取的系统时间
        open_time = time.time()             # 阅读书籍时获取的系统时间

    def reading_edit_pdf(self):
        """对pdf格式的书籍进行编辑"""
        pass

    def reading_edit_epub(self):
        """对epub格式的书籍进行编辑"""
        pass

    def reading_edit_txt(self):
        """对txt格式的书籍进行编辑"""
        pass

    def reading_status(self):
        """统计书籍的阅读状态"""
        books_status = ['尚未阅读', '正在阅读', '暂停阅读', '阅读完成']
        if eval(self.reading_progress) == 0:
            self.reading_status = books_status[0]              # 将阅读状态设置为“尚未阅读”
        elif eval(self.reading_progress) == 100:
            self.reading_status = books_status[-1]             # 将阅读状态设置为“阅读完成”
        else:
            self.reading_status = input()                      # 由用户从给定的列表中选择阅读状态


history_book = Books("Python编程：从入门到实践", "埃里克·马瑟斯", nationality="美国")
