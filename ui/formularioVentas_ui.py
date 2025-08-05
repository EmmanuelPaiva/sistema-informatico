# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'formularioVentas.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateTimeEdit, QGridLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(285, 593)
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButtonQuitarProducto = QPushButton(self.widget)
        self.pushButtonQuitarProducto.setObjectName(u"pushButtonQuitarProducto")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        self.pushButtonQuitarProducto.setIcon(icon)

        self.gridLayout.addWidget(self.pushButtonQuitarProducto, 11, 0, 1, 1)

        self.labelPrecioTotal = QLabel(self.widget)
        self.labelPrecioTotal.setObjectName(u"labelPrecioTotal")

        self.gridLayout.addWidget(self.labelPrecioTotal, 12, 0, 1, 1)

        self.comboBox = QComboBox(self.widget)
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout.addWidget(self.comboBox, 1, 1, 1, 3)

        self.labelFecha = QLabel(self.widget)
        self.labelFecha.setObjectName(u"labelFecha")

        self.gridLayout.addWidget(self.labelFecha, 0, 0, 1, 1)

        self.lineEditPrecioTotal = QLineEdit(self.widget)
        self.lineEditPrecioTotal.setObjectName(u"lineEditPrecioTotal")

        self.gridLayout.addWidget(self.lineEditPrecioTotal, 12, 1, 1, 3)

        self.labelCliente = QLabel(self.widget)
        self.labelCliente.setObjectName(u"labelCliente")

        self.gridLayout.addWidget(self.labelCliente, 1, 0, 1, 1)

        self.pushButtonAgregarProducto = QPushButton(self.widget)
        self.pushButtonAgregarProducto.setObjectName(u"pushButtonAgregarProducto")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.pushButtonAgregarProducto.setIcon(icon1)

        self.gridLayout.addWidget(self.pushButtonAgregarProducto, 11, 1, 1, 1)

        self.dateTimeEditCliente = QDateTimeEdit(self.widget)
        self.dateTimeEditCliente.setObjectName(u"dateTimeEditCliente")

        self.gridLayout.addWidget(self.dateTimeEditCliente, 0, 1, 1, 3)

        self.pushButtonAceptar = QPushButton(self.widget)
        self.pushButtonAceptar.setObjectName(u"pushButtonAceptar")

        self.gridLayout.addWidget(self.pushButtonAceptar, 13, 1, 1, 1)

        self.pushButtonCancelar = QPushButton(self.widget)
        self.pushButtonCancelar.setObjectName(u"pushButtonCancelar")

        self.gridLayout.addWidget(self.pushButtonCancelar, 13, 2, 1, 2)

        self.tablaProductos = QTableWidget(self.widget)
        self.tablaProductos.setObjectName(u"tablaProductos")

        self.gridLayout.addWidget(self.tablaProductos, 2, 0, 1, 4)


        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButtonQuitarProducto.setText("")
        self.labelPrecioTotal.setText(QCoreApplication.translate("Form", u"Precio total", None))
        self.labelFecha.setText(QCoreApplication.translate("Form", u"Fecha", None))
        self.labelCliente.setText(QCoreApplication.translate("Form", u"Cliente", None))
        self.pushButtonAgregarProducto.setText("")
        self.pushButtonAceptar.setText(QCoreApplication.translate("Form", u"Aceptar", None))
        self.pushButtonCancelar.setText(QCoreApplication.translate("Form", u"Cancelar", None))
    # retranslateUi

