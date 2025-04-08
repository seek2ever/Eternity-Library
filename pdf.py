# 用于实现pdf编辑、转换、合并、提取、压缩等操作
import os
import fitz
from database import DatabaseManager


def get_pdf_path(book_name: str):
    """
    获取pdf文件的路径
    :param book_name: 需要获取路径的书籍名称
    """
    path = DatabaseManager()
    file_path = path.get_book(book_name, columns='book_path')  # 获取pdf文件的路径
    return file_path


class PDFEdit:
    def get_pdf_character(self, book_name: str):
        """获取pdf文件每页的文字"""
        get_path = get_pdf_path(book_name)
        pdf_doc = fitz.open(get_path)
        full_text = ""  # 初始化一个空字符串来存储所有文本
        for page in pdf_doc:
            text = page.get_text()
            full_text += text  # 累加每一页的文本
        return full_text  # 返回所有文本


if __name__ == '__main__':
    test_2 = PDFEdit().get_pdf_character('test_file.pdf')
    print(test_2)
