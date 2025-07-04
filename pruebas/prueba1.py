# Diseño de una interfaz CRUD de productos usando PySide6 y QTableWidget

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView
)
from PySide6.QtGui import QColor, Qt
import sys

class ProductosUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.resize(800, 600)

        # Layout principal
        layout_principal = QVBoxLayout()

        # Formulario de entrada
        formulario = QFormLayout()
        self.input_nombre = QLineEdit()
        self.input_categoria = QLineEdit()
        self.input_precio = QLineEdit()
        self.input_stock = QLineEdit()
        self.input_costo = QLineEdit()
        self.combo_proveedor = QComboBox()
        self.combo_proveedor.addItems(["Proveedor A", "Proveedor B"])  # Simulado

        formulario.addRow("Nombre:", self.input_nombre)
        formulario.addRow("Categoría:", self.input_categoria)
        formulario.addRow("Precio Venta:", self.input_precio)
        formulario.addRow("Stock:", self.input_stock)
        formulario.addRow("Costo Unitario:", self.input_costo)
        formulario.addRow("Proveedor:", self.combo_proveedor)

        layout_principal.addLayout(formulario)

        # Botones CRUD
        botones = QHBoxLayout()
        self.boton_agregar = QPushButton("Agregar")
        self.boton_editar = QPushButton("Editar")
        self.boton_eliminar = QPushButton("Eliminar")
        self.boton_limpiar = QPushButton("Limpiar")

        botones.addWidget(self.boton_agregar)
        botones.addWidget(self.boton_editar)
        botones.addWidget(self.boton_eliminar)
        botones.addWidget(self.boton_limpiar)

        layout_principal.addLayout(botones)
        widget = QWidget()
        layout = QHBoxLayout()
        etiqueta = QLabel("Disponible")
        etiqueta.setStyleSheet("background-color: #D4EDDA; padding: 4px; border-radius: 5px;")
        layout.addWidget(etiqueta)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)


        # Tabla de productos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Categoría", "Precio", "Stock", "Proveedor"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout_principal.addWidget(self.tabla)

        self.setLayout(layout_principal)

        # Simular carga de datos
        self.cargar_datos_demo()    
        self.tabla.setStyleSheet("""
         QTableWidget {
            background-color: #F9F9F9;
            border: none;
            font-size: 14px;
        }
         QHeaderView::section {
            background-color: #EDEDED;
            padding: 5px;
            font-weight: bold;
            border: none;
        }
        QTableWidget::item {
            padding: 10px;
        }
        """)

    def cargar_datos_demo(self):
        datos = [
            (1, "Cemento", "Construcción", "25000", "100", "Materiales SRL"),
            (2, "Ladrillo", "Construcción", "3000", "500", "Ladrillos PY")
        ]

        self.tabla.setRowCount(len(datos))
        for fila, tupla in enumerate(datos):
            for columna, valor in enumerate(tupla):
                item = QTableWidgetItem(str(valor))
                if columna == 4 and int(valor) < 50:
                    item.setBackground(QColor("#FFD2D2"))  # Rojo claro si stock bajo
                self.tabla.setItem(fila, columna, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ProductosUI()
    ventana.show()
    sys.exit(app.exec())
