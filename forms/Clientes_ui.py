# clientes_willow.py — reemplaza tu módulo de Clientes por este

import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from PySide6.QtCore import (Qt, QSize, QCoreApplication, QMetaObject)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView,
    QFileDialog, QMessageBox
)

from forms.AgregarClientes import Ui_Form as FormularioClientes
from db.clientes_queries import (
    guardar_registro, cargar_clientes, buscar_clientes,
    editar_cliente, obtener_cliente_por_id
)
from reports.excel import export_qtable_to_excel

# >>> Estilos/helpers del sistema
try:
    from ui_helpers import apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search  # noqa
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search  # noqa

# ---- Constantes UI (alineadas con Productos)
ROW_HEIGHT = 46
OPCIONES_COL = 5
OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ICON_PX = 18

# ---------------- Iconos (rodlerIcons en Escritorio/OneDrive) ----------------
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

# ---------------- QSS Willow (base, sin tocar colores de icon-buttons por código) ----------------
QSS_WILLOW = """
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background: transparent; }

/* Cards blancas */
#headerCard, #tableCard, QTableWidget {
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

/* Botón primario */
QPushButton[type="primary"] {
  background:#2979FF;
  border:1px solid #2979FF;
  color:#FFFFFF;
  border-radius:10px;
  padding:8px 12px;
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

/* Garantiza que los contenedores incrustados en la tabla no pinten gris */
QTableWidget QWidget { background: transparent; border: none; }
"""

