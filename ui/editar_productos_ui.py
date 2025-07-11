# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editar_productos.ui'
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
        Form.resize(723, 106)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelNombre = QLabel(Form)
        self.labelNombre.setObjectName(u"labelNombre")

        self.gridLayout.addWidget(self.labelNombre, 0, 0, 1, 1)

        self.lineEditNombre = QLineEdit(Form)
        self.lineEditNombre.setObjectName(u"lineEditNombre")

        self.gridLayout.addWidget(self.lineEditNombre, 0, 1, 1, 1)

        self.labelPrecio = QLabel(Form)
        self.labelPrecio.setObjectName(u"labelPrecio")

        self.gridLayout.addWidget(self.labelPrecio, 0, 2, 1, 1)

        self.lineEditPrecio = QLineEdit(Form)
        self.lineEditPrecio.setObjectName(u"lineEditPrecio")

        self.gridLayout.addWidget(self.lineEditPrecio, 0, 3, 1, 1)

        self.labelStock = QLabel(Form)
        self.labelStock.setObjectName(u"labelStock")

        self.gridLayout.addWidget(self.labelStock, 0, 4, 1, 1)

        self.lineEditStock = QLineEdit(Form)
        self.lineEditStock.setObjectName(u"lineEditStock")

        self.gridLayout.addWidget(self.lineEditStock, 0, 5, 1, 2)

        self.labelDescripcion = QLabel(Form)
        self.labelDescripcion.setObjectName(u"labelDescripcion")

        self.gridLayout.addWidget(self.labelDescripcion, 1, 0, 1, 1)

        self.lineEditDescripcion = QLineEdit(Form)
        self.lineEditDescripcion.setObjectName(u"lineEditDescripcion")

        self.gridLayout.addWidget(self.lineEditDescripcion, 1, 1, 1, 6)

        self.labelProveedor = QLabel(Form)
        self.labelProveedor.setObjectName(u"labelProveedor")

        self.gridLayout.addWidget(self.labelProveedor, 2, 0, 1, 1)

        self.comboBoxProveedor = QComboBox(Form)
        self.comboBoxProveedor.setObjectName(u"comboBoxProveedor")

        self.gridLayout.addWidget(self.comboBoxProveedor, 2, 1, 1, 1)

        self.pushButtonGC = QPushButton(Form)
        self.pushButtonGC.setObjectName(u"pushButtonGC")

        self.gridLayout.addWidget(self.pushButtonGC, 2, 4, 1, 2)

        self.pushButtonCancelar = QPushButton(Form)
        self.pushButtonCancelar.setObjectName(u"pushButtonCancelar")

        self.gridLayout.addWidget(self.pushButtonCancelar, 2, 6, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.labelNombre.setText(QCoreApplication.translate("Form", u"Nombre:", None))
        self.labelPrecio.setText(QCoreApplication.translate("Form", u"Precio:", None))
        self.labelStock.setText(QCoreApplication.translate("Form", u"Stock:", None))
        self.labelDescripcion.setText(QCoreApplication.translate("Form", u"Descripcion:", None))
        self.labelProveedor.setText(QCoreApplication.translate("Form", u"Proveedor", None))
        self.pushButtonGC.setText(QCoreApplication.translate("Form", u"Guardar cambios", None))
        self.pushButtonCancelar.setText(QCoreApplication.translate("Form", u"Cancelar", None))
    # retranslateUi

