# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Clientes.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QTableView,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(917, 408)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.pushButton_2 = QPushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout.addWidget(self.frame)

        self.tableView = QTableView(Form)
        self.tableView.setObjectName(u"tableView")

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Cientes", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Buscar", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Agregar cliente", None))
    # retranslateUi

from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from Clientes import Ui_Form

class VentanaClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.conectar_db()
        self.configurar_tabla()

        self.ui.pushButton.clicked.connect(self.agregar_cliente)

    def conectar_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("clientes.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos.")
            exit()

        # Crear tabla si no existe
        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                apellido TEXT,
                ruc TEXT,
                celular TEXT,
                correo TEXT,
                direccion TEXT
            )
        """)

    def configurar_tabla(self):
        self.modelo = QSqlTableModel(self)
        self.modelo.setTable("clientes")
        self.modelo.select()
        self.ui.tableView.setModel(self.modelo)

    def agregar_cliente(self):
        nombre = self.ui.lineEdit_nombre.text()
        apellido = self.ui.lineEdit_apellido.text()
        ruc = self.ui.lineEdit_ruc.text()
        celular = self.ui.lineEdit_celular.text()
        correo = self.ui.lineEdit_correo.text()
        direccion = self.ui.lineEdit_direccion.text()

        if not nombre:
            QMessageBox.warning(self, "Validación", "El campo nombre es obligatorio.")
            return
    

        query = QSqlQuery()
        query.prepare("""
            INSERT INTO clientes (nombre, apellido, ruc, celular, correo, direccion)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        query.addBindValue(nombre)
        query.addBindValue(apellido)
        query.addBindValue(ruc)
        query.addBindValue(celular)
        query.addBindValue(correo)
        query.addBindValue(direccion)
        query.exec()

        self.modelo.select()  # Refrescar la tabla
        self.limpiar_campos()

    def limpiar_campos(self):
        self.ui.lineEdit_nombre.clear()
        self.ui.lineEdit_apellido.clear()
        self.ui.lineEdit_ruc.clear()
        self.ui.lineEdit_celular.clear()
        self.ui.lineEdit_correo.clear()
        self.ui.lineEdit_direccion.clear()

if __name__ == "__main__":
    app = QApplication([])
    ventana = VentanaClientes()
    ventana.show()
    app.exec()