# ---------- helper de estilo para acción (igual que en Productos) ----------
def _style_action_button(btn: QPushButton, kind: str):
    """Aplica color sólido + tamaño + solo icono (igual que módulo Productos)."""
    if kind == "edit":
        # Azul sólido
        btn.setStyleSheet(
            "QPushButton{background:#2979FF;border:1px solid #2979FF;color:#FFFFFF;border-radius:8px;padding:6px;}"
            "QPushButton:hover{background:#3b86ff;}"
        )
        btn.setIcon(icon("edit"))
        btn.setToolTip("Editar cliente")
    else:
        # Rojo sólido
        btn.setStyleSheet(
            "QPushButton{background:#EF5350;border:1px solid #EF5350;color:#FFFFFF;border-radius:8px;padding:6px;}"
            "QPushButton:hover{background:#f26461;}"
        )
        btn.setIcon(icon("trash"))
        btn.setToolTip("Eliminar cliente")

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
        self.grid.setContentsMargins(12, 12, 12, 12)
        self.grid.setSpacing(10)

        # ---------------- Header (misma línea: título + search + botones) ----------------
        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16,12,16,12); hl.setSpacing(10)

        self.lblTitle = QLabel("Clientes", self.headerCard)
        self.lblTitle.setProperty("role", "pageTitle")
        mark_title(self.lblTitle)
        hl.addWidget(self.lblTitle)

        hl.addStretch(1)

        self.search = QLineEdit(self.headerCard)
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Buscar por nombre o RUC/CI…")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(280)
        self.search.addAction(icon("search"), QLineEdit.LeadingPosition)
        style_search(self.search)
        hl.addWidget(self.search, 1)

        self.btnExport = QPushButton("Exportar", self.headerCard)
        self.btnExport.setProperty("type","primary")
        self.btnExport.setIcon(icon("file-spreadsheet"))
        make_primary(self.btnExport)
        self.btnExport.clicked.connect(self.exportar_excel_clientes)
        hl.addWidget(self.btnExport)

        self.btnNuevo = QPushButton("Nuevo cliente", self.headerCard)
        self.btnNuevo.setObjectName("btnClienteNuevo")               # PATCH permisos
        self.btnNuevo.setProperty("type","primary")
        self.btnNuevo.setProperty("perm_code", "clientes.create") 
        self.btnNuevo.setIcon(icon("plus"))
        make_primary(self.btnNuevo)
        self.btnNuevo.clicked.connect(lambda: self.abrir_formulario(Form))
        hl.addWidget(self.btnNuevo)

        self.grid.addWidget(self.headerCard, 0, 0, 1, 1)

        # ---------------- Tabla ----------------
        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.tableWidget = QTableWidget(self.tableCard)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID","Nombre","Teléfono","CI/RUC","Email","Opciones"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (se oculta luego)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)

        style_table(self.tableWidget)
        tv.addWidget(self.tableWidget)
        self.grid.addWidget(self.tableCard, 1, 0, 1, 1)

        # ---------------- Datos / bindings ----------------
        self.search.textChanged.connect(
            lambda text: buscar_clientes(
                text, self.tableWidget,
                edit_callback=self.abrir_formulario_editar,
                main_form_widget=Form
            ) or self._post_refresh_table()
        )

        cargar_clientes(self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        self._post_refresh_table()

        # ---------------- Estilos globales + Willow ----------------
        apply_global_styles(Form)
        Form.setStyleSheet(QSS_WILLOW)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    # ———— Ocultar ID + aplicar estilos a botones de “Opciones” ————
    def _post_refresh_table(self):
        try:
            if self.tableWidget.columnCount() > 0:
                self.tableWidget.setColumnHidden(0, True)  # oculta ID SIEMPRE
        except Exception:
            pass

        try:
            current_width = self.tableWidget.columnWidth(OPCIONES_COL)
            if current_width < OPCIONES_MIN_WIDTH:
                self.tableWidget.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)
        except Exception:
            pass

        self._restyle_option_buttons()

    # ———— Icon-only en columna Opciones, con color y tamaño como en Productos ————
    def _restyle_option_buttons(self):
        col = OPCIONES_COL
        rows = self.tableWidget.rowCount()
        for r in range(rows):
            cell = self.tableWidget.cellWidget(r, col)
            if not cell:
                continue

            # El contenedor no debe pintar gris
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
                else:
                    continue
                # refrescar estilo QSS nativo, por las dudas
                btn.style().unpolish(btn); btn.style().polish(btn)

    # ———— Exportar ————
    def exportar_excel_clientes(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Clientes.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtable_to_excel(self.tableWidget, ruta, title="Clientes")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    # ———— Mostrar / Editar (misma lógica que tu archivo original) ————
    def cancelar(self, Form):
        if hasattr(self, 'formularioCliente') and self.formularioCliente.isVisible():
            self.formularioCliente.close()
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
        if hasattr(self, 'formularioCliente') and self.formularioCliente.isVisible():
            return
        self.ui_nuevo_cliente = FormularioClientes()
        self.formularioCliente = QWidget()
        self.ui_nuevo_cliente.setupUi(self.formularioCliente)
        self.formularioCliente.setParent(Form)
        self.formularioCliente.show()

        try:
            self.grid.removeWidget(self.headerCard)
            self.grid.removeWidget(self.tableCard)
        except Exception:
            pass

        self.grid.addWidget(self.headerCard, 1, 0, 1, 1)
        self.grid.addWidget(self.formularioCliente, 0, 0, 1, 1)
        self.grid.addWidget(self.tableCard, 2, 0, 1, 1)

        # Conectar botones del form
        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: guardar_registro(self.ui_nuevo_cliente, self.formularioCliente,
                                     self.tableWidget, self.abrir_formulario_editar, Form)
        )

    def abrir_formulario_editar(self, Form, id_cliente):
        if hasattr(self, 'formularioCliente') and self.formularioCliente.isVisible():
            self.formularioCliente.close()

        self.ui_nuevo_cliente = FormularioClientes()
        self.formularioCliente = QWidget()
        self.ui_nuevo_cliente.setupUi(self.formularioCliente)
        self.formularioCliente.setParent(Form)
        self.formularioCliente.show()

        try:
            self.grid.removeWidget(self.headerCard)
            self.grid.removeWidget(self.tableCard)
        except Exception:
            pass

        self.grid.addWidget(self.headerCard, 1, 0, 1, 1)
        self.grid.addWidget(self.formularioCliente, 0, 0, 1, 1)
        self.grid.addWidget(self.tableCard, 2, 0, 1, 1)

        # Precarga
        cli = obtener_cliente_por_id(id_cliente)
        if cli:
            _, nombre, email, telefono, ruc_ci = cli
            self.ui_nuevo_cliente.lineEditNombre.setText(nombre or "")
            self.ui_nuevo_cliente.lineEditRuc_Ci.setText(str(ruc_ci) if ruc_ci is not None else "")
            self.ui_nuevo_cliente.lineEditTelefono.setText(str(telefono) if telefono is not None else "")
            self.ui_nuevo_cliente.lineEditCorreo.setText(email or "")

        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: editar_cliente(self.ui_nuevo_cliente, self.tableWidget, id_cliente,
                                   self.formularioCliente, self.abrir_formulario_editar, Form)
        )

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Clientes"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
