# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, Qt, QMetaObject, QPropertyAnimation, QRect, QEvent, QObject)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel, QLineEdit,
                               QPushButton, QTreeWidget, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QTableWidget, QHeaderView)
from forms.agregarProveedor import  Ui_Form as FormularioProv
from db.prov_queries import guardar_registro

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(939, 672)
        Form.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: Arial;
            }
            QLineEdit {
                border: none;
                border-bottom: 2px solid #00bcd4;
                padding: 4px;
                color: #333;
                min-height: 30px;
                font-size: 14px;
            }
            QLineEdit:focus {
                color: #000;
            }
            QPushButton {
                background-color: #00bcd4;
                color: white;
                padding: 8px 16px;
                min-height: 22px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00acc1;
            }
            QLabel {
                color: #00bcd4;
                font-weight: bold;
                font-size: 18px;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                background-color: #f9f9f9;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #00bcd4;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setSpacing(10)

        # ---- Header ----
        self.header_frame = QFrame(Form)
        self.header_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.header_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.header_layout = QVBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(15)

        # Title
        self.label_title = QLabel(self.header_frame)
        self.label_title.setText("Proveedores")
        self.header_layout.addWidget(self.label_title)

        # Search + Button aligned
        self.search_layout = QHBoxLayout()
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_layout.setSpacing(10)

        self.lineEdit = QLineEdit(self.header_frame)
        self.lineEdit.setPlaceholderText("Buscar proveedor")
        self.lineEdit.setMinimumWidth(int(Form.width() * 0.5))
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_layout.addWidget(self.lineEdit)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.search_layout.addWidget(spacer)


        self.newButton = QPushButton(self.header_frame)
        self.newButton.setText("Nuevo proveedor")
        self.newButton.setFixedWidth(150)
        self.newButton.setMinimumHeight(22)   
        self.search_layout.addWidget(self.newButton)
        self.newButton.clicked.connect(lambda: self.abrir_formulario(Form))
        


        self.header_layout.addLayout(self.search_layout)
        self.gridLayout.addWidget(self.header_frame, 0, 0, 1, 1)

        # ---- Table ----
        self.table_frame = QFrame(Form)
        self.table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.table_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout = QVBoxLayout(self.table_frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.tableWidget = QTableWidget(self.table_frame)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Email", "Dirección"])
        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(True)
        for col in range(self.tableWidget.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        self.verticalLayout.addWidget(self.tableWidget)

        self.gridLayout.addWidget(self.table_frame, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Proveedores", None))
        
    def cancelar(self, Form):
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            self.formularioProveedor.close()
        
        
    def abrir_formulario(self, Form):
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            return

        self.ui_nuevo_proveedor = FormularioProv()
        self.formularioProveedor = QWidget()
        self.ui_nuevo_proveedor.setupUi(self.formularioProveedor)

        self.formularioProveedor.setParent(Form)
        self.formularioProveedor.show()
        
        # Eliminar widgets anteriores del gridLayout
        self.gridLayout.removeWidget(self.header_frame)
        self.gridLayout.removeWidget(self.table_frame)
    
        # Agregar el formulario arriba, el header abajo, y la tabla aún más abajo
        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)

        self.gridLayout.addWidget(self.formularioProveedor, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)
        
        
        # Funciones internas para ajustar altura y posición
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioProveedor.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()  # llamada inicial

        # Animación para deslizar desde arriba hacia abajo
        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioProveedor.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioProveedor, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioProveedor)
        Form.installEventFilter(self.resize_filter)
        
        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(lambda : guardar_registro(self.ui_nuevo_proveedor, self.formularioProveedor))

class ResizeHandler(QObject):
    def __init__(self, form, widget):
        super().__init__()
        self.form = form
        self.widget = widget

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            ancho = self.form.width()
            alto = int(self.form.height() * 0.40)
            self.widget.setGeometry(0, 0, ancho, alto)
        return False
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())