from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QPushButton, QLineEdit, QTabWidget,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView, QInputDialog
)
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Obras")
        self.setGeometry(300, 150, 900, 600)

        # QStackedWidget para manejar las páginas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Página principal con carpetas
        self.pagina_principal = QWidget()
        layout_principal = QVBoxLayout(self.pagina_principal)

        titulo = QLabel("📂 Obras")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #333; margin: 10px;")

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                font-size: 14px;
            }
            QTreeWidget::item {
                padding: 8px;
                color: black;
            }
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: black;
            }
        """)

        # Ejemplo de carpetas
        obras = ["Obra Casa López", "Obra Edificio San Martín", "Obra Escuela Central"]
        for obra in obras:
            item = QTreeWidgetItem([obra])
            self.tree.addTopLevelItem(item)

        self.tree.itemClicked.connect(self.abrir_obra)

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(self.tree)

        # Añadir la página principal al stacked widget
        self.stacked_widget.addWidget(self.pagina_principal)

    def abrir_obra(self, item):
        nombre_obra = item.text(0)

        # Crear página de la obra
        pagina_obra = QWidget()
        layout_obra = QVBoxLayout(pagina_obra)

        # Título
        titulo_obra = QLabel(f"🏗 {nombre_obra}")
        titulo_obra.setAlignment(Qt.AlignCenter)
        titulo_obra.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")

        # Botón volver
        boton_volver = QPushButton("⬅ Volver a Obras")
        boton_volver.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        boton_volver.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.pagina_principal))

        # Tabla editable
        tabla = QTableWidget(5, 5)  # Empieza con 5 filas y 5 columnas
        tabla.setEditTriggers(QAbstractItemView.AllEditTriggers)  # Editar celdas
        tabla.horizontalHeader().setSectionsClickable(True)  # Click en headers
        tabla.horizontalHeader().setSectionsMovable(True)    # Mover columnas
        tabla.verticalHeader().setSectionsMovable(True)      # Mover filas
        tabla.setHorizontalHeaderLabels([f"Columna {i+1}" for i in range(5)])
        tabla.horizontalHeader().sectionDoubleClicked.connect(
            lambda idx: self.editar_encabezado(tabla, idx)
        )

        # Botones para modificar tabla
        contenedor_botones = QHBoxLayout()

        btn_agregar_fila = QPushButton("➕ Fila")
        btn_agregar_fila.clicked.connect(lambda: tabla.insertRow(tabla.rowCount()))

        btn_eliminar_fila = QPushButton("🗑 Fila")
        btn_eliminar_fila.clicked.connect(lambda: tabla.removeRow(tabla.currentRow()))

        btn_agregar_columna = QPushButton("➕ Columna")
        btn_agregar_columna.clicked.connect(lambda: tabla.insertColumn(tabla.columnCount()))

        btn_eliminar_columna = QPushButton("🗑 Columna")
        btn_eliminar_columna.clicked.connect(lambda: tabla.removeColumn(tabla.currentColumn()))

        for btn in [btn_agregar_fila, btn_eliminar_fila, btn_agregar_columna, btn_eliminar_columna]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #45A049;
                }
            """)
            contenedor_botones.addWidget(btn)

        # Añadir widgets al layout
        layout_obra.addWidget(titulo_obra)
        layout_obra.addWidget(boton_volver)
        layout_obra.addLayout(contenedor_botones)
        layout_obra.addWidget(tabla)

        # Cambiar la vista a la obra
        self.stacked_widget.addWidget(pagina_obra)
        self.stacked_widget.setCurrentWidget(pagina_obra)


    def editar_encabezado(self, tabla, indice):
        """Permite editar el texto del encabezado de la columna."""
        nuevo_texto, ok = QInputDialog.getText(None, "Editar Encabezado", 
                                               "Nuevo nombre:", 
                                               text=tabla.horizontalHeaderItem(indice).text())
        if ok and nuevo_texto.strip():
            tabla.setHorizontalHeaderItem(indice, QTableWidgetItem(nuevo_texto))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
