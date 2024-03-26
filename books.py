"""
此模块用于处理与书籍文件进行具体交互功能（查找、编辑等）的相关代码，
GUI相关代码放在el_gui.py中
"""
import os
import sys
import time
import datetime
import json
import fitz
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt


class ScanBookFiles(QWidget):
    """
    选择扫描路径的窗口，用户可以通过点击按钮选择扫描文件所在的路径，
    该窗口还会调用scan_book_files函数扫描文件夹中的电子书，并将结果写入文本文件
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('扫描路径')  # 设置窗口标题
        self.setGeometry(1000, 700, 400, 200)  # 设置窗口的位置和大小

        self.directory_label = QLabel('请选择扫描路径：')
        self.selected_directory_label = QLabel("")

        self.select_button = QPushButton('选择路径')
        self.select_button.clicked.connect(self.select_directory)  # type: ignore

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)                 # 设置布局居中
        layout.addWidget(self.directory_label)              # 将标签控件添加到布局中
        layout.addWidget(self.selected_directory_label)     # 将标签控件添加到布局中
        layout.addWidget(self.select_button)                # 将按钮控件添加到布局中
        self.setLayout(layout)                              # 将布局应用到窗口中

    def select_directory(self):
        #  os.path.expanduser("~") 表示打开用户的主目录
        directory = QFileDialog.getExistingDirectory(self, "选择扫描路径", os.path.expanduser("~"))
        scanned_file = "scan_record.json"
        if directory:
            self.selected_directory_label.setText(directory)            # 将用户选择的文件夹路径显示在标签控件上
            project_root = os.path.dirname(os.path.abspath(__file__))
            # __file__表示当前脚本文件；os.path.abspath(__file__) 返回当前脚本文件的绝对路径，
            # os.path.dirname() 对这个路径进行处理，只保留其目录部分，去掉文件名部分，从而得到当前脚本文件所在的目录路径

            output_file = os.path.join(project_root, scanned_file)
            # 将扫描结果记录文件（scan_record.json）与其路径拼接，形成完整路径，以便后续调用scan_book_files()时可以将扫描结果写入文件
            self.scan_book_files(directory, output_file)                # 调用scan_book_files函数扫描文件夹中的电子书
        else:
            QMessageBox.warning(self, "提示", "未选择扫描路径！扫描已取消。", QMessageBox.Ok)
            self.close()

    def scan_book_files(self, directory, output_file):
        """
        扫描本地硬盘中的电子书，directory为待扫描文件所在路径；output_file为扫描记录的路径
        """
        global file_lists
        file_lists = []
        current_date = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')

        try:
            # os.walk函数将扫描的每个目录返回一个三元组，
            # 包含当前目录的路径（root），当前目录下的所有子目录名（dirs），以及当前目录下的所有文件名（files）
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.pdf', '.doc', '.docx', '.epub', '.txt')):
                        file_lists.append(os.path.join(root, file))
            with open(output_file, 'a') as o_file:
                for item in file_lists:
                    o_file.write(item + '\n')
                o_file.write(f" --- 本次扫描日期：{current_date} --- \n")

                # 显示询问弹窗，让用户决定是否继续扫描其他文件夹
                reply = QMessageBox.question(None, "提示", "扫描完成！是否继续扫描其他文件夹？",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # 用户选择继续扫描，则再次调用select_directory()方法
                    scan_book_files.select_directory()
                else:
                    # 用户选择结束扫描，则显示提示信息
                    QMessageBox.information(None, "提示", "扫描已结束！", QMessageBox.Ok)
                    self.close()

        # 扫描遇到错误时执行以下语句
        except FileNotFoundError:
            QMessageBox.information(None, "提示", "系统找不到指定的路径，请重试。", QMessageBox.Ok)
        except PermissionError:
            QMessageBox.information(None, "提示", "扫描路径无访问权限，请检查路径权限。", QMessageBox.Ok)
        except Exception:
            QMessageBox.information(None, "提示", "遇到未知错误。", QMessageBox.Ok)
        else:
            return file_lists


class Books:
    """
    关于各种书籍的类，基本属性包括：书籍名称、作者、国籍、译者、出版单位、
    出版日期、评分（1至5⭐）、页数、书籍类型（专业书籍、其它专著、文学作品、课外读物）、ISBN码、
    阅读状态(尚未阅读、正在阅读、暂停阅读、阅读完成）、阅读进度、阅读时长、内容简介
    """

    def __init__(
            self,
            book_name, author, nationality="", translator="", publisher="", publication_date="", level="",
            read_status="", book_type="", isbn="", pages="", read_progress="", read_time="", read_date="",
            read_link="", introduction=""
    ):

        self.book_name = book_name
        self.author = author
        self.nationality = nationality
        self.translator = translator

        self.publisher = publisher
        self.publication_date = publication_date
        self.level = level
        self.read_status = read_status

        self.book_type = book_type
        self.isbn = isbn
        self.pages = pages
        self.read_progress = read_progress

        self.read_time = read_time  # 阅读时长（单位：小时）
        self.read_date = read_date
        self.read_link = read_link  # 第三方阅读器或书籍评分网站（如豆瓣读书）的网址链接
        self.introduction = introduction

    def level(self):
        """统计书籍的评分情况，以一到五个⭐表示，分别表示书籍由低到高的评价"""
        default_symbol = ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐']  # 默认评价图标
        custom_symbol = [self.level]  # 用户自定义图标

    def read_status(self):
        """统计书籍的阅读状态"""
        books_status = ['尚未阅读', '正在阅读', '暂停阅读', '阅读完成']
        if eval(self.read_progress) == 0:
            self.read_status = books_status[0]  # 将阅读状态设置为“尚未阅读”
        elif eval(self.read_progress) == 100:
            self.read_status = books_status[-1]  # 将阅读状态设置为“阅读完成”
        else:
            self.read_status = input()  # 由用户从给定的列表中选择阅读状态
            books_status.append(self.read_status)
            print(books_status)

    def reading_time(self):
        """统计书籍的阅读时长，包括阅读的天数、阅读的小时数（可切换为x时x分的格式）"""
        # 计算阅读天数
        total_read_days = 0
        add_date = datetime.datetime.now()  # 添加书籍到书库时获取的系统日期
        open_time = time.time()  # 每次阅读书籍时获取的系统时间
        # 此处执行打开书籍文件的操作
        reading_date = datetime.datetime.now()  # 当前阅读时获取的系统日期,标记为“阅读完成”时则表示最后一次阅读的日期
        if self.read_status == "阅读完成":
            total_read_days = reading_date - add_date  # 计算总的阅读天数
            print(f"阅读天数：{total_read_days.days}天")
        else:
            print("书籍尚未阅读完成！请继续加油！")

        close_time = time.time()  # 每次关闭书籍时获取的系统时间
        read_date = datetime.datetime.now()  # 每次阅读时获取的系统日期

        # 每次阅读时间>=10秒时，阅读天数+1，否则不变
        if close_time - open_time >= 10:
            total_read_days += 1
        else:
            total_read_days += 0

    def book_animation(self):
        """控制电子书打开、关闭、翻页时的动画效果"""
        pass


class PDFBooks(Books):
    """Books的子类：pdf格式电子书"""

    def __init__(
            self,
            book_name, author, nationality="", translator="", publisher="", publication_date="", level="",
            read_status="", book_type="", isbn="", pages="", read_progress="", read_time="", read_date="",
            read_link="", introduction=""
    ):
        super().__init__(
            book_name, author, nationality, translator, publisher, publication_date, level,
            read_status, book_type, isbn, pages, read_progress, read_time, read_date,
            read_link, introduction
        )

    def get_pdf_path(self):
        """获取pdf文件的路径"""
        with open("scan_record.json") as files:
            for file in files:
                return file

    def get_pdf_character(self):
        """获取pdf文件每页的文字"""
        get_path = self.get_pdf_path()  # 获取pdf文件的路径
        pdf_doc = fitz.open(get_path)
        for page in pdf_doc:
            text = page.get_text()
            print(text)


class TxtBooks(Books):
    """Books的子类：txt格式电子书"""

    def __init__(
            self,
            book_name, author, nationality="", translator="", publisher="", publication_date="", level="",
            read_status="", book_type="", isbn="", pages="", read_progress="", read_time="", read_date="",
            read_link="", introduction=""
    ):
        super().__init__(
            book_name, author, nationality, translator, publisher, publication_date, level,
            read_status, book_type, isbn, pages, read_progress, read_time, read_date,
            read_link, introduction
        )

    def edit_txt(self):
        """对txt格式的书籍内容进行编辑"""
        pass


class EpubBooks(Books):
    """Books的子类：epub格式电子书"""

    def __init__(
            self,
            book_name, author, nationality="", translator="", publisher="", publication_date="", level="",
            read_status="", book_type="", isbn="", pages="", read_progress="", read_time="", read_date="",
            read_link="", introduction=""
    ):
        super().__init__(
            book_name, author, nationality, translator, publisher, publication_date, level,
            read_status, book_type, isbn, pages, read_progress, read_time, read_date,
            read_link, introduction
        )

    def edit_epub(self):
        """对epub格式的书籍内容进行编辑"""


if __name__ == '__main__':
    book = Books(
        "Python编程：从入门到实践",
        "Eric Matthews",
    )
    app = QApplication(sys.argv)  # 创建PyQt应用程序，sys.argv用于获取当前正在执行的命令行参数的参数列表
    scan_book_files = ScanBookFiles()
    scan_book_files.select_directory()
    scan_book_files.show()  # 显示窗口
    sys.exit(app.exec_())
