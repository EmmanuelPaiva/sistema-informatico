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
       Reglas:
       - Tipo = 'Material': Producto visible; Descripción oculta; Unidad sugerida desde el producto
         pero editable; Precio unitario autocompletado; Total recalculado localmente.
       - Tipo != 'Material': Producto oculto; Descripción visible; Unidad editable.
       - La BD calcula costo_total definitivo con trigger; aquí solo se muestra el estimado.
    """
    def __init__(self, on_submit, on_cancel=None, parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        self.setObjectName("GastoForm")

        # [(id_producto, nombre, unidad, precio_ref)]
        self._productos_cache = []
        self._precio_bloqueado = False  # evita loops al setear precio desde código

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
        self.lbl_producto = QLabel("Producto:")
        form.addRow(self.lbl_producto, self.input_producto)

        # Descripción (solo si tipo != Material) -> se guarda en 'concepto'
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Ej.: Albañil, Flete, Servicio de mixer…")
        self.lbl_desc = QLabel("Descripción:")
        form.addRow(self.lbl_desc, self.input_desc)

        # Unidad (si es Material se sugiere desde producto PERO queda editable)
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

        # Precio unitario (costo_unitario)
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setDecimals(2)
        self.input_precio.setRange(0, 1_000_000_000)
        self.input_precio.setValue(0)
        form.addRow("Precio unitario (Gs.):", self.input_precio)

        # Total (solo lectura, calculado localmente para mostrar)
        self.lbl_total = QLabel("Costo total (Gs.):")
        self.input_total = QLineEdit("0.00")
        self.input_total.setReadOnly(True)
        form.addRow(self.lbl_total, self.input_total)

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

        # Estilos locales removidos: usar QSS global (main/themes.py)
        # Configurar tipos para botones y permitir que el QSS global los pinte
        self.btn_guardar.setProperty("type", "primary")
        self.btn_cancelar.setProperty("type", "secondary")

        # Conexiones
        self.btn_guardar.clicked.connect(self._submit)
        self.btn_cancelar.clicked.connect(self._cancel)
        self.input_tipo.currentIndexChanged.connect(self._on_tipo_changed)
        self.input_producto.currentIndexChanged.connect(self._on_producto_changed)
        self.input_cantidad.valueChanged.connect(self._recalcular_total)
        self.input_precio.valueChanged.connect(self._recalcular_total)

        # Inicializar productos y ajustar modo inicial (arranca en Material)
        self._cargar_productos()
        self._on_tipo_changed()
        self._recalcular_total()

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

        # Alternar visibilidad de campos
        self.input_producto.setVisible(es_material)
        self.lbl_producto.setVisible(es_material)

        self.input_desc.setVisible(not es_material)
        self.lbl_desc.setVisible(not es_material)

        # En Material: sugerimos unidad y precio desde el producto, PERO la unidad queda editable
        if es_material:
            if self.input_producto.count() == 0:
                self._cargar_productos()
            self._on_producto_changed()  # sincroniza unidad/precio según producto
        # En no Material no forzamos nada adicional

        # Recalcular total por si cambia el modo
        self._recalcular_total()

    def _on_producto_changed(self):
        """Cuando cambia el producto, autocompleta unidad (sugerida) y precio de referencia."""
        idx = self.input_producto.currentIndex()
        if idx < 0 or idx >= len(self._productos_cache):
            return

        _, _, unidad, precio_ref = self._productos_cache[idx]

        # Sugerir unidad (pero el usuario la puede cambiar)
        if unidad:
            # buscar en opciones existentes (case-insensitive)
            found = False
            for i in range(self.input_unidad.count()):
                if self.input_unidad.itemText(i).lower() == unidad.lower():
                    self.input_unidad.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.input_unidad.insertItem(0, unidad)
                self.input_unidad.setCurrentIndex(0)

        # Setear precio de referencia (editable por el usuario)
        self._precio_bloqueado = True
        try:
            self.input_precio.setValue(float(precio_ref or 0))
        finally:
            self._precio_bloqueado = False

        self._recalcular_total()

    def _recalcular_total(self):
        # La BD calcula costo_total definitivo; aquí solo mostramos el estimado
        if self._precio_bloqueado:
            return
        cantidad = float(self.input_cantidad.value())
        precio = float(self.input_precio.value())
        total = round(cantidad * precio, 2)
        # Mostrar
        self.input_total.setText(f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # ----------------- API pública -----------------
    def _submit(self):
        datos = self.datos()

        # Validaciones según reglas
        if datos["tipo"].lower() == "material":
            if not datos["id_producto"]:
                QMessageBox.warning(self, "Validación", "Seleccioná un producto para el gasto de Material.")
                return
            if datos["cantidad"] <= 0:
                QMessageBox.warning(self, "Validación", "La cantidad debe ser mayor a 0.")
                return
        else:
            if not datos["descripcion"]:
                QMessageBox.warning(self, "Validación", "Ingresá una descripción para el gasto.")
                return

        # Al guardar con tipo=Material y tener id_producto, el trigger tg_sync_gasto_a_consumo
        # se encargará de registrar en obras_consumos automáticamente.
        if callable(self.on_submit):
            self.on_submit(datos)

    def _cancel(self):
        if callable(self.on_cancel):
            self.on_cancel()

    def datos(self):
        """Devuelve dict listo para inserción. Incluye:
           - concepto: autogenerado para Material, desde descripción para no Material
           - tipo, unidad, cantidad, costo_unitario, fecha, id_producto (o None)
           - total (solo referencia UI)
        """
        cantidad = float(self.input_cantidad.value())
        precio = float(self.input_precio.value())
        total = round(cantidad * precio, 2)

        es_material = (self.input_tipo.currentText().lower() == "material")

        id_producto = None
        nombre_producto = ""
        if self.input_producto.isVisible() and self.input_producto.currentIndex() >= 0 and self.input_producto.count() > 0:
            id_producto = self.input_producto.currentData()
            nombre_producto = self.input_producto.currentText().strip()

        if es_material:
            concepto = f"Material: {nombre_producto}" if nombre_producto else "Material"
            descripcion = ""  # no se usa en Material
        else:
            concepto = self.input_desc.text().strip()
            descripcion = concepto

        return {
            # Esquema DB
            "concepto": concepto,
            "tipo": self.input_tipo.currentText(),
            "unidad": self.input_unidad.currentText().strip(),
            "cantidad": cantidad,
            "costo_unitario": precio,
            "fecha": self.input_fecha.date().toPython(),  # date nativo
            "id_producto": id_producto,  # None si no aplica

            # Compat: usado por vistas/handlers existentes en tu app
            "descripcion": descripcion,
            "usa_producto": es_material,
            "precio": precio,
            "total": total,
        }

    def limpiar(self):
        self.input_tipo.setCurrentIndex(0)
        if self.input_producto.count() > 0:
            self.input_producto.setCurrentIndex(0)
        self.input_desc.clear()
        self.input_unidad.setCurrentIndex(0)
        self.input_cantidad.setValue(1)
        self.input_precio.setValue(0)
        self.input_total.setText("0.00")
        self.input_fecha.setDate(QDate.currentDate())
        self._on_tipo_changed()

    def focusIn(self):
        if self.input_tipo.currentText().lower() == "material":
            self.input_producto.setFocus()
        else:
            self.input_desc.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = GastoFormWidget(lambda d: print("SUBMIT:", d), lambda: print("CANCEL"))
    ui.show()
    sys.exit(app.exec())
