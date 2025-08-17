# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Proveedores.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(939, 672)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_4 = QFrame(Form)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMaximumSize(QSize(16777215, 16777215))
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.treeWidget = QTreeWidget(self.frame_4)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setColumnCount(0)

        self.verticalLayout_2.addWidget(self.treeWidget)


        self.gridLayout.addWidget(self.frame_4, 1, 0, 2, 1)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.frame, 3, 0, 1, 1)

        self.frame_3 = QFrame(Form)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMaximumSize(QSize(16777215, 60))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_11 = QLabel(self.frame_3)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)

        self.lineEdit = QLineEdit(self.frame_3)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout_2.addWidget(self.lineEdit, 1, 0, 1, 1)

        self.pushButton = QPushButton(self.frame_3)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_2.addWidget(self.pushButton, 1, 1, 1, 1)


        self.gridLayout.addWidget(self.frame_3, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_11.setText(QCoreApplication.translate("Form", u"Proveedores", None))
        self.lineEdit.setText(QCoreApplication.translate("Form", u"Buscar proveedores", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Agregar Proveedor", None))
    # retranslateUi

