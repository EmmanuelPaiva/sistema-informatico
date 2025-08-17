# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ventas.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableView,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(653, 475)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 2, 0, 1, 1)

        self.pushButton_3 = QPushButton(Form)
        self.pushButton_3.setObjectName(u"pushButton_3")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.AddressBookNew))
        self.pushButton_3.setIcon(icon)

        self.gridLayout.addWidget(self.pushButton_3, 2, 2, 1, 1)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 0, 3, 1, 1)

        self.tableView = QTableView(Form)
        self.tableView.setObjectName(u"tableView")

        self.gridLayout.addWidget(self.tableView, 3, 0, 1, 4)

        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 2, 3, 1, 1)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.lineEdit.setText(QCoreApplication.translate("Form", u"Buscar venta", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"FIltrar", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Nueva venta", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Exportar", None))
        self.label.setText(QCoreApplication.translate("Form", u"Ventas", None))
    # retranslateUi

