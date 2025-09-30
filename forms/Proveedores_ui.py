# proveedores_willow.py  — reemplaza tu archivo de Proveedores por este

import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path

from PySide6.QtCore import (Qt, QSize, QCoreApplication, QMetaObject)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QHeaderView,
    QFileDialog, QMessageBox
)

from forms.agregarProveedor import Ui_Form as FormularioProv
from db.prov_queries import (
    guardar_registro, cargar_proveedores, buscar_proveedores,
    editar_proveedor, obtener_proveedor_por_id
)

# ==== Estilos/helpers del sistema (compat) ====
try:
    from ui_helpers import apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search

from reports.excel import export_qtable_to_excel

ROW_HEIGHT = 46
OPCIONES_COL = 5
OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ICON_PX = 18

# ------------- Iconos (carpeta rodlerIcons en Escritorio/OneDrive) -------------
def _desktop_dir() -> Path:
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

ICON_DIR = _desktop_dir() / "sistema-informatico" / "rodlerIcons"
def icon(name: str) -> QIcon:
    p = ICON_DIR / f"{name}.svg"
    return QIcon(str(p)) if p.exists() else QIcon()

# ------------- QSS Willow (idéntico a la base) -------------
QSS_WILLOW = """
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background: transparent; }

/* Card blanca */
#headerCard, #tableCard, QTableWidget {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Título de página */
QLabel[role="pageTitle"] { font-size:18px; font-weight:800; color:#0F172A; }

/* Buscador */
QLineEdit#searchBox {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:10px;
  padding:8px 12px;
}
QLineEdit#searchBox:focus { border-color:#90CAF9; }

/* Botón primario azul */
QPushButton[type="primary"] {
  background:#2979FF;
  border:1px solid #2979FF;
  color:#FFFFFF;
  border-radius:10px;
  padding:8px 12px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

/* Tabla estilo Willow */
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

/* Evitar fondo gris en contenedores dentro de celdas */
QTableWidget QWidget { background: transparent; border: none; }
"""

