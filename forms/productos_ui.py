import sys
import os
from decimal import Decimal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QCoreApplication, QMetaObject, QObject, QEvent
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,
    QMessageBox, QFileDialog, QLineEdit, QSizePolicy
)

from forms.agregarProductos import Ui_Form as AgregarProductoForm
from db.conexion import conexion
try:
    import psycopg2
    from psycopg2 import errors as pg_errors
except Exception:
    psycopg2 = None
    pg_errors = None

from reports.excel import export_qtable_to_excel

# === Estilos y helpers Rodler (paleta clara) ===
from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search
)

OPCIONES_MIN_WIDTH = 140  # ancho mínimo para Editar/Eliminar


class _ResizeWatcher(QObject):
    """Observa resizeEvent del QTableWidget para reajustar columnas."""
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner.ajustar_columnas()
        return False


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 600)

        # ===== Layout raíz =====
        self.rootLayout = QVBoxLayout(Form)
        self.rootLayout.setContentsMargins(12, 12, 12, 12)
        self.rootLayout.setSpacing(10)

        # ===== Encabezado =====
        self.headerFrame = QFrame(Form)
        self.headerFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.headerLayout = QHBoxLayout(self.headerFrame)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(10)

        self.label = QLabel(self.headerFrame)
        self.label.setText("Productos")
        mark_title(self.label)

        self.headerLayout.addWidget(self.label)
        self.headerLayout.addStretch(1)

        # Buscador
        self.searchBox = QLineEdit(self.headerFrame)
        self.searchBox.setPlaceholderText("Buscar por nombre o proveedor…")
        self.searchBox.setClearButtonEnabled(True)
        self.searchBox.setMinimumWidth(260)
        self.searchBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        style_search(self.searchBox)
        self.searchBox.textChanged.connect(self.filtrar_tabla)
        self.headerLayout.addWidget(self.searchBox)

        self.btnExportExcel = QPushButton(self.headerFrame)
        self.btnExportExcel.setMinimumSize(100, 34)
        self.btnExportExcel.setMaximumWidth(200)
        self.btnExportExcel.setText("Exportar Excel")
        self.btnExportExcel.setToolTip("Exporta la tabla visible a Excel (.xlsx)")
        make_primary(self.btnExportExcel)
        self.btnExportExcel.clicked.connect(self.exportar_excel)

        self.pushButton = QPushButton(self.headerFrame)
        self.pushButton.setMinimumSize(120, 34)
        self.pushButton.setMaximumWidth(220)
        self.pushButton.setText("Agregar producto")
        self.pushButton.setCursor(Qt.PointingHandCursor)
        make_primary(self.pushButton)
        self.pushButton.clicked.connect(self.mostrar_formulario)

        self.headerLayout.addWidget(self.btnExportExcel)
        self.headerLayout.addWidget(self.pushButton)
        self.rootLayout.addWidget(self.headerFrame)

        # ===== Tabla =====
        self.tableWidget = QTableWidget(Form)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Stock", "Proveedor", "Opciones"])
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setWordWrap(False)
        self.tableWidget.setAlternatingRowColors(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(44)
        self.tableWidget.setColumnHidden(0, True)  # Oculta ID

        header = self.tableWidget.horizontalHeader()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)

        # Modo de resize: 1..4 Stretch (mismo tamaño); 5 Opciones a contenido
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (oculto)
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Precio
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Stock
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Proveedor
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Opciones (pequeña)

        style_table(self.tableWidget)  # aplica estilo de headers/bordes/selección
        self.rootLayout.addWidget(self.tableWidget)

        # Watcher para recalcular columnas cuando la tabla cambia de tamaño
        self._resizeWatcher = _ResizeWatcher(self)
        self.tableWidget.installEventFilter(self._resizeWatcher)

        # ===== Cargar datos =====
        self.cargar_todos_los_productos()
        self.ajustar_columnas()  # asegura tamaños iniciales

        # ===== Estilos globales del módulo =====
        apply_global_styles(Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)


    # ======= Exportar =======
    def exportar_excel(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(
                None,
                "Guardar como",
                "Productos.xlsx",
                "Excel (*.xlsx)"
            )
            if not ruta:
                return
            export_qtable_to_excel(self.tableWidget, ruta, title="Productos")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")


    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Productos"))


    # ---------- ALTA ----------
    def mostrar_formulario(self):
        if hasattr(self, 'widgetAgregarProducto') or hasattr(self, 'widgetEditarProducto'):
            return

        self.widgetAgregarProducto = QWidget()
        self.uiAgregarProducto = AgregarProductoForm()
        self.uiAgregarProducto.setupUi(self.widgetAgregarProducto)
        apply_global_styles(self.widgetAgregarProducto)  # hereda estilos del helper
        self.rootLayout.insertWidget(1, self.widgetAgregarProducto)

        # 👉 stock solo lectura en el formulario de ALTA
        if hasattr(self.uiAgregarProducto, "lineEditStock"):
            self.uiAgregarProducto.lineEditStock.setReadOnly(True)
            self.uiAgregarProducto.lineEditStock.setPlaceholderText("Solo lectura (ajustes desde Compras/Ventas/Obras/Ajustes)")
            self.uiAgregarProducto.lineEditStock.setText("0")

        # cargar proveedores
        try:
            with conexion() as conexion_db:
                with conexion_db.cursor() as cursor:
                    cursor.execute("SELECT id_proveedor, nombre FROM proveedores;")
                    proveedores = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudieron cargar proveedores:\n{e}")
            return

        self.uiAgregarProducto.comboBoxProveedore.clear()
        for id_proveedor, nombre in proveedores:
            self.uiAgregarProducto.comboBoxProveedore.addItem(nombre, id_proveedor)

        # botones del form
        if hasattr(self.uiAgregarProducto, "pushButton"):
            self.uiAgregarProducto.pushButton.setText("Guardar")
            make_primary(self.uiAgregarProducto.pushButton)
        if hasattr(self.uiAgregarProducto, "pushButton_2"):
            self.uiAgregarProducto.pushButton_2.setText("Cancelar")
        self.uiAgregarProducto.pushButton_2.clicked.connect(self.cancelar)
        self.uiAgregarProducto.pushButton.clicked.connect(self.aceptar)


    def cancelar(self):
        if hasattr(self, 'widgetAgregarProducto'):
            self.rootLayout.removeWidget(self.widgetAgregarProducto)
            self.widgetAgregarProducto.deleteLater()
            del self.widgetAgregarProducto
        if hasattr(self, 'widgetEditarProducto'):
            self.rootLayout.removeWidget(self.widgetEditarProducto)
            self.widgetEditarProducto.deleteLater()
            del self.widgetEditarProducto


    def aceptar(self):
        nombre = self.uiAgregarProducto.lineEditNombre.text().strip()
        precio_txt = self.uiAgregarProducto.lineEditPrecio.text().strip()
        proveedor = self.uiAgregarProducto.comboBoxProveedore.currentData()
        descripcion = self.uiAgregarProducto.lineEditDescripcion.text().strip() if hasattr(self.uiAgregarProducto, 'lineEditDescripcion') else None

        if not nombre:
            QMessageBox.warning(None, "Validación", "Nombre es obligatorio.")
            return
        try:
            precio = float(precio_txt)
        except Exception:
            QMessageBox.warning(None, "Validación", "Precio inválido.")
            return

        # Crea con stock_actual = 0 (no se permite setear stock desde este módulo)
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO productos (nombre, precio_venta, stock_actual, id_proveedor, descripcion)
                        VALUES (%s, %s, 0, %s, %s)
                        RETURNING id_producto;
                        """,
                        (nombre, precio, proveedor, descripcion)
                    )
                    id_producto = cur.fetchone()[0]
                c.commit()
            self.cargar_datos(id_producto)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo crear el producto:\n{e}")


    def cargar_datos(self, id_producto):
        try:
            with conexion() as conexion_db:
                with conexion_db.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT p.id_producto, p.nombre, p.precio_venta, p.stock_actual, pr.nombre AS proveedor
                        FROM productos p
                        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
                        WHERE p.id_producto = %s;
                        """, (id_producto,)
                    )
                    producto = cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo cargar el producto {id_producto}:\n{e}")
            return

        if producto:
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)

            # ID, Nombre, Precio, Stock, Proveedor
            for col, valor in enumerate(producto):
                val_str = self._format_cell(col, valor)
                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row_count, col, item)

            self._colocar_botones_opciones(row_count, producto[0])
            self.ajustar_columnas()
            self.cancelar()


    def cargar_todos_los_productos(self):
        try:
            with conexion() as conexion_db:
                with conexion_db.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT p.id_producto, p.nombre, p.precio_venta, p.stock_actual, pr.nombre AS proveedor
                        FROM productos p
                        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor;
                        """
                    )
                    productos = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudieron cargar productos:\n{e}")
            return

        self.tableWidget.setRowCount(0)
        for producto in productos:
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)

            for col, valor in enumerate(producto):
                val_str = self._format_cell(col, valor)
                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row_count, col, item)

            self._colocar_botones_opciones(row_count, producto[0])

        self.ajustar_columnas()


    def _colocar_botones_opciones(self, fila: int, id_producto: int):
        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        boton_editar = QPushButton("Editar")
        boton_eliminar = QPushButton("Eliminar")

        make_primary(boton_editar)
        make_danger(boton_eliminar)

        boton_editar.setMinimumHeight(28)
        boton_eliminar.setMinimumHeight(28)

        boton_editar.clicked.connect(lambda _, pid=id_producto: self.mostrar_formulario_editar(pid))
        boton_eliminar.clicked.connect(lambda _, pid=id_producto: self.eliminar_producto(pid))

        layout.addWidget(boton_editar)
        layout.addWidget(boton_eliminar)
        self.tableWidget.setCellWidget(fila, 5, contenedor)


    def _format_cell(self, col: int, valor):
        """Formatea celdas para mejor legibilidad (precio con 2 decimales)."""
        if col == 2:  # Precio
            try:
                v = float(valor)
                return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # formato 1.234,56
            except Exception:
                return str(valor)
        return str(valor)


    def eliminar_producto(self, id_producto):
        confirm = QMessageBox.question(
            None, "Eliminar",
            f"¿Eliminar el producto {id_producto}? Si tiene movimientos/ventas/compras no se podrá borrar.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            with conexion() as c:
                with c.cursor() as cur:
                    # pre-chequeo amigable
                    cur.execute("SELECT EXISTS (SELECT 1 FROM movimientos_stock WHERE id_producto=%s LIMIT 1);", (id_producto,))
                    tiene_kardex = cur.fetchone()[0]
                    cur.execute("SELECT EXISTS (SELECT 1 FROM ventas_detalle WHERE id_producto=%s LIMIT 1);", (id_producto,))
                    en_ventas = cur.fetchone()[0]
                    cur.execute("SELECT EXISTS (SELECT 1 FROM compra_detalles WHERE id_producto=%s LIMIT 1);", (id_producto,))
                    en_compras = cur.fetchone()[0]

                    if tiene_kardex or en_ventas or en_compras:
                        msg = "No se puede eliminar el producto porque:\n"
                        if tiene_kardex: msg += "• Tiene movimientos en el kardex (movimientos_stock)\n"
                        if en_ventas:    msg += "• Está usado en ventas_detalle\n"
                        if en_compras:   msg += "• Está usado en compra_detalles\n"
                        msg += "\nSugerencia: marcar como Inactivo/oculto en lugar de borrar."
                        QMessageBox.warning(None, "No se puede eliminar", msg)
                        return

                    cur.execute("DELETE FROM productos WHERE id_producto = %s;", (id_producto,))
                c.commit()
        except Exception as e:
            QMessageBox.critical(None, "No se pudo eliminar", f"El producto {id_producto} no pudo eliminarse.\nDetalle: {e}")
            return

        # quitar de la UI
        for fila in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(fila, 0)
            if item and int(item.text()) == id_producto:
                self.tableWidget.removeRow(fila)
                break

        self.ajustar_columnas()


    # ---------- EDICIÓN ----------
    def mostrar_formulario_editar(self, id_producto):
        if hasattr(self, 'widgetEditarProducto') or hasattr(self, 'widgetAgregarProducto'):
            return

        self.widgetEditarProducto = QWidget()
        self.uiEditarProducto = AgregarProductoForm()
        self.uiEditarProducto.setupUi(self.widgetEditarProducto)
        apply_global_styles(self.widgetEditarProducto)
        self.rootLayout.insertWidget(1, self.widgetEditarProducto)

        # 👉 stock solo lectura también en EDICIÓN
        if hasattr(self.uiEditarProducto, "lineEditStock"):
            self.uiEditarProducto.lineEditStock.setReadOnly(True)
            self.uiEditarProducto.lineEditStock.setPlaceholderText("Solo lectura (ajustes desde Compras/Ventas/Obras/Ajustes)")

        # leer datos actuales
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute(
                        "SELECT nombre, precio_venta, stock_actual, descripcion, id_proveedor FROM productos WHERE id_producto = %s;",
                        (id_producto,)
                    )
                    producto = cur.fetchone()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo leer el producto:\n{e}")
            return

        if not producto:
            QMessageBox.warning(None, "Aviso", "Producto no encontrado.")
            return

        nombre, precio, stock_db, descripcion, proveedor = producto

        self.uiEditarProducto.lineEditNombre.setText(nombre)
        self.uiEditarProducto.lineEditPrecio.setText(str(precio))
        self.uiEditarProducto.lineEditStock.setText(str(stock_db))
        if hasattr(self.uiEditarProducto, 'lineEditDescripcion') and descripcion is not None:
            self.uiEditarProducto.lineEditDescripcion.setText(descripcion)

        # proveedores
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute("SELECT id_proveedor, nombre FROM proveedores;")
                    proveedores = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo cargar proveedores:\n{e}")
            return

        self.uiEditarProducto.comboBoxProveedore.clear()
        for idp, nombrep in proveedores:
            self.uiEditarProducto.comboBoxProveedore.addItem(nombrep, idp)
            if idp == proveedor:
                self.uiEditarProducto.comboBoxProveedore.setCurrentIndex(self.uiEditarProducto.comboBoxProveedore.count()-1)

        # botones del form
        if hasattr(self.uiEditarProducto, "pushButton"):
            self.uiEditarProducto.pushButton.setText("Guardar cambios")
            make_primary(self.uiEditarProducto.pushButton)
        if hasattr(self.uiEditarProducto, "pushButton_2"):
            self.uiEditarProducto.pushButton_2.setText("Cancelar")
        self.uiEditarProducto.pushButton_2.clicked.connect(self.cancelar)
        self.uiEditarProducto.pushButton.clicked.connect(lambda: self.editar_producto(id_producto))


    def editar_producto(self, id_producto):
        nombre = self.uiEditarProducto.lineEditNombre.text().strip()
        precio_txt = self.uiEditarProducto.lineEditPrecio.text().strip()
        proveedor = self.uiEditarProducto.comboBoxProveedore.currentData()
        descripcion = self.uiEditarProducto.lineEditDescripcion.text().strip() if hasattr(self.uiEditarProducto, 'lineEditDescripcion') else None

        try:
            precio = float(precio_txt)
        except Exception:
            QMessageBox.warning(None, "Validación", "Precio inválido.")
            return

        # actualizar SOLO datos base (stock no se toca aquí)
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE productos
                        SET nombre=%s, precio_venta=%s, id_proveedor=%s, descripcion=%s
                        WHERE id_producto=%s;
                        """,
                        (nombre, precio, proveedor, descripcion, id_producto)
                    )
                c.commit()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo actualizar el producto:\n{e}")
            return

        # refrescar fila
        self.tableWidget.setSortingEnabled(False)
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute(
                        """
                        SELECT p.id_producto, p.nombre, p.precio_venta, p.stock_actual, pr.nombre AS proveedor
                        FROM productos p
                        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
                        WHERE p.id_producto = %s;
                        """, (id_producto,)
                    )
                    prod = cur.fetchone()
        except Exception as e:
            QMessageBox.warning(None, "Aviso", f"Actualizado, pero no se pudo refrescar la tabla:\n{e}")
            self.cancelar()
            return

        if prod:
            for fila in range(self.tableWidget.rowCount()):
                item_id = self.tableWidget.item(fila, 0)
                if item_id and int(item_id.text()) == id_producto:
                    self.tableWidget.item(fila, 1).setText(str(prod[1]))
                    self.tableWidget.item(fila, 2).setText(self._format_cell(2, prod[2]))
                    self.tableWidget.item(fila, 3).setText(str(prod[3]))
                    self.tableWidget.item(fila, 4).setText(str(prod[4]))
                    break

        self.tableWidget.setSortingEnabled(True)
        self.ajustar_columnas()
        self.cancelar()


    # ---------- BÚSQUEDA / COLUMNAS ----------
    def filtrar_tabla(self, texto: str):
        """Filtra por Nombre (col 1) o Proveedor (col 4)."""
        query = (texto or "").strip().lower()
        for fila in range(self.tableWidget.rowCount()):
            nombre_item = self.tableWidget.item(fila, 1)
            prov_item = self.tableWidget.item(fila, 4)
            nombre = nombre_item.text().lower() if nombre_item else ""
            proveedor = prov_item.text().lower() if prov_item else ""
            visible = (query in nombre) or (query in proveedor)
            self.tableWidget.setRowHidden(fila, not visible)

    def ajustar_columnas(self):
        """Asegura columnas iguales (1..4) y opciones más chica."""
        header = self.tableWidget.horizontalHeader()
        # Igualar 1..4 como Stretch y que ocupen el espacio disponible
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        # Opciones a contenido con mínimo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        # Asegurar mínimo de opciones
        current_width = self.tableWidget.columnWidth(5)
        if current_width < OPCIONES_MIN_WIDTH:
            self.tableWidget.setColumnWidth(5, OPCIONES_MIN_WIDTH)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
