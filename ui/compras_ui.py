# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compras.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(868, 646)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_4 = QFrame(Form)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMaximumSize(QSize(16777215, 16777215))
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_4)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.gridLayout.addWidget(self.frame_4, 2, 0, 2, 1)

        self.frame_3 = QFrame(Form)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMaximumSize(QSize(16777215, 60))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButtonNuevaCompra = QPushButton(self.frame_3)
        self.pushButtonNuevaCompra.setObjectName(u"pushButtonNuevaCompra")

        self.gridLayout_2.addWidget(self.pushButtonNuevaCompra, 0, 1, 1, 1)

        self.pushButtonExportar = QPushButton(self.frame_3)
        self.pushButtonExportar.setObjectName(u"pushButtonExportar")

        self.gridLayout_2.addWidget(self.pushButtonExportar, 1, 1, 1, 1)

        self.labelCompras = QLabel(self.frame_3)
        self.labelCompras.setObjectName(u"labelCompras")

        self.gridLayout_2.addWidget(self.labelCompras, 0, 0, 2, 1)


        self.gridLayout.addWidget(self.frame_3, 1, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButtonNuevaCompra.setText(QCoreApplication.translate("Form", u"Nueva compra", None))
        self.pushButtonExportar.setText(QCoreApplication.translate("Form", u"Exportar", None))
        self.labelCompras.setText(QCoreApplication.translate("Form", u"Compras", None))
    # retranslateUi