# ---------- helper de estilo para acción (igual que Productos/Ventas) ----------
def _style_action_button(btn: QPushButton, kind: str):
    if kind == "edit":
        # Azul sólido
        btn.setStyleSheet(
            "QPushButton{background:#2979FF;border:1px solid #2979FF;color:#FFFFFF;border-radius:8px;padding:6px;}"
            "QPushButton:hover{background:#3b86ff;}"
        )
        btn.setIcon(icon("edit"))
        btn.setToolTip("Editar proveedor")
    else:
        # Rojo sólido
        btn.setStyleSheet(
            "QPushButton{background:#EF5350;border:1px solid #EF5350;color:#FFFFFF;border-radius:8px;padding:6px;}"
            "QPushButton:hover{background:#f26461;}"
        )
        btn.setIcon(icon("trash"))
        btn.setToolTip("Eliminar proveedor")
    btn.setText("")  # icon-only
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(BTN_MIN_HEIGHT)
    btn.setIconSize(QSize(ICON_PX, ICON_PX))


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 680)

        self.grid = QGridLayout(Form)
        self.grid.setContentsMargins(12,12,12,12)
        self.grid.setSpacing(10)

        # ---------- Header (título + buscador + botones) ----------
        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        h = QHBoxLayout(self.headerCard); h.setContentsMargins(16,12,16,12); h.setSpacing(10)

        self.lblTitle = QLabel("Proveedores", self.headerCard)
        self.lblTitle.setProperty("role","pageTitle")
        mark_title(self.lblTitle)
        h.addWidget(self.lblTitle)

        h.addStretch(1)

        self.search = QLineEdit(self.headerCard)
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Buscar por nombre, teléfono o email…")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(280)
        self.search.addAction(icon("search"), QLineEdit.LeadingPosition)
        style_search(self.search)
        h.addWidget(self.search, 1)

        self.btnExport = QPushButton("Exportar", self.headerCard)
        self.btnExport.setProperty("type","primary")
        self.btnExport.setIcon(icon("file-spreadsheet"))
        self.btnExport.clicked.connect(self.exportar_excel_proveedores)
        make_primary(self.btnExport)
        h.addWidget(self.btnExport)

        self.btnNuevo = QPushButton("Nuevo proveedor", self.headerCard)
        self.btnNuevo.setProperty("type","primary")
        self.btnNuevo.setIcon(icon("plus"))
        self.btnNuevo.clicked.connect(lambda: self.abrir_formulario(Form))
        make_primary(self.btnNuevo)
        h.addWidget(self.btnNuevo)

        self.grid.addWidget(self.headerCard, 0, 0, 1, 1)

        # ---------- Tabla ----------
        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.table = QTableWidget(self.tableCard)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID","Nombre","Teléfono","Dirección","Email","Opciones"])
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (se oculta luego)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)

        style_table(self.table)
        tv.addWidget(self.table)
        self.grid.addWidget(self.tableCard, 1, 0, 1, 1)

        # ---------- Data bindings ----------
        self.search.textChanged.connect(
            lambda text: buscar_proveedores(
                text, self.table,
                edit_callback=self.abrir_formulario_editar,
                main_form_widget=Form
            ) or self._post_refresh_table()
        )

        cargar_proveedores(self.table, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        self._post_refresh_table()

        # ---------- Estilos globales + Willow ----------
        apply_global_styles(Form)
        Form.setStyleSheet(QSS_WILLOW)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    # ————————— Post-refresco: ocultar ID + colorear botones —————————
    def _post_refresh_table(self):
        # Ocultar SIEMPRE la columna ID
        try:
            if self.table.columnCount() > 0:
                self.table.setColumnHidden(0, True)
        except Exception:
            pass

        # Ajustar ancho de Opciones
        try:
            current_width = self.table.columnWidth(OPCIONES_COL)
            if current_width < OPCIONES_MIN_WIDTH:
                self.table.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)
        except Exception:
            pass

        # Aplicar estilo a botones Editar/Eliminar
        self._colorize_option_buttons()

    def _colorize_option_buttons(self):
        rows = self.table.rowCount()
        for r in range(rows):
            cell = self.table.cellWidget(r, OPCIONES_COL)
            if not cell:
                continue

            # Contenedor sin fondo/sombra
            try:
                cell.setAutoFillBackground(False)
                cell.setAttribute(Qt.WA_StyledBackground, False)
                cell.setAttribute(Qt.WA_NoSystemBackground, True)
                cell.setStyleSheet("background: transparent; border: none;")
            except Exception:
                pass

            for btn in cell.findChildren(QPushButton):
                txt = (btn.text() or "").lower()
                if "edit" in txt or "editar" in txt:
                    _style_action_button(btn, "edit")
                elif "del" in txt or "elimin" in txt or "borrar" in txt:
                    _style_action_button(btn, "del")
                # refrescar estilo
                btn.style().unpolish(btn); btn.style().polish(btn)

    # ————————— Exportar —————————
    def exportar_excel_proveedores(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Proveedores.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtable_to_excel(self.table, ruta, title="Proveedores")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    # ————————— Formularios (con tu misma lógica) —————————
    def cancelar(self, Form):
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            self.formularioProveedor.close()
        try:
            self.grid.removeWidget(self.headerCard)
            self.grid.removeWidget(self.tableCard)
        except Exception:
            pass
        try:
            self.grid.addWidget(self.headerCard, 0, 0, 1, 1)
            self.grid.addWidget(self.tableCard, 1, 0, 1, 1)
        except Exception:
            pass

    def abrir_formulario(self, Form):
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            return
        self.ui_nuevo_proveedor = FormularioProv()
        self.formularioProveedor = QWidget()
        self.ui_nuevo_proveedor.setupUi(self.formularioProveedor)
        self.formularioProveedor.setParent(Form)
        self.formularioProveedor.show()

        try:
            self.grid.removeWidget(self.headerCard)
            self.grid.removeWidget(self.tableCard)
        except Exception:
            pass

        self.grid.addWidget(self.headerCard, 1, 0, 1, 1)
        self.grid.addWidget(self.formularioProveedor, 0, 0, 1, 1)
        self.grid.addWidget(self.tableCard, 2, 0, 1, 1)

        # Conectar botones del formulario
        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(
            lambda: guardar_registro(self.ui_nuevo_proveedor, self.formularioProveedor,
                                     self.table, self.abrir_formulario_editar, Form)
        )

    def abrir_formulario_editar(self, Form, id_proveedor):
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            self.formularioProveedor.close()

        self.ui_nuevo_proveedor = FormularioProv()
        self.formularioProveedor = QWidget()
        self.ui_nuevo_proveedor.setupUi(self.formularioProveedor)
        self.formularioProveedor.setParent(Form)
        self.formularioProveedor.show()

        try:
            self.grid.removeWidget(self.headerCard)
            self.grid.removeWidget(self.tableCard)
        except Exception:
            pass

        self.grid.addWidget(self.headerCard, 1, 0, 1, 1)
        self.grid.addWidget(self.formularioProveedor, 0, 0, 1, 1)
        self.grid.addWidget(self.tableCard, 2, 0, 1, 1)

        # Precarga de datos
        prov = obtener_proveedor_por_id(id_proveedor)
        if prov:
            _, nombre, tel, dire, mail = prov
            self.ui_nuevo_proveedor.lineEditNombre.setText(nombre)
            self.ui_nuevo_proveedor.lineEditTelefono.setText(str(tel))
            self.ui_nuevo_proveedor.lineEditDireccion.setText(dire)
            self.ui_nuevo_proveedor.lineEditCorreo.setText(mail)

        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(
            lambda: editar_proveedor(self.ui_nuevo_proveedor, self.table, id_proveedor,
                                     self.formularioProveedor, self.abrir_formulario_editar, Form)
        )

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Proveedores"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
