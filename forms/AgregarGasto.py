import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFrame, QFormLayout, QComboBox, QLineEdit,
    QDoubleSpinBox, QDateEdit, QHBoxLayout, QPushButton
)


class GastoFormWidget(QWidget):
    """Formulario inline para registrar un gasto (embebido, no diálogo)."""
    def __init__(self, on_submit, on_cancel=None, parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        self.setObjectName("GastoForm")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(8)

        self.frame = QFrame(self)
        self.frame.setObjectName("GastoFormFrame")
        root_layout.addWidget(self.frame)

        form = QFormLayout(self.frame)
        form.setContentsMargins(10, 10, 10, 6)
        form.setSpacing(10)

        # Tipo
        self.input_tipo = QComboBox()
        self.input_tipo.addItems(["Material", "Mano de obra", "Servicio", "Transporte", "Otro"])
        form.addRow("Tipo:", self.input_tipo)

        # Descripción
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Ej.: Cemento, Albañil, Flete…")
        form.addRow("Descripción:", self.input_desc)

        # Unidad
        self.input_unidad = QComboBox()
        self.input_unidad.setEditable(True)
        self.input_unidad.addItems(["unidades", "bolsas", "m³", "m²", "días", "horas", "kg"])
        form.addRow("Unidad:", self.input_unidad)

        # Cantidad
        self.input_cantidad = QDoubleSpinBox()
        self.input_cantidad.setDecimals(2)
        self.input_cantidad.setRange(0, 1_000_000)
        self.input_cantidad.setValue(1)
        form.addRow("Cantidad:", self.input_cantidad)

        # Precio unitario
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setDecimals(2)
        self.input_precio.setRange(0, 1_000_000_000)
        self.input_precio.setValue(0)
        form.addRow("Precio unitario (Gs.):", self.input_precio)

        # Fecha
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())
        form.addRow("Fecha:", self.input_fecha)

        # Botones
        botones = QHBoxLayout()
        botones.setContentsMargins(0, 0, 0, 0)
        botones.setSpacing(8)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("cancel")
        self.btn_guardar = QPushButton("Guardar gasto")
        botones.addStretch()
        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)
        root_layout.addLayout(botones)

        # Estilos (colores Rodler)
        self.setStyleSheet("""
            #GastoFormFrame {
                background: #ffffff;
                border: 1px solid #0097e6;
                border-radius: 10px;
            }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                padding: 6px; border: 1px solid #dcdde1; border-radius: 6px; background: #ffffff;
                color: black;
            }
            QPushButton { padding: 8px 12px; border-radius: 6px; color: white; background-color: #0097e6; }
            QPushButton#cancel { background-color: #7f8c8d; }
            QPushButton:hover { background-color: #00a8ff; }
        """)

        # Conexiones
        self.btn_guardar.clicked.connect(self._submit)
        self.btn_cancelar.clicked.connect(self._cancel)

    def _submit(self):
        datos = self.datos()
        if not datos["descripcion"]:
            # Si querés, acá podés validar con un QMessageBox. Por ahora, evitamos guardar vacío.
            return
        if callable(self.on_submit):
            self.on_submit(datos)

    def _cancel(self):
        if callable(self.on_cancel):
            self.on_cancel()

    def datos(self):
        cantidad = float(self.input_cantidad.value())
        precio = float(self.input_precio.value())
        total = round(cantidad * precio, 2)
        return {
            "tipo": self.input_tipo.currentText(),
            "descripcion": self.input_desc.text().strip(),
            "cantidad": cantidad,
            "unidad": self.input_unidad.currentText().strip(),
            "precio": precio,
            "total": total,
            "fecha": self.input_fecha.date().toString("dd/MM/yyyy"),
        }

    def limpiar(self):
        self.input_tipo.setCurrentIndex(0)
        self.input_desc.clear()
        self.input_unidad.setCurrentIndex(0)
        self.input_cantidad.setValue(1)
        self.input_precio.setValue(0)
        self.input_fecha.setDate(QDate.currentDate())

    def focusIn(self):
        self.input_desc.setFocus()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = GastoFormWidget(Form)
    ui.show()
    sys.exit(app.exec())
