# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'agregarProductos.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(698, 282)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEditStock = QLineEdit(Form)
        self.lineEditStock.setObjectName(u"lineEditStock")

        self.gridLayout.addWidget(self.lineEditStock, 2, 1, 1, 3)

        self.lineEditDescripcion = QLineEdit(Form)
        self.lineEditDescripcion.setObjectName(u"lineEditDescripcion")

        self.gridLayout.addWidget(self.lineEditDescripcion, 1, 3, 1, 4)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 3, 6, 1, 1)

        self.labelPrecio = QLabel(Form)
        self.labelPrecio.setObjectName(u"labelPrecio")

        self.gridLayout.addWidget(self.labelPrecio, 0, 0, 1, 2)

        self.labelNombre = QLabel(Form)
        self.labelNombre.setObjectName(u"labelNombre")

        self.gridLayout.addWidget(self.labelNombre, 0, 5, 1, 1)

        self.lineEditPrecio = QLineEdit(Form)
        self.lineEditPrecio.setObjectName(u"lineEditPrecio")

        self.gridLayout.addWidget(self.lineEditPrecio, 0, 2, 1, 2)

        self.labelProveedor = QLabel(Form)
        self.labelProveedor.setObjectName(u"labelProveedor")

        self.gridLayout.addWidget(self.labelProveedor, 2, 5, 1, 1)

        self.labelDescripcion = QLabel(Form)
        self.labelDescripcion.setObjectName(u"labelDescripcion")

        self.gridLayout.addWidget(self.labelDescripcion, 1, 0, 1, 3)

        self.lineEditNombre = QLineEdit(Form)
        self.lineEditNombre.setObjectName(u"lineEditNombre")

        self.gridLayout.addWidget(self.lineEditNombre, 0, 6, 1, 1)

        self.comboBoxProveedore = QComboBox(Form)
        self.comboBoxProveedore.setObjectName(u"comboBoxProveedore")

        self.gridLayout.addWidget(self.comboBoxProveedore, 2, 6, 1, 1)

        self.labelStock = QLabel(Form)
        self.labelStock.setObjectName(u"labelStock")

        self.gridLayout.addWidget(self.labelStock, 2, 0, 1, 1)

        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 3, 2, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"PushButton", None))
        self.labelPrecio.setText(QCoreApplication.translate("Form", u"Precio", None))
        self.labelNombre.setText(QCoreApplication.translate("Form", u"Nombre", None))
        self.labelProveedor.setText(QCoreApplication.translate("Form", u"Proveedor", None))
        self.labelDescripcion.setText(QCoreApplication.translate("Form", u"Descripcion", None))
        self.labelStock.setText(QCoreApplication.translate("Form", u"Stock", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"PushButton", None))
    # retranslateUi

