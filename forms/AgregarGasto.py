import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFrame, QFormLayout, QComboBox, QLineEdit,
    QDoubleSpinBox, QDateEdit, QHBoxLayout, QPushButton, QMessageBox, QLabel
)

# Cargamos productos para el caso "Material"
try:
    from db.conexion import conexion
except Exception:
    conexion = None  # por si corrés el widget aislado


class GastoFormWidget(QWidget):
    """Formulario inline para registrar un gasto (embebido, no diálogo).
       Cuando Tipo = 'Material', permite seleccionar un producto para descontar stock (obras_consumos)."""
    def __init__(self, on_submit, on_cancel=None, parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        self.setObjectName("GastoForm")

        self._productos_cache = []      # [(id_producto, nombre, unidad, precio_ref)]
        self._precio_bloqueado = False  # usamos flag para evitar loops al setear precio desde código

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

        # Producto (visible solo si tipo=Material)
        self.input_producto = QComboBox()
        self.input_producto.setVisible(True)  # por defecto arranca en Material
        self.lbl_producto = QLabel("Producto:")
        self.lbl_producto.setVisible(True)
        form.addRow(self.lbl_producto, self.input_producto)

        # Descripción (nota / detalle)
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Ej.: Cemento CP II, Albañil, Flete…")
        form.addRow("Descripción:", self.input_desc)

        # Unidad (editable si NO es material; autocompletada si es material)
        self.input_unidad = QComboBox()
        self.input_unidad.setEditable(True)
        self.input_unidad.addItems(["unidades", "bolsas", "m³", "m²", "días", "horas", "kg"])
        form.addRow("Unidad:", self.input_unidad)

        # Cantidad
        self.input_cantidad = QDoubleSpinBox()
        self.input_cantidad.setDecimals(3)
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
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")
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
        self.input_tipo.currentIndexChanged.connect(self._on_tipo_changed)
        self.input_producto.currentIndexChanged.connect(self._on_producto_changed)
        self.input_cantidad.valueChanged.connect(self._recalcular_total)
        self.input_precio.valueChanged.connect(self._recalcular_total)

        # Inicializar productos si estamos en "Material"
        self._cargar_productos()
        self._on_tipo_changed()  # ajusta visibilidad y bloqueos iniciales

    # ----------------- Carga de productos -----------------
    def _cargar_productos(self):
        """Carga productos desde la BD con unidad y precio de referencia (costo o precio_venta)."""
        self._productos_cache.clear()
        self.input_producto.clear()

        if conexion is None:
            # Modo fallback si no hay conexión (testing del widget)
            return

        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute("""
                        SELECT id_producto,
                               nombre,
                               COALESCE(unidad, '') AS unidad,
                               COALESCE(costo_unitario, precio_venta, 0) AS precio_ref
                        FROM productos
                        ORDER BY nombre;
                    """)
                    rows = cur.fetchall()
                    for pid, nombre, unidad, precio_ref in rows:
                        self._productos_cache.append((pid, nombre, unidad, float(precio_ref or 0)))
                        self.input_producto.addItem(nombre, pid)
        except Exception as e:
            QMessageBox.warning(self, "Productos", f"No se pudieron cargar productos:\n{e}")

    # ----------------- Reacciones UI -----------------
    def _on_tipo_changed(self):
        es_material = (self.input_tipo.currentText().lower() == "material")
        # Alternar producto
        self.input_producto.setVisible(es_material)
        self.lbl_producto.setVisible(es_material)

        # Si es material: Unidad se autocompleta y la dejamos editable pero con valor sugerido
        # Precio se autocompleta con costo/venta de referencia (usuario puede editar).
        if es_material:
            if self.input_producto.count() == 0:
                self._cargar_productos()
            self._on_producto_changed()  # sincroniza unidad/precio según producto
        else:
            # Para otros tipos: no forzamos la unidad ni el precio
            pass

    def _on_producto_changed(self):
        """Cuando cambia el producto, autocompleta unidad y precio de referencia."""
        idx = self.input_producto.currentIndex()
        if idx < 0 or idx >= len(self._productos_cache):
            return
        _, _, unidad, precio_ref = self._productos_cache[idx]

        # Setear unidad (si está presente en la lista, seleccionarla; si no, agregarla)
        if unidad:
            # buscar en opciones existentes
            found = False
            for i in range(self.input_unidad.count()):
                if self.input_unidad.itemText(i).lower() == unidad.lower():
                    self.input_unidad.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.input_unidad.insertItem(0, unidad)
                self.input_unidad.setCurrentIndex(0)

        # Setear precio de referencia (editable)
        self._precio_bloqueado = True
        try:
            self.input_precio.setValue(float(precio_ref or 0))
        finally:
            self._precio_bloqueado = False

        self._recalcular_total()

    def _recalcular_total(self):
        # Solo recalculamos si no estamos en un setValue programático del precio
        if self._precio_bloqueado:
            return
        # (La UI principal puede mostrar total, aquí solo mantenemos consistencia de datos)

    # ----------------- API pública -----------------
    def _submit(self):
        datos = self.datos()
        # Validaciones mínimas
        if datos["tipo"].lower() == "material":
            if not datos["id_producto"]:
                QMessageBox.warning(self, "Validación", "Seleccioná un producto para descontar stock.")
                return
            if datos["cantidad"] <= 0:
                QMessageBox.warning(self, "Validación", "La cantidad debe ser mayor a 0.")
                return
        else:
            if not datos["descripcion"]:
                QMessageBox.warning(self, "Validación", "Ingresá una descripción para el gasto.")
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

        es_material = (self.input_tipo.currentText().lower() == "material")
        id_producto = None
        if es_material and self.input_producto.currentIndex() >= 0:
            id_producto = self.input_producto.currentData()

        return {
            "tipo": self.input_tipo.currentText(),
            "usa_producto": es_material,                # True si debe ir a obras_consumos (descontar stock)
            "id_producto": id_producto,                 # None si no aplica
            "descripcion": self.input_desc.text().strip(),  # se puede usar como nota
            "cantidad": cantidad,
            "unidad": self.input_unidad.currentText().strip(),
            "precio": precio,
            "total": total,
            "fecha": self.input_fecha.date().toPython(),    # date nativo
        }

    def limpiar(self):
        self.input_tipo.setCurrentIndex(0)
        self.input_producto.setCurrentIndex(0)
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
    ui = GastoFormWidget(lambda d: print("SUBMIT:", d), lambda: print("CANCEL"))
    ui.show()
    sys.exit(app.exec())
