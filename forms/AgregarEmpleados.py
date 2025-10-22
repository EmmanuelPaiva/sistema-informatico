# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormularioClientes.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(805, 245)
        Form.setMinimumSize(QSize(805, 0))
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEditNombre = QLineEdit(Form)
        self.lineEditNombre.setObjectName(u"lineEditNombre")

        self.gridLayout.addWidget(self.lineEditNombre, 0, 1, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.lineEditTelefono = QLineEdit(Form)
        self.lineEditTelefono.setObjectName(u"lineEditTelefono")

        self.gridLayout.addWidget(self.lineEditTelefono, 1, 1, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.lineEditRuc_Ci = QLineEdit(Form)
        self.lineEditRuc_Ci.setObjectName(u"lineEditRuc_Ci")

        self.gridLayout.addWidget(self.lineEditRuc_Ci, 0, 3, 1, 2)

        self.pushButtonAceptar = QPushButton(Form)
        self.pushButtonAceptar.setObjectName(u"pushButtonAceptar")
        self.pushButtonAceptar.setProperty("type", "primary")

        self.gridLayout.addWidget(self.pushButtonAceptar, 2, 3, 1, 1)

        self.lineEditCorreo = QLineEdit(Form)
        self.lineEditCorreo.setObjectName(u"lineEditCorreo")

        self.gridLayout.addWidget(self.lineEditCorreo, 1, 3, 1, 2)

        self.labelRuc_Ci = QLabel(Form)
        self.labelRuc_Ci.setObjectName(u"labelRuc_Ci")

        self.gridLayout.addWidget(self.labelRuc_Ci, 0, 2, 1, 1)

        self.labelCorreo = QLabel(Form)
        self.labelCorreo.setObjectName(u"labelCorreo")

        self.gridLayout.addWidget(self.labelCorreo, 1, 2, 1, 1)

        self.pushButtonCancelar = QPushButton(Form)
        self.pushButtonCancelar.setObjectName(u"pushButtonCancelar")
        self.pushButtonCancelar.setProperty("type", "secondary")

        self.gridLayout.addWidget(self.pushButtonCancelar, 2, 4, 1, 1)

        self.labelNombre = QLabel(Form)
        self.labelNombre.setObjectName(u"labelNombre")

        self.gridLayout.addWidget(self.labelNombre, 0, 0, 1, 1)

        self.labelTelefono = QLabel(Form)
        self.labelTelefono.setObjectName(u"labelTelefono")

        self.gridLayout.addWidget(self.labelTelefono, 1, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.lineEditNombre.setText(QCoreApplication.translate("Form", u"Ingresar Nombre", None))
        self.lineEditTelefono.setText("")
        self.lineEditRuc_Ci.setText(QCoreApplication.translate("Form", u"Ingresar RUC o CI", None))
        self.pushButtonAceptar.setText(QCoreApplication.translate("Form", u"Aceptar", None))
        self.labelRuc_Ci.setText(QCoreApplication.translate("Form", u"RUC/CI", None))
        self.labelCorreo.setText(QCoreApplication.translate("Form", u"Correo", None))
        self.pushButtonCancelar.setText(QCoreApplication.translate("Form", u"Cancelar", None))
        self.labelNombre.setText(QCoreApplication.translate("Form", u"Nombre", None))
        self.labelTelefono.setText(QCoreApplication.translate("Form", u"Telefono", None))
    # retranslateUi

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
    
