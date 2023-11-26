import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel,
                             QLineEdit, QMessageBox, QPushButton)
from PyQt5.QtCore import QCoreApplication


"""
本模块代码来自知乎：https://zhuanlan.zhihu.com/p/52920094，实现登录窗口的简单功能
"""

# 主窗体
app = QApplication(sys.argv)  # 创建应用对象
LoginWindow = QWidget()  # 构造登陆窗口
LoginWindow.setWindowTitle('登陆窗口')  # 窗口标题
LoginWindow.resize(300, 180)  # 窗口大小

# 姓名Label
name_Label = QLabel(LoginWindow)  # 放置在登陆窗口上
name_Label.setText('姓名')  # 设置显示文本
name_Label.move(60, 40)  # 设置位置

# 输入姓名文本框
name_Edit = QLineEdit(LoginWindow)  # 放置在登陆窗口上
name_Edit.move(100, 36)  # 设置位置

# 密码Label
pass_Label = QLabel(LoginWindow)  # 放置在登陆窗口上
pass_Label.setText('密码')  # 设置显示文本
pass_Label.move(60, 80)  # 设置位置

# 输入密码文本框
pass_Edit = QLineEdit(LoginWindow)  # 放置在登陆窗口上
pass_Edit.move(100, 76)  # 设置位置
pass_Edit.setEchoMode(QLineEdit.Password)  # 设置输入密码不可见


# 登陆函数
def end_event():
    if name_Edit.text() == "":
        QMessageBox.about(LoginWindow, '登陆', '请输入姓名')
    elif pass_Edit.text() == "":
        QMessageBox.about(LoginWindow, '登陆', '请输入密码')
    else:
        QMessageBox.about(LoginWindow, '登陆', name_Edit.text() + ' 欢迎登陆')


# 登陆按钮
end_Btn = QPushButton('登陆', LoginWindow)
end_Btn.clicked.connect(end_event)  # 绑定登陆函数
end_Btn.move(60, 120)

# 退出按钮
exit_Btn = QPushButton('退出', LoginWindow)
exit_Btn.clicked.connect(QCoreApplication.instance().quit)  # 绑定退出事件
exit_Btn.move(160, 120)

LoginWindow.show()  # 显示窗口
sys.exit(app.exec_())  # 进入消息循环
