from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QDateEdit, QDoubleSpinBox, QGridLayout, QSizePolicy, QComboBox, QMessageBox
)

class FormularioNuevaObra(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Usa estilos globales (main/themes.py) según el modo claro/oscuro

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

        # Widgets
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej.: Vivienda unifamiliar – Barrio X")

        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Calle / Ciudad")

        self.input_fecha_inicio = QDateEdit()
        self.input_fecha_inicio.setCalendarPopup(True)
        self.input_fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_inicio.setDate(QDate.currentDate())

        self.input_fecha_fin = QDateEdit()
        self.input_fecha_fin.setCalendarPopup(True)
        self.input_fecha_fin.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_fin.setDate(QDate.currentDate().addDays(30))

        self.input_estado = QComboBox()
        self.input_estado.addItems(["En progreso", "Pausado", "Finalizado"])

        self.input_metros = QDoubleSpinBox()
        self.input_metros.setMaximum(9999999)
        self.input_metros.setDecimals(2)
        self.input_metros.setSingleStep(1.0)
        self.input_metros.setSuffix(" m²")
        self.input_metros.setValue(0.00)

        self.input_presupuesto = QDoubleSpinBox()
        self.input_presupuesto.setMaximum(9999999999)
        self.input_presupuesto.setDecimals(2)
        self.input_presupuesto.setSingleStep(10000.0)
        self.input_presupuesto.setPrefix("Gs. ")
        self.input_presupuesto.setValue(0.00)

        self.input_descripcion = QTextEdit()
        self.input_descripcion.setPlaceholderText("Notas / alcance / detalles…")

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
        self.btn_aceptar.setObjectName("btnAceptarObra")         # PATCH permisos
        self.btn_aceptar.setProperty("perm_code", "obras.create")
        # Aplicar tipos para que tomen estilos del tema
        self.btn_aceptar.setProperty("type", "primary")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setProperty("type", "secondary")
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_aceptar)

        layout.addLayout(botones_layout)

    def obtener_datos(self):
        nombre = self.input_nombre.text().strip()
        direccion = self.input_direccion.text().strip()
        fecha_inicio = self.input_fecha_inicio.date().toPython()  # datetime.date
        fecha_fin = self.input_fecha_fin.date().toPython()        # datetime.date
        estado = self.input_estado.currentText()
        metros = float(self.input_metros.value())                  # float -> numeric en DB
        presupuesto = float(self.input_presupuesto.value())        # float -> numeric en DB
        descripcion = self.input_descripcion.toPlainText().strip()

        # Validaciones básicas
        if not nombre or not direccion:
            QMessageBox.warning(self, "Validación", "Nombre y Dirección son obligatorios.")
            return None

        if metros <= 0:
            QMessageBox.warning(self, "Validación", "Metros cuadrados debe ser mayor que 0.")
            return None

        if presupuesto <= 0:
            QMessageBox.warning(self, "Validación", "El presupuesto total debe ser mayor que 0.")
            return None

        if fecha_fin < fecha_inicio:
            QMessageBox.warning(self, "Validación", "La fecha de entrega no puede ser anterior a la fecha de inicio.")
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
        self.input_metros.setValue(0.00)
        self.input_presupuesto.setValue(0.00)
        self.input_descripcion.clear()

    # Estilos propios eliminados para heredar del tema global

# Ejemplo de prueba visual
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = FormularioNuevaObra()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
