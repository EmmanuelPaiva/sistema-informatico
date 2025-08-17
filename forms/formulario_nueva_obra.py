from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QDateEdit, QDoubleSpinBox, QGridLayout, QSizePolicy, QComboBox
)

class FormularioNuevaObra(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(self.estilos())

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("Registrar Nueva Obra")
        fuente = QFont("Segoe UI", 16, QFont.Bold)
        titulo.setFont(fuente)
        layout.addWidget(titulo, alignment=Qt.AlignHCenter)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(12)

        self.input_nombre = QLineEdit()
        self.input_direccion = QLineEdit()
        self.input_fecha_inicio = QDateEdit()
        self.input_fecha_fin = QDateEdit()
        self.input_estado = QComboBox()
        self.input_estado.addItems(["En progreso", "Pausado", "Finalizado"])
        self.input_metros = QDoubleSpinBox()
        self.input_metros.setMaximum(99999)
        self.input_metros.setSuffix(" m²")
        self.input_presupuesto = QDoubleSpinBox()
        self.input_presupuesto.setMaximum(999999999)
        self.input_presupuesto.setPrefix("Gs. ")
        self.input_descripcion = QTextEdit()

        # Fila 0
        grid.addWidget(QLabel("Nombre de la Obra:"), 0, 0)
        grid.addWidget(self.input_nombre, 0, 1)
        grid.addWidget(QLabel("Dirección:"), 0, 2)
        grid.addWidget(self.input_direccion, 0, 3)

        # Fila 1
        grid.addWidget(QLabel("Fecha de Inicio:"), 1, 0)
        grid.addWidget(self.input_fecha_inicio, 1, 1)
        grid.addWidget(QLabel("Fecha de Entrega:"), 1, 2)
        grid.addWidget(self.input_fecha_fin, 1, 3)

        # Fila 2
        grid.addWidget(QLabel("Estado:"), 2, 0)
        grid.addWidget(self.input_estado, 2, 1)
        grid.addWidget(QLabel("Metros Cuadrados:"), 2, 2)
        grid.addWidget(self.input_metros, 2, 3)

        # Fila 3
        grid.addWidget(QLabel("Presupuesto Total:"), 3, 0)
        grid.addWidget(self.input_presupuesto, 3, 1, 1, 3)

        # Fila 4
        grid.addWidget(QLabel("Descripción:"), 4, 0, 1, 4)
        grid.addWidget(self.input_descripcion, 5, 0, 1, 4)

        layout.addLayout(grid)

        # Botones
        botones_layout = QHBoxLayout()
        self.btn_aceptar = QPushButton("Aceptar")
        self.btn_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_aceptar)

        layout.addLayout(botones_layout)
        
    def obtener_datos(self):
        nombre = self.input_nombre.text().strip()
        direccion = self.input_direccion.text().strip()
        fecha_inicio = self.input_fecha_inicio.date().toPython()
        fecha_fin = self.input_fecha_fin.date().toPython()
        estado = self.input_estado.currentText()
        metros = self.input_metros.value()
        presupuesto = self.input_presupuesto.value()
        descripcion = self.input_descripcion.toPlainText().strip()

        if not nombre or not direccion or metros <= 0 or presupuesto <= 0:
            return None

        return {
            "nombre": nombre,
            "direccion": direccion,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "estado": estado,
            "metros_cuadrados": metros,
            "presupuesto_total": presupuesto,
            "descripcion": descripcion
        }

    def limpiar_campos(self):
        self.input_nombre.clear()
        self.input_direccion.clear()
        self.input_fecha_inicio.setDate(QDate.currentDate())
        self.input_fecha_fin.setDate(QDate.currentDate())
        self.input_estado.setCurrentIndex(0)
        self.input_metros.setValue(0)
        self.input_presupuesto.setValue(0)
        self.input_descripcion.clear()

    def estilos(self):
        return """
        QWidget {
            font-family: 'Segoe UI';
            font-size: 11pt;
            background-color: #f5f6fa;
        }

        QLineEdit, QDateEdit, QDoubleSpinBox, QTextEdit {
            background-color: white;
            border: 1px solid #dcdde1;
            border-radius: 8px;
            padding: 6px;
            color: black;
        }

        QPushButton {
            background-color: #0097e6;
            color: white;
            padding: 8px 20px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #00a8ff;
        }

        QLabel {
            color: #2f3640;
        }
        """

# Ejemplo de prueba visual
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = FormularioNuevaObra()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
