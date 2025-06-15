from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QApplication
)
from PySide6.QtCore import Qt
import sys

class ObraDesplegable(QWidget):
    def __init__(self, nombre_obra, datos):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.boton = QPushButton(f"▶ {nombre_obra}")
        self.boton.setCheckable(True)
        self.boton.setChecked(False)
        self.boton.clicked.connect(self.toggle_tabla)
        self.layout.addWidget(self.boton)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Dato", "Valor"])
        self.tabla.setRowCount(len(datos))

        for i, (dato, valor) in enumerate(datos.items()):
            self.tabla.setItem(i, 0, QTableWidgetItem(dato))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(valor)))

        self.tabla.setVisible(False)
        self.layout.addWidget(self.tabla)

    def toggle_tabla(self):
        visible = self.boton.isChecked()
        self.tabla.setVisible(visible)
        self.boton.setText(f"{'▼' if visible else '▶'} {self.boton.text()[2:]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = QWidget()
    layout = QVBoxLayout()
    ventana.setLayout(layout)

    obra1 = ObraDesplegable("Obra Avenida Central", {"Fecha": "2023-01-01", "Presupuesto": "1.000.000"})
    obra2 = ObraDesplegable("Obra Barrio Norte", {"Fecha": "2024-03-15", "Presupuesto": "850.000"})

    layout.addWidget(obra1)
    layout.addWidget(obra2)

    ventana.show()
    sys.exit(app.exec())