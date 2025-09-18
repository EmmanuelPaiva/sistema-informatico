# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'agregarProductos.ui'
## Created by: Qt User Interface Compiler version 6.9.0
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

        self.lineEditTelefono = QLineEdit(Form)
        self.lineEditTelefono.setObjectName(u"lineEditTelefono")
        self.gridLayout.addWidget(self.lineEditTelefono, 1, 1, 1, 3)

        self.lineEditCorreo = QLineEdit(Form)
        self.lineEditCorreo.setObjectName(u"lineEditCorreo")
        self.gridLayout.addWidget(self.lineEditCorreo, 1, 6, 1, 2)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.gridLayout.addWidget(self.pushButton, 3, 6, 1, 1)

        self.labelNombre = QLabel(Form)
        self.labelNombre.setObjectName(u"labelNombre")
        self.gridLayout.addWidget(self.labelNombre, 0, 0, 1, 2)

        self.labelDireccion = QLabel(Form)
        self.labelDireccion.setObjectName(u"labelDireccion")
        self.gridLayout.addWidget(self.labelDireccion, 0, 5, 1, 1)

        # --- CORREGIDO: ubicaciones de los QLineEdit para que coincidan con sus labels ---
        self.lineEditNombre = QLineEdit(Form)
        self.lineEditNombre.setObjectName(u"lineEditNombre")
        # Nombre debe ir al lado de labelNombre
        self.gridLayout.addWidget(self.lineEditNombre, 0, 2, 1, 2)

        self.lineEditDireccion = QLineEdit(Form)
        self.lineEditDireccion.setObjectName(u"lineEditDireccion")
        # Dirección debe ir al lado de labelDireccion
        self.gridLayout.addWidget(self.lineEditDireccion, 0, 6, 1, 1)
        # -------------------------------------------------------------------------------

        self.labelCorreo = QLabel(Form)
        self.labelCorreo.setObjectName(u"labelCorreo")
        self.gridLayout.addWidget(self.labelCorreo, 1, 4, 1, 2)

        self.labelTelefono = QLabel(Form)
        self.labelTelefono.setObjectName(u"labelTelefono")
        self.gridLayout.addWidget(self.labelTelefono, 1, 0, 1, 1)

        self.pushButtonCancelar = QPushButton(Form)
        self.pushButtonCancelar.setObjectName(u"pushButtonCancelar")
        self.gridLayout.addWidget(self.pushButtonCancelar, 3, 2, 1, 1)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

        Form.setStyleSheet("""
        QWidget {
            background-color: #fafafa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 15px;
            color: #2c3e50;
        }
        QLabel { font-weight: 600; margin-bottom: 4px; }
        QLineEdit, QComboBox {
            border: 1.8px solid #bdc3c7;
            border-radius: 8px;
            padding: 6px 10px;
            background-color: #ffffff;
            selection-background-color: #3498db;
            selection-color: white;
            transition: border-color 0.3s ease;
        }
        QLineEdit:focus, QComboBox:focus { border-color: #2980b9; background-color: #ecf6fc; }
        QPushButton {
            background-color: #2980b9; color: white; border-radius: 10px;
            padding: 8px 18px; font-weight: 700; min-width: 100px; border: none; cursor: pointer;
            transition: background-color 0.3s ease;
        }
        QPushButton:hover { background-color: #3498db; }
        QPushButton:pressed { background-color: #1f618d; }
        QGridLayout { spacing: 12px; }
        """)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Aceptar", None))
        self.labelNombre.setText(QCoreApplication.translate("Form", u"Nombre", None))
        self.labelDireccion.setText(QCoreApplication.translate("Form", u"Direccion", None))
        self.labelCorreo.setText(QCoreApplication.translate("Form", u"Correo", None))
        self.labelTelefono.setText(QCoreApplication.translate("Form", u"Telefono", None))
        self.pushButtonCancelar.setText(QCoreApplication.translate("Form", u"Cancelar", None))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
