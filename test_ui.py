import sys
import os

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListView,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(549, 271)
        self.horizontalLayout_2 = QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.btn_open = QPushButton(Form)
        self.btn_open.setObjectName(u"btn_open")

        self.verticalLayout_2.addWidget(self.btn_open)

        self.listView = QListView(Form)
        self.listView.setObjectName(u"listView")

        self.verticalLayout_2.addWidget(self.listView)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btn_add = QPushButton(Form)
        self.btn_add.setObjectName(u"btn_add")

        self.horizontalLayout.addWidget(self.btn_add)

        self.btn_insert = QPushButton(Form)
        self.btn_insert.setObjectName(u"btn_insert")

        self.horizontalLayout.addWidget(self.btn_insert)

        self.btn_delete = QPushButton(Form)
        self.btn_delete.setObjectName(u"btn_delete")

        self.horizontalLayout.addWidget(self.btn_delete)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listView_2 = QListView(Form)
        self.listView_2.setObjectName(u"listView_2")

        self.verticalLayout.addWidget(self.listView_2)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btn_open.setText(QCoreApplication.translate("Form", u"\u6253\u5f00", None))
        self.btn_add.setText(QCoreApplication.translate("Form", u"\u6dfb\u52a0", None))
        self.btn_insert.setText(QCoreApplication.translate("Form", u"\u63d2\u5165", None))
        self.btn_delete.setText(QCoreApplication.translate("Form", u"\u5220\u9664", None))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
