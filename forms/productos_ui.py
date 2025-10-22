# productos_willow.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
import platform

from PySide6.QtCore import Qt, QSize, QCoreApplication, QMetaObject, QObject, QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,
    QMessageBox, QFileDialog, QLineEdit, QSizePolicy
)

from forms.agregarProductos import Ui_Form as AgregarProductoForm
from db.conexion import conexion
from reports.excel import export_qtable_to_excel

# === Helpers existentes ===
from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search
)

OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ICON_PX = 18
  # ancho mínimo para columna Opciones


# =================== Helper de íconos (Tabler) ===================
def _detect_desktop() -> Path:
    home = Path.home()
    if platform.system().lower().startswith("win"):
        for env in ("ONEDRIVE", "OneDrive", "OneDriveConsumer"):
            od = os.environ.get(env)
            if od:
                d = Path(od) / "Desktop"
                if d.exists():
                    return d
        d = Path(os.environ.get("USERPROFILE", str(home))) / "Desktop"
        return d if d.exists() else home
    d = home / "Desktop"
    return d if d.exists() else home


def _icon_dirs() -> list[Path]:
    desktop = _detect_desktop()
    project_dir = Path(__file__).resolve().parent.parent
    return [
        desktop / "sistema-informatico" / "rodlerIcons",
        desktop / "rodlerIcons",
        project_dir / "rodlerIcons",
    ]


def _find_icon_path(name: str) -> Path | None:
    for base in _icon_dirs():
        p = base / f"{name}.svg"
        if p.exists():
            return p
    return None


from main.themes import themed_icon

def icon(name: str) -> QIcon:
    # Theme-aware icon (white in dark mode)
    return themed_icon(name)


# =================== ESTILOS (Willow base) ===================
QSS_RODLER = """
/* Base y tipografía */
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background: transparent; }

/* Cards suaves */
#card, QTableWidget {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Barra superior */
#headerCard {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Título */
QLabel[role="pageTitle"] { font-size:18px; font-weight:800; color:#0F172A; }

/* Buscador */
QLineEdit#searchBox {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:10px;
  padding:8px 12px;
}
QLineEdit#searchBox:focus { border-color:#90CAF9; }

/* Inputs del formulario */
QLineEdit, QComboBox {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:10px;
  padding:6px 10px;
  min-height:28px;
}
QLineEdit:focus, QComboBox:focus {
  border:1px solid #90CAF9;
  background:#FFFFFF;
}

/* Botones "grandes" fuera de la tabla */
QPushButton[type="primary"] {
  background:#2979FF;
  border:1px solid #2979FF;
  color:#FFFFFF;
  border-radius:10px;
  padding:8px 12px;
  qproperty-iconSize: 18px 18px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

/* Tabla */
QTableWidget {
  gridline-color:#E8EEF6;
  selection-background-color: rgba(41,121,255,.15);
  selection-color:#0F172A;
}
QHeaderView::section {
  background:#F8FAFF;
  color:#0F172A;
  padding:10px;
  border:none;
  border-right:1px solid #E8EEF6;
}
QTableWidget::item { padding:6px; }

/* Asegurar que contenedores en celdas no pinten gris */
QTableWidget QWidget { background: transparent; border: none; }
"""


class _ResizeWatcher(QObject):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner.ajustar_columnas()
        return False


# ===== helper: estilo local (sobrescribe cualquier QSS global) =====

