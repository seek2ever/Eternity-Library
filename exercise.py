import sys
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout,
                                QPushButton, QLineEdit)

class CalculatorDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('基础网格布局示例')

        # 1. 创建布局对象
        layout = QGridLayout()

        # 2. 创建一个显示框，放在第0行，横跨4列
        display = QLineEdit()
        display.setReadOnly(True)
        layout.addWidget(display, 0, 0, 1, 4)

        # 3. 按钮文本和位置 (行, 列)
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            layout.addWidget(button, row, col)

        # 4. 将布局设置为窗口的主布局
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorDemo()
    window.show()
    sys.exit(app.exec())