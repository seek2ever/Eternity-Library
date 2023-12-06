import time


class Books:
    """
    关于各种书籍的类，基本属性包括：书籍名称、作者、国籍、译者、出版单位、
    出版日期、评分（1至5⭐）、页数、书籍类型（专业书籍、其它专著、文学作品、课外读物）、ISBN码、
    阅读状态(尚未阅读、正在阅读、暂停阅读、阅读完成）、阅读进度、阅读时长、内容简介
    """

    def __init__(self, book_name, author, nationality="", translator="", publisher="", publication_date="", level="",
                 reading_status="", book_type="", isbn="", pages="", reading_progress="",
                 reading_time="", reading_date="", reading_link="", introduction=""):
        self.book_name = book_name
        self.author = author
        self.nationality = nationality
        self.translator = translator
        self.publisher = publisher
        self.publication_date = publication_date
        self.level = level
        self.reading_status = reading_status
        self.book_type = book_type
        self.isbn = isbn
        self.pages = pages
        self.reading_progress = reading_progress
        self.reding_time = reading_time                 # 阅读时长（单位：小时）
        self.reading_date = reading_date
        self.reading_link = reading_link                # 第三方阅读器或书籍评分网站（如豆瓣读书）的网址链接
        self.introduction = introduction

        print(f"书籍名称：{self.book_name}\n作者：{self.author}\n出版社：{self.publisher}\n评分：{self.level}")

    def level(self):
        """统计书籍的评分情况，以一到五个⭐表示，分别表示书籍由低到高的评价"""
        level_symbol = ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐']
        set_level = input()

    def reading_status(self):
        """统计书籍的阅读状态"""
        books_status = ['尚未阅读', '正在阅读', '暂停阅读', '阅读完成']
        if eval(self.reading_progress) == 0:
            self.reading_status = books_status[0]              # 将阅读状态设置为“尚未阅读”
        elif eval(self.reading_progress) == 100:
            self.reading_status = books_status[-1]             # 将阅读状态设置为“阅读完成”
        else:
            self.reading_status = input()                      # 由用户从给定的列表中选择阅读状态

    def reading_duration(self):
        """统计书籍的阅读时长，包括阅读的天数、阅读的小时数（可切换为x时x分的格式"""
        add_time = time.time()              # 添加书籍到书库时获取的系统时间
        last_time = time.time()             # 最后一次阅读书籍或书籍标记为“阅读完成”时获取的系统时间
        open_time = time.time()             # 阅读书籍时获取的系统时间
        close_time = time.time()            # 每次关闭书籍时获取的系统时间

    def book_animation(self):
        """控制电子书打开、关闭、翻页时的动画效果"""
        pass

    def reading_edit_pdf(self):
        """对pdf格式的书籍进行编辑"""
        pass

    def reading_edit_epub(self):
        """对epub格式的书籍进行编辑"""
        pass

    def reading_edit_txt(self):
        """对txt格式的书籍进行编辑"""
        pass


history_book = Books("Python编程：从入门到实践", "埃里克·马瑟斯", nationality="美国")
