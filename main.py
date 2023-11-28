class Books:
    """
    关于各种书籍的类，基本属性包括：书籍名称、作者、国籍、译者、出版单位、
    出版日期、评分（1至5⭐）、页数、书籍类型（专业书籍、其它专著、文学作品、课外读物）、ISBN码、
    阅读状态(尚未阅读、正在阅读、暂停阅读、阅读完成）、阅读进度、阅读时长、内容简介
    """

    def __init__(self, book_name, author, publisher="未知", publication_date="未知", pages=0, grade="⭐️",
                 isbn="无", translator="无", nationality="中国", book_type="专业书籍",
                 reading_status="尚未阅读", reading_time="无", reading_progress=0, introduction="无"):
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
        """统计书籍的阅读时长"""
        pass


history_book = Books("中西文化交流史", "沈福伟")
