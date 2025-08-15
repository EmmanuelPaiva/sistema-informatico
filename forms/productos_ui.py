import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import Qt, QCoreApplication, QMetaObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView, QStackedLayout, QStackedWidget, QGridLayout, QMessageBox
)
from forms.agregarProductos import Ui_Form as AgregarProductoForm
from db.conexion import conexion
from forms.editarProductos import Ui_Form

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 600)
        
            # 🎨 Aplicar estilos globales
        Form.setStyleSheet("""
            QWidget {
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
                background-color: #f9fbfd;
            }

            /* Controles */
            QLineEdit, QDateTimeEdit, QComboBox {
                padding: 8px;
                border: 1px solid #b0c4de;
                border-radius: 8px;
                background-color: #ffffff;
            }

            QLineEdit:focus, QDateTimeEdit:focus, QComboBox:focus {
                border: 1px solid #5dade2;
                background-color: #eef7ff;
            }

            /* Botones */
            QPushButton {
                padding: 10px 18px;
                background-color: #5dade2;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }

            QPushButton:hover {
                background-color: #3498db;
            }

            QPushButton:pressed {
                background-color: #2e86c1;
            }

            /* Labels */
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }

            /* Tabla */
            QTableWidget {
                border: 1px solid #d6eaf8;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #d0d0d0;
            }

            QTableWidget::item {
                padding: 6px;
                font-size: 12px;
                color: #333333;
                height: 40px;
            }

            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-size: 13px;
            }

            QTableCornerButton::section {
                background-color: #3498db;
            }

            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #a0c4ff;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        
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
        self.horizontalLayout.setContentsMargins(60,30, 50,50)
        self.horizontalLayout.setSpacing(0)
    

        self.label = QLabel(self.frame)
        self.label.setObjectName("label")


        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(80, 32)
        self.pushButton.setMaximumWidth(190)

        
        self.pushButton.clicked.connect(self.mostrar_formulario)

        self.horizontalLayout.addWidget(self.label)
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.frame)

        self.tableWidget = QTableWidget(Form)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID","Nombre", "Precio", "Stock", "Proveedor", "Opciones"])
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(60)
        self.tableWidget.setColumnHidden(0, True)
        
        header = self.tableWidget.horizontalHeader()
        for col in range(6):
            header.setSectionResizeMode(col, QHeaderView.Stretch) 
        self.cargar_todos_los_productos()

        self.verticalLayout.addWidget(self.tableWidget)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Productos"))
        self.label.setText(QCoreApplication.translate("Form", "Productos"))
        self.pushButton.setText(QCoreApplication.translate("Form", "Agregar Producto"))

    
    def mostrar_formulario(self):
        if hasattr(self, 'widgetAgregarProducto'):
            return

        if hasattr(self, 'widgetEditarProducto'):
            return
        
        self.widgetAgregarProducto = QWidget()
        self.uiAgregarProducto = AgregarProductoForm()
        self.uiAgregarProducto.setupUi(self.widgetAgregarProducto)
                
        self.verticalLayout.insertWidget(1, self.widgetAgregarProducto)
        
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        query = "SELECT id_proveedor, nombre FROM proveedores;"
        cursor.execute(query)
        proveedores = cursor.fetchall()

        self.uiAgregarProducto.comboBoxProveedore.clear()

        for id_proveedor, nombre in proveedores:
            self.uiAgregarProducto.comboBoxProveedore.addItem(nombre, id_proveedor)
            self.uiAgregarProducto.comboBoxProveedore.setStyleSheet("""QComboBox {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 4px;
            }""")
        
        self.uiAgregarProducto.pushButton_2.clicked.connect(self.cancelar)
        self.uiAgregarProducto.pushButton.clicked.connect(self.aceptar)
        
        cursor.close()
        conexion_db.close()
        
            
    def cancelar(self):
        if hasattr(self, 'widgetAgregarProducto'):
            self.verticalLayout.removeWidget(self.widgetAgregarProducto)
            self.widgetAgregarProducto.deleteLater()
            del self.widgetAgregarProducto
        if hasattr(self, 'widgetEditarProducto'):
            self.verticalLayout.removeWidget(self.widgetEditarProducto)
            self.widgetEditarProducto.deleteLater()
            del self.widgetEditarProducto
    
    def aceptar(self):
        nombre = self.uiAgregarProducto.lineEditNombre.text()
        precio = self.uiAgregarProducto.lineEditPrecio.text()
        stock = self.uiAgregarProducto.lineEditStock.text()
        proveedor = self.uiAgregarProducto.comboBoxProveedore.currentData()
        descripcion = self.uiAgregarProducto.lineEditDescripcion.text()
        
        conexion_db = conexion()
        
        cursor = conexion_db.cursor()
        
        query = "INSERT INTO productos (nombre, precio_venta, stock_actual, id_proveedor) VALUES (%s,%s,%s,%s) RETURNING id_producto;"
        cursor.execute(query,(nombre, precio, stock, proveedor))
        id_producto = cursor.fetchone()[0]
        
        conexion_db.commit()
        cursor.close()
        conexion_db.close()
        
        self.cargar_datos(id_producto)
        
    def cargar_datos(self, id_producto):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        query = """
            SELECT p.id_producto,  p.nombre, p.precio_venta, p.stock_actual, pr.nombre AS proveedor
            FROM productos p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            WHERE p.id_producto = %s;
        """
        cursor.execute(query, (id_producto,))
        producto = cursor.fetchone()
        
        if producto:
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            id_producto = producto[0]
        
            for col, valor in enumerate(producto):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row_count, col, item)

            boton_editar = QPushButton("Editar")
            boton_editar.setStyleSheet("background-color: #3498db; color: white; border-radius: 5px; padding: 4px;")
            boton_editar.clicked.connect(lambda _, pid=producto[0]: self.mostrar_formulario_editar(pid))
            
            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter) 
            layout.setContentsMargins(0, 0, 0, 0) 
            
            boton_eliminar = QPushButton("Eliminar")
            boton_eliminar.setStyleSheet("background-color: #e00000; color: white; border-radius: 5px; padding: 4px;")
            boton_eliminar.clicked.connect(lambda _, r=row_count: self.eliminar_producto(r))
            self.tableWidget.setCellWidget(row_count, 5, contenedor)
        
            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
                            
            cursor.close()
            conexion_db.close()    
            self.cancelar()
            
    def cargar_todos_los_productos(self):
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        query = """
            SELECT p.id_producto, p.nombre, p.precio_venta, p.stock_actual, pr.nombre AS proveedor
            FROM productos p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor;
        """
        cursor.execute(query)
        productos = cursor.fetchall()

        self.tableWidget.setRowCount(0) 

        for producto in productos:
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            #id_producto = producto[0] 

            for col, valor in enumerate(producto):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row_count, col, item)
                
            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter) 
            layout.setContentsMargins(0, 0, 0, 0) 

            boton_editar = QPushButton("Editar")
            boton_editar.setStyleSheet("background-color: #3498db; color: white; border-radius: 5px; padding: 4px;")
            boton_editar.clicked.connect(lambda _, pid=producto[0]: self.mostrar_formulario_editar(pid))

            boton_eliminar = QPushButton("Eliminar")
            boton_eliminar.setStyleSheet("background-color: #e00000; color: white; border-radius: 5px; padding: 4px;")
            boton_eliminar.clicked.connect(lambda _, pid=producto[0]: self.eliminar_producto(pid))
            
            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
            self.tableWidget.setCellWidget(row_count, 5, contenedor)

        cursor.close()
        conexion_db.close()
        
    def eliminar_producto(self, id_producto):
        confirm = QMessageBox.question(None, "Eliminar", "¿Estás seguro de eliminar este producto?",
            QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            query = "DELETE FROM productos WHERE id_producto = %s;"
            cursor.execute(query, (id_producto,))
            conexion_db.commit()
            cursor.close()
            conexion_db.close()
            
            for fila in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(fila, 0)
                if item and int(item.text()) == id_producto:
                    self.tableWidget.removeRow(fila)
                    break
                
    def mostrar_formulario_editar(self, id_producto):
        if hasattr(self, 'widgetEditarProducto'):
            return
        
        if hasattr(self, 'widgetAgregarProducto'):
            return
        
        self.widgetEditarProducto = QWidget()
        self.uiEditarProducto = AgregarProductoForm()
        self.uiEditarProducto.setupUi(self.widgetEditarProducto)
        self.verticalLayout.insertWidget(1, self.widgetEditarProducto)

        conexion_db = conexion()
        cursor = conexion_db.cursor()
        query = "SELECT nombre, precio_venta, stock_actual, descripcion, id_proveedor FROM productos WHERE id_producto = %s;"
        cursor.execute(query, (id_producto,))
        producto = cursor.fetchone()
        cursor.close()
        conexion_db.close()

        if producto:
            nombre, precio, stock, descripcion ,proveedor = producto

            self.uiEditarProducto.lineEditNombre.setText(nombre)
            self.uiEditarProducto.lineEditPrecio.setText(str(precio))
            self.uiEditarProducto.lineEditStock.setText(str(stock))
            self.uiEditarProducto.lineEditDescripcion.setText(descripcion)  # si querés

            # cargar combo de proveedores como antes
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            cursor.execute("SELECT id_proveedor, nombre FROM proveedores")
            proveedores = cursor.fetchall()
            self.uiEditarProducto.comboBoxProveedore.clear()
            for idp, nombrep in proveedores:
                self.uiEditarProducto.comboBoxProveedore.addItem(nombrep, idp)
                if idp == proveedor:
                    self.uiEditarProducto.comboBoxProveedore.setCurrentIndex(
                        self.uiEditarProducto.comboBoxProveedore.count() - 1
                    )
            cursor.close()
            conexion_db.close()

            # cone
            self.uiEditarProducto.pushButton_2.clicked.connect(self.cancelar)
            self.uiEditarProducto.pushButton.clicked.connect(lambda: self.editar_producto(id_producto))
            
    def editar_producto(self, id_producto):
    # ─── 1. Leer y validar campos ────────────────────────────
        nombre     = self.uiEditarProducto.lineEditNombre.text()
        precio_txt = self.uiEditarProducto.lineEditPrecio.text()
        stock_txt  = self.uiEditarProducto.lineEditStock.text()
        proveedor  = self.uiEditarProducto.comboBoxProveedore.currentData()

        try:
            precio = float(precio_txt)
            stock  = int(stock_txt)
        except ValueError:
            QMessageBox.warning(None, "Error",
                                "Precio debe ser número y stock un entero.")
            return

        # ─── 2. Actualizar en la BD ──────────────────────────────
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    UPDATE productos
                    SET nombre = %s,
                        precio_venta = %s,
                        stock_actual = %s,
                        id_proveedor = %s
                    WHERE id_producto = %s
                    RETURNING id_producto;
                    """,
                    (nombre, precio, stock, proveedor, id_producto)
                )
            c.commit()

        # ─── 3. Actualizar la tabla sin que “salte” ──────────────
        self.tableWidget.setSortingEnabled(False)          # congela orden

        for fila in range(self.tableWidget.rowCount()):
            item_id = self.tableWidget.item(fila, 0)
            if item_id and int(item_id.text()) == id_producto:

                # Columna 1: Nombre
                self.tableWidget.item(fila, 1).setText(nombre)

                # Columna 2: Precio
                self.tableWidget.item(fila, 2).setText(str(precio))

                # Columna 3: Stock
                self.tableWidget.item(fila, 3).setText(str(stock))

                # Columna 4: Proveedor
                proveedor_txt = (
                    self.uiEditarProducto.comboBoxProveedore.currentText()
                )
                self.tableWidget.item(fila, 4).setText(proveedor_txt)

                break

        self.tableWidget.setSortingEnabled(True)           # vuelve orden

        # ─── 4. Cerrar formulario de edición ─────────────────────
        self.cancelar()
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
