import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets



if __name__ == '__main__':
    app = QApplication(sys.argv)            # sys.argv用于获取当前正在执行的命令行参数的参数列表
    sys.exit(app.exec_())
