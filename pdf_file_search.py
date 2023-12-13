# 本模块代码用于扫描本地硬盘中的pdf文件，代码由Copilot生成
import os
from typing import List, Union


def find_pdf_files(directory):
    pdf_lists: list[Union[str, bytes]] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pdf'):
                pdf_lists.append(os.path.join(root, file))
    return pdf_lists


file_path = 'E:\\History\\新疆'  # 切换为想要搜索的目录，注意不要缺少反斜杠（'\'）
pdf_files = find_pdf_files(file_path)

for pdf_file in pdf_files:
    print(pdf_file)
