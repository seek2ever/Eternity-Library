# 用于实现pdf编辑、转换、合并、提取、压缩等操作

import fitz


def get_pdf_path(self):
    """获取pdf文件的路径"""
    with open("scan_record.json") as files:
        for file in files:
            return file


class PDFEdit:
    def get_pdf_character(self):
        """获取pdf文件每页的文字"""
        get_path = self.get_pdf_path()  # 获取pdf文件的路径
        pdf_doc = fitz.open(get_path)
        for page in pdf_doc:
            text = page.get_text()
            print(text)
