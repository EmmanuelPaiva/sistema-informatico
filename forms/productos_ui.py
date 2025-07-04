import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import Qt, QCoreApplication, QMetaObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,QStackedLayout, QStackedWidget, QGridLayout
)
from forms.agregarProductos import Ui_Form as AgregarProductoForm
from db.conexion import conexion

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 600)
        
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

        self.frame = QFrame(Form)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setMinimumHeight(0)
        self.frame.setStyleSheet("QFrame { border: none; padding: 0px; margin: 0px; background-color: #f0f0f0; }")

        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(80,50, 50,50)
        self.horizontalLayout.setSpacing(0)
    

        self.label = QLabel(self.frame)
        self.label.setObjectName("label")
        self.label.setStyleSheet("""
            QLabel {
                margin: 0px;
                padding: 0px;
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(80, 32)
        self.pushButton.setMaximumWidth(190)
        self.pushButton.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border: none;
                background-color: #3498db;
                border-radius: 5px;
                color: white;
            }
        """)
        
        self.pushButton.clicked.connect(self.mostrar_productos)

        self.horizontalLayout.addWidget(self.label)
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.frame)

        self.tableWidget = QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Nombre", "Precio", "Stock", "Proveedor", "Opciones"])
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(60)
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background-color: #f0f0f0;
                border: none;
                gridline-color: transparent;
                color: #2c3e50;
                font-size: 14px;
                border-bottom: 1px solid #dcdcdc;
            }
            QTableWidget::item {
                border-bottom: 1px solid #d0d0d0; 
                
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #2c3e50;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #d0d0d0;
            }
            
        """)

        self.verticalLayout.addWidget(self.tableWidget)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

        self.cargar_datos()

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Productos"))
        self.label.setText(QCoreApplication.translate("Form", "Productos"))
        self.pushButton.setText(QCoreApplication.translate("Form", "Agregar Producto"))

    def cargar_datos(self):
        datos = [
            ("Cemento", "65.000", "90", "Acemar"),
            ("Hierro", "180.000", "40", "HierrosPy")
        ]

        self.tableWidget.setRowCount(len(datos))

        for fila, fila_datos in enumerate(datos):
            for col, valor in enumerate(fila_datos):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(fila, col, item)

            boton_editar = QPushButton("Editar")
            boton_editar.setStyleSheet("background-color: #3498db; color: white; border-radius: 5px; padding: 4px;")
            boton_editar.setFixedSize(80, 30)
            boton_editar.clicked.connect(lambda _, f=fila: print(f"Editar fila {f}"))
            header = self.tableWidget.horizontalHeader()
            
            boton_eliminar = QPushButton("Eliminar")
            boton_eliminar.setStyleSheet("background-color: #e00000; color: white; border-radius: 5px; padding: 4px;")
            boton_eliminar.setFixedSize(80, 30)
            boton_eliminar.clicked.connect(self.cancelar)

            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter) 
            layout.setContentsMargins(0, 0, 0, 0) 
            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
            self.tableWidget.setCellWidget(fila, 4, contenedor)
            
        for col in range(self.tableWidget.columnCount()):
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
    def mostrar_productos(self):
        if hasattr(self, 'widgetAgregarProducto'):
            return
        
        self.widgetAgregarProducto = QWidget()
        self.uiAgregarProducto = AgregarProductoForm()
        self.uiAgregarProducto.setupUi(self.widgetAgregarProducto)
                
        self.verticalLayout.insertWidget(1, self.widgetAgregarProducto)
        
        self.uiAgregarProducto.pushButton_2.clicked.connect(self.cancelar)
            
    def cancelar(self):
        if hasattr(self, 'widgetAgregarProducto'):
            self.verticalLayout.removeWidget(self.widgetAgregarProducto)
            self.widgetAgregarProducto.deleteLater()
            del self.widgetAgregarProducto
    
    def registrar_productos(self):
        nombre = self.uiAgregarProducto.lineEditNombre.text()
        precio = self.uiAgregarProducto.lineEditPrecio.text()
        stock = self.uiAgregarProducto.lineEditStock.text()
        proveedor = self.uiAgregarProducto.comboBoxProveedore.currentText()
        descripcion = self.uiAgregarProducto.textEditDescripcion.toPlainText()
        
        conexion_db = conexion
        
        
        
            
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
