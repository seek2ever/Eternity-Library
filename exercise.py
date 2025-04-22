import sys

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QApplication, QVBoxLayout, QPushButton, QDesktopWidget, \
    QLabel, QHBoxLayout
from PyQt5.QtCore import Qt


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("click to jump")
        self.setGeometry(1000, 500, 500, 300)

        self.push_button = QPushButton("click to jump", self)
        self.push_button.clicked.connect(self.jump)
        self.push_button.setFixedSize(200, 100)

        self.userLabel = QLabel()
        self.userLabel.setAlignment(Qt.AlignCenter)
        self.userLabel.setFixedSize(150, 150)
        self.userLabel.setText("<a href='https://www.baidu.com'>百度一下</a>")
        self.userLabel.setOpenExternalLinks(True)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.userLabel)
        hLayout.addWidget(self.push_button)

        self.layout = QVBoxLayout()
        self.layout.addLayout(hLayout)

        mainLayout = QWidget()
        mainLayout.setLayout(self.layout)
        self.setCentralWidget(mainLayout)

        screen = QDesktopWidget().screenGeometry()
    def jump(self):
        QMessageBox.information(self, "提示", "成功点击！")


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
