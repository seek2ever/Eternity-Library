import os
import sys
import time
import datetime
from typing import List, Union
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt


class ScanBookFiles(QWidget):
    """
    选择扫描路径的窗口，用户可以通过点击按钮选择扫描文件所在的路径，
    该窗口还会调用scan_book_files函数扫描文件夹中的电子书，并将结果写入文本文件
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('扫描路径')
        self.setGeometry(100, 100, 400, 200)

        self.directory_label = QLabel('请选择扫描路径：')
        self.selected_directory_label = QLabel("")

        self.select_button = QPushButton('选择路径')
        self.select_button.clicked.connect(self.select_directory)       # type: ignore

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.directory_label)
        layout.addWidget(self.selected_directory_label)
        layout.addWidget(self.select_button)
        self.setLayout(layout)

    def select_directory(self):
        #  os.path.expanduser("~") 表示打开用户的主目录
        directory = QFileDialog.getExistingDirectory(self, "选择扫描路径", os.path.expanduser("~"))
        if directory:
            self.selected_directory_label.setText(directory)  # 将用户选择的文件夹路径显示在标签控件上
            project_root = os.path.dirname(os.path.abspath(__file__))           # 获取项目的根目录路径
            output_file = os.path.join(project_root, 'scanned_record.txt')      # 将扫描结果写入scanned_file.txt
            self.scan_book_files(directory, output_file)
        else:
            QMessageBox.warning(self, "提示", "未选择路径！扫描已取消。", QMessageBox.Ok)

    def scan_book_files(self, directory: str, output_file: str):
        """
        扫描本地硬盘中的电子书，directory为待扫描文件所在路径；output_file为扫描记录的路径
        """
        pdf_lists: List[Union[str, bytes]] = []     # 本行类型提示详细解释见Notion相关页面
        current_date = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        try:
            # os.walk函数将扫描的每个目录返回一个三元组，
            # 包含当前目录的路径（root），当前目录下的所有子目录名（dirs），以及当前目录下的所有文件名（files）
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.pdf', '.doc', '.docx', '.epub', '.txt')):
                        pdf_lists.append(os.path.join(root, file))
            with open(output_file, 'a') as file:
                for item in pdf_lists:
                    file.write(item + '\n')
                file.write(f" --- 本次扫描日期：{current_date} --- \n")

                # 显示询问弹窗，让用户决定是否继续扫描其他文件夹
                reply = QMessageBox.question(None, "提示", "扫描完成！是否继续扫描其他文件夹？",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # 用户选择继续扫描，则递归调用自身，并传入新的文件夹路径
                    new_directory = QFileDialog.getExistingDirectory(None, "选择扫描路径", os.path.expanduser("~"))
                    if new_directory:
                        ScanBookFiles.scan_book_files(new_directory, output_file)
                else:
                    # 用户选择结束扫描，则显示提示信息
                    QMessageBox.information(None, "提示", "扫描已结束！", QMessageBox.Ok)
        except Exception as e:      # Exception是所有异常的基类，它代表了所有常见的错误类型
            print(f"在扫描文件时发生错误: {e}")


class Books:
    """
    关于各种书籍的类，基本属性包括：书籍名称、作者、国籍、译者、出版单位、
    出版日期、评分（1至5⭐）、页数、书籍类型（专业书籍、其它专著、文学作品、课外读物）、ISBN码、
    阅读状态(尚未阅读、正在阅读、暂停阅读、阅读完成）、阅读进度、阅读时长、内容简介
    """

    def __init__(
            self,
            book_name, author,
            nationality="", translator="",
            publisher="", publication_date="",
            level="", read_status="",
            book_type="", isbn="",
            pages="", read_progress="",
            read_time="", read_date="",
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
        self.read_time = read_time             # 阅读时长（单位：小时）
        self.read_date = read_date
        self.read_link = read_link            # 第三方阅读器或书籍评分网站（如豆瓣读书）的网址链接
        self.introduction = introduction

        print(f"书籍名称：{self.book_name}\n作者：{self.author}\n出版社：{self.publisher}\n评分：{self.level}")

    def level(self):
        """统计书籍的评分情况，以一到五个⭐表示，分别表示书籍由低到高的评价"""
        level_symbol = ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐']
        set_level = input()

    def read_status(self):
        """统计书籍的阅读状态"""
        books_status = ['尚未阅读', '正在阅读', '暂停阅读', '阅读完成']
        if eval(self.read_progress) == 0:
            self.read_status = books_status[0]  # 将阅读状态设置为“尚未阅读”
        elif eval(self.read_progress) == 100:
            self.read_status = books_status[-1]  # 将阅读状态设置为“阅读完成”
        else:
            self.read_status = input()  # 由用户从给定的列表中选择阅读状态

    def read_duration(self):
        """统计书籍的阅读时长，包括阅读的天数、阅读的小时数（可切换为x时x分的格式）"""
        add_time = time.time()  # 添加书籍到书库时获取的系统时间
        last_time = time.time()  # 最后一次阅读书籍或书籍标记为“阅读完成”时获取的系统时间
        open_time = time.time()  # 每次阅读书籍时获取的系统时间
        # 此处执行打开书籍文件的操作
        close_time = time.time()  # 每次关闭书籍时获取的系统时间

    def book_animation(self):
        """控制电子书打开、关闭、翻页时的动画效果"""
        pass


class PDFBooks(Books):
    """Books的子类：pdf格式电子书"""
    def __init__(
            self,
            book_name, author,
            nationality="", translator="",
            publisher="", publication_date="",
            level="", read_status="",
            book_type="", isbn="",
            pages="", read_progress="",
            read_time="", read_date="",
            read_link="", introduction=""
            ):
        super().__init__(
            book_name, author,
            nationality, translator,
            publisher, publication_date,
            level, read_status,
            book_type, isbn,
            pages, read_progress,
            read_time, read_date,
            read_link, introduction
            )

    def edit_pdf(self):
        """对pdf格式的书籍进行编辑"""
        pass


class TxtBooks(Books):
    """Books的子类：txt格式电子书"""
    def __init__(
            self,
            book_name, author,
            nationality="", translator="",
            publisher="", publication_date="",
            level="", read_status="",
            book_type="", isbn="",
            pages="", read_progress="",
            read_time="", read_date="",
            read_link="", introduction=""
            ):
        super().__init__(
            book_name, author,
            nationality, translator,
            publisher, publication_date,
            level, read_status,
            book_type, isbn,
            pages, read_progress,
            read_time, read_date,
            read_link, introduction
            )

    def edit_txt(self):
        """对txt格式的书籍内容进行编辑"""
        pass


class EpubBooks(Books):
    """Books的子类：epub格式电子书"""
    def __init__(
            self,
            book_name, author,
            nationality="", translator="",
            publisher="", publication_date="",
            level="", read_status="",
            book_type="", isbn="",
            pages="", read_progress="",
            read_time="", read_date="",
            read_link="", introduction=""
            ):
        super().__init__(
            book_name, author,
            nationality, translator,
            publisher, publication_date,
            level, read_status,
            book_type, isbn,
            pages, read_progress,
            read_time, read_date,
            read_link, introduction
            )

    def edit_epub(self):
        """对epub格式的书籍内容进行编辑"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scan_book_files = ScanBookFiles()
    scan_book_files.show()
    sys.exit(app.exec_())