def _style_action_button(btn: QPushButton, kind: str):
    """Configura botones de acción usando variantes del tema."""
    btn.setText("")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(BTN_MIN_HEIGHT)
    btn.setIconSize(QSize(ICON_PX, ICON_PX))
    btn.setProperty("type", "icon")
    if kind == "edit":
        btn.setProperty("variant", "edit")
        btn.setIcon(icon("edit"))
        btn.setToolTip("Editar producto")
    else:
        btn.setProperty("variant", "delete")
        btn.setIcon(icon("trash"))
        btn.setToolTip("Eliminar producto")
    btn.style().unpolish(btn); btn.style().polish(btn)



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
        self.headerFrame.setObjectName("headerCard")
        self.headerFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.headerLayout = QHBoxLayout(self.headerFrame)
        self.headerLayout.setContentsMargins(16, 12, 16, 12)
        self.headerLayout.setSpacing(10)

        self.label = QLabel(self.headerFrame)
        self.label.setText("Productos")
        self.label.setProperty("role", "pageTitle")
        mark_title(self.label)
        self.headerLayout.addWidget(self.label)
        self.headerLayout.addStretch(1)

        # Buscador
        self.searchBox = QLineEdit(self.headerFrame)
        self.searchBox.setObjectName("searchBox")
        self.searchBox.setPlaceholderText("Buscar por nombre o proveedor…")
        self.searchBox.setClearButtonEnabled(True)
        self.searchBox.setMinimumWidth(260)
        self.searchBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        style_search(self.searchBox)
        self.searchBox.addAction(icon("search"), QLineEdit.LeadingPosition)
        self.searchBox.textChanged.connect(self.filtrar_tabla)
        self.headerLayout.addWidget(self.searchBox)

        # Exportar
        self.btnExportExcel = QPushButton(self.headerFrame)
        self.btnExportExcel.setMinimumSize(100, 34)
        self.btnExportExcel.setMaximumWidth(200)
        self.btnExportExcel.setText("Exportar Excel")
        self.btnExportExcel.setToolTip("Exporta la tabla visible a Excel (.xlsx)")
        self.btnExportExcel.setProperty("type", "primary")
        self.btnExportExcel.setIcon(icon("file-spreadsheet"))
        make_primary(self.btnExportExcel)
        self.btnExportExcel.clicked.connect(self.exportar_excel)

        # Agregar
        self.pushButton = QPushButton(self.headerFrame)
        self.pushButton.setMinimumSize(120, 34)
        self.pushButton.setMaximumWidth(220)
        self.pushButton.setText("Agregar producto")
        self.pushButton.setObjectName("btnProductoNuevo")               # PATCH permisos
        self.pushButton.setProperty("type", "primary")
        self.pushButton.setProperty("perm_code", "productos.create") 
        self.pushButton.setIcon(icon("plus"))
        make_primary(self.pushButton)
        self.pushButton.clicked.connect(self.mostrar_formulario)

        self.headerLayout.addWidget(self.btnExportExcel)
        a = self.headerLayout.addWidget(self.pushButton)
        self.rootLayout.addWidget(self.headerFrame)

        # ===== Tabla =====
        self.tableWidget = QTableWidget(Form)
        self.tableWidget.setObjectName("card")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Stock", "Proveedor", "Opciones"])
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setWordWrap(False)
        self.tableWidget.setAlternatingRowColors(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(44)

        header = self.tableWidget.horizontalHeader()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        style_table(self.tableWidget)
        self.rootLayout.addWidget(self.tableWidget)

        # Watcher resize
        self._resizeWatcher = _ResizeWatcher(self)
        self.tableWidget.installEventFilter(self._resizeWatcher)

        # ===== Cargar datos =====
        self.cargar_todos_los_productos()
        self._post_refresh_table()

        # ===== Estilos globales + Willow =====
        apply_global_styles(Form)
        # Styles are applied globally via main/themes

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    # ======= Exportar =======
    def exportar_excel(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Productos.xlsx", "Excel (*.xlsx)")
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

        # Forzar skin Willow sobre cualquier QSS del .ui
        self._force_willow_styles(self.widgetAgregarProducto)

        self.rootLayout.insertWidget(1, self.widgetAgregarProducto)

        if hasattr(self.uiAgregarProducto, "lineEditStock"):
            self.uiAgregarProducto.lineEditStock.setReadOnly(True)
            self.uiAgregarProducto.lineEditStock.setPlaceholderText("Solo lectura (ajustes desde Compras/Ventas/Obras/Ajustes)")
            self.uiAgregarProducto.lineEditStock.setText("0")

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

        if hasattr(self.uiAgregarProducto, "pushButton"):
            self.uiAgregarProducto.pushButton.setText("Guardar")
            self.uiAgregarProducto.pushButton.setProperty("type","primary")
            self.uiAgregarProducto.pushButton.setIcon(icon("device-floppy"))
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
            for col, valor in enumerate(producto):
                val_str = self._format_cell(col, valor)
                item = QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(row_count, col, item)
            self._colocar_botones_opciones(row_count, producto[0])
            self._post_refresh_table()
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
        self._post_refresh_table()

    def _colocar_botones_opciones(self, fila: int, id_producto: int):
        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Asegurar contenedor transparente (sin gris)
        contenedor.setAutoFillBackground(False)
        contenedor.setAttribute(Qt.WA_StyledBackground, False)
        contenedor.setAttribute(Qt.WA_NoSystemBackground, True)
        contenedor.setStyleSheet("background: transparent; border: none;")

        # Icon-only + color forzado
        btn_edit = QPushButton("")
        btn_edit.setObjectName("btnProductoEditar")                # PATCH permisos
        btn_edit.setProperty("perm_code", "productos.update") 
        btn_del  = QPushButton("")
        btn_del.setObjectName("btnProductoEliminar")               # PATCH permisos
        btn_del.setProperty("perm_code", "productos.delete")
        _style_action_button(btn_edit, "edit")
        _style_action_button(btn_del, "delete")

        btn_edit.clicked.connect(lambda _, pid=id_producto: self.mostrar_formulario_editar(pid))
        btn_del.clicked.connect(lambda _, pid=id_producto: self.eliminar_producto(pid))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        self.tableWidget.setCellWidget(fila, 5, contenedor)

    def _format_cell(self, col: int, valor):
        if col == 2:  # Precio
            try:
                v = float(valor)
                return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
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

        for fila in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(fila, 0)
            if item and int(item.text()) == id_producto:
                self.tableWidget.removeRow(fila)
                break

        self._post_refresh_table()

    # ---------- EDICIÓN ----------
    def mostrar_formulario_editar(self, id_producto):
        if hasattr(self, 'widgetEditarProducto') or hasattr(self, 'widgetAgregarProducto'):
            return

        self.widgetEditarProducto = QWidget()
        self.uiEditarProducto = AgregarProductoForm()
        self.uiEditarProducto.setupUi(self.widgetEditarProducto)

        # Forzar skin Willow
        self._force_willow_styles(self.widgetEditarProducto)

        self.rootLayout.insertWidget(1, self.widgetEditarProducto)

        if hasattr(self.uiEditarProducto, "lineEditStock"):
            self.uiEditarProducto.lineEditStock.setReadOnly(True)
            self.uiEditarProducto.lineEditStock.setPlaceholderText("Solo lectura (ajustes desde Compras/Ventas/Obras/Ajustes)")

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

        if hasattr(self.uiEditarProducto, "pushButton"):
            self.uiEditarProducto.pushButton.setText("Guardar cambios")
            self.uiEditarProducto.pushButton.setProperty("type","primary")
            self.uiEditarProducto.pushButton.setIcon(icon("device-floppy"))
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
        self._post_refresh_table()
        self.cancelar()

    # ---------- BÚSQUEDA / COLUMNAS ----------
    def filtrar_tabla(self, texto: str):
        query = (texto or "").strip().lower()
        for fila in range(self.tableWidget.rowCount()):
            nombre_item = self.tableWidget.item(fila, 1)
            prov_item = self.tableWidget.item(fila, 4)
            nombre = nombre_item.text().lower() if nombre_item else ""
            proveedor = prov_item.text().lower() if prov_item else ""
            visible = (query in nombre) or (query in proveedor)
            self.tableWidget.setRowHidden(fila, not visible)

    def ajustar_columnas(self):
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        current_width = self.tableWidget.columnWidth(5)
        if current_width < OPCIONES_MIN_WIDTH:
            self.tableWidget.setColumnWidth(5, OPCIONES_MIN_WIDTH)

    def _post_refresh_table(self):
        """Asegura estado visual consistente tras cargar/editar/borrar."""
        try:
            self.tableWidget.setColumnHidden(0, True)  # ocultar ID SIEMPRE
        except Exception:
            pass
        self.ajustar_columnas()

    # ---------- Forzado de estilos Willow en formularios ----------
    def _force_willow_styles(self, container: QWidget):
        # limpiar estilos heredados
        if container.styleSheet():
            container.setStyleSheet("")
        for child in container.findChildren(QWidget):
            if child.styleSheet():
                child.setStyleSheet("")

        apply_global_styles(container)
        # Styles are applied globally via main/themes

        for btn in container.findChildren(QPushButton):
            txt = (btn.text() or "").lower()
            if "guardar" in txt:
                btn.setProperty("type", "primary")
                make_primary(btn)
            btn.setMinimumHeight(32)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
