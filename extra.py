import sys
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QWidget, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from random import randint


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMenuBar应用实例")
        self.setupUi()

    def setupUi(self):
        self.menubar = QMenuBar()
        # “文件”菜单
        self.file = self.menubar.addMenu("文件(&F)")
        self.file.addAction("新建")
        self.file.addAction("打开")
        self.file_close = self.file.addAction("关闭")
        self.file_close.triggered.connect(self.close)
        self.file.addAction("保存")
        self.file.addAction("另存为")
        self.file.addSeparator()
        self.file.addAction("设置")

        # “编辑”菜单
        self.edit = self.menubar.addMenu("编辑(&E)")
        self.edit_clear = self.edit.addAction("清空(&C)")
        self.edit.triggered.connect(self.judge_edit)

        self.menu_view = self.menubar.addMenu("视图(&V)")
        self.menu_view.addAction("放大(&I)")
        self.menu_view.addAction("缩小(&O)")

        self.menu_about = self.menubar.addMenu("关于(&A)")
        self.about_me = self.menu_about.addAction("关于本软件")
        self.about_me.triggered.connect(self.show_about)

        self.label = QLabel("学生考试成绩查询")
        self.label.setFont(QFont("Arial", 20))
        self.label.setAlignment(Qt.AlignCenter)
        self.name = QLineEdit()
        self.name.setPlaceholderText("请输入姓名...")
        self.test_num = QLineEdit()
        self.test_num.setPlaceholderText("请输入准考证号...")
        self.test_num.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.widget = QWidget()  # 仅作为QVBoxLayout的容器
        self.layout = QFormLayout()

        self.layout.addRow("姓名", self.name)
        self.layout.addRow("准考证号", self.test_num)

        self.btn_check = QPushButton("查询(&E)")
        self.btn_check.clicked.connect(self.show_add_result)
        self.btn_clear = QPushButton("清空(&C)")
        self.btn_clear.clicked.connect(self.clear_info)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.btn_check)
        self.btn_layout.addWidget(self.btn_clear)

        self.info_layout = QVBoxLayout(self.widget)
        self.info_layout.addWidget(self.label)
        self.info_layout.addLayout(self.layout)
        self.info_layout.addLayout(self.btn_layout)

        self.text_edit = QTextEdit()

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.widget, "信息输入")
        self.tab_widget.addTab(self.text_edit, "查询结果")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.menubar)
        self.main_layout.addWidget(self.tab_widget)
        self.setLayout(self.main_layout)

    def judge_edit(self, action):
        if action == self.edit_clear:
            self.clear_info()

    def show_add_result(self):
        name = self.name.text()
        chinese = randint(0, 100)
        math = randint(0, 100)
        english = randint(0, 100)
        self.text_edit.setText(
            f"{name}的考试成绩：\n语文 {chinese}，数学 {math}， 英语 {english}"
        )
        self.tab_widget.setCurrentIndex(1)  # 点击“查询”时自动切换到查询结果页面

    def show_about(self):
        QMessageBox.about(
            self,
            "QMenuBar、QTabWidget综合应用",
            "这是关于QMenuBar、QTabWidget综合应用的示例程序，目前还需完善。"
        )

    def clear_info(self):
        self.name.clear()
        self.test_num.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
