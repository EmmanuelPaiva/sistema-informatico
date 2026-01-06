import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from PySide6.QtCore import Qt, QSize, QCoreApplication, QMetaObject, QTimer
from PySide6.QtGui import QIcon, QFont
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

try:
    from ui_helpers import (
        apply_global_styles, mark_title, make_primary, make_danger,
        style_table, style_search, style_edit_button, style_delete_button
    )
except ModuleNotFoundError:
    from forms.ui_helpers import (
        apply_global_styles, mark_title, make_primary, make_danger,
        style_table, style_search, style_edit_button, style_delete_button
    )

from reports.excel import export_qtable_to_excel

ROW_HEIGHT = 46
OPCIONES_COL = 5
OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ICON_PX = 18

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

from main.themes import themed_icon

ICON_DIR = _desktop_dir() / "sistema-informatico" / "rodlerIcons"
def icon(name: str) -> QIcon:
    return themed_icon(name)

def _style_action_button(btn: QPushButton, kind: str):
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(BTN_MIN_HEIGHT)
    btn.setIconSize(QSize(ICON_PX, ICON_PX))
    if kind == "edit":
        # Propiedades que suelen enganchar el QSS pastel
        btn.setProperty("variant", "edit")
        btn.setProperty("tone", "pastel")
        style_edit_button(btn, "Editar proveedor")
    else:
        btn.setProperty("variant", "danger")  # o "delete" según tu QSS
        btn.setProperty("tone", "pastel")
        style_delete_button(btn, "Eliminar proveedor")
    # Re-evaluar estilo tras setear propiedades
    btn.style().unpolish(btn)
    btn.style().polish(btn)
    btn.update()

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 680)
        self._form_main = Form

        self.grid = QGridLayout(Form)
        self.grid.setContentsMargins(12,12,12,12)
        self.grid.setSpacing(10)

        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        h = QHBoxLayout(self.headerCard); h.setContentsMargins(16,12,16,12); h.setSpacing(10)

        self.lblTitle = QLabel("proveedores", self.headerCard)
        self.lblTitle.setObjectName("proveedoresTitle")
        self.lblTitle.setProperty("role","pageTitle")
        f = QFont(self.lblTitle.font()); f.setBold(False); f.setPointSize(26)
        self.lblTitle.setFont(f)
        mark_title(self.lblTitle)
        self.lblTitle.setStyleSheet("""
            #proveedoresTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
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
        self.btnNuevo.setObjectName("btnProveedorNuevo")
        self.btnNuevo.setProperty("perm_code", "proveedores.create")
        self.btnNuevo.setProperty("type","primary")
        self.btnNuevo.setIcon(icon("plus"))
        self.btnNuevo.clicked.connect(lambda: self.abrir_formulario(Form))
        make_primary(self.btnNuevo)
        h.addWidget(self.btnNuevo)

        self.grid.addWidget(self.headerCard, 0, 0, 1, 1)

        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.table = QTableWidget(self.tableCard)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID","Nombre","Teléfono","Dirección","Email","Opciones"])
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)
        try:
            header.setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass

        style_table(self.table)
        tv.addWidget(self.table)
        self.grid.addWidget(self.tableCard, 1, 0, 1, 1)

        # === Importante: aplicar estilos globales ANTES de cargar/colorear ===
        apply_global_styles(Form)

        # Conexiones y datos (después del polish global)
        self.search.textChanged.connect(
            lambda text: buscar_proveedores(
                text, self.table,
                edit_callback=self.abrir_formulario_editar,
                main_form_widget=Form
            ) or self._post_refresh_table()
        )

        cargar_proveedores(self.table, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        self._post_refresh_table()

        # Asegurar recoloreo tras el ciclo de eventos (por si el QSS repintó)
        QTimer.singleShot(0, self._post_refresh_table)

        self.lblTitle.setStyleSheet("""
            #proveedoresTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
        self.lblTitle.style().unpolish(self.lblTitle)
        self.lblTitle.style().polish(self.lblTitle)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def _post_refresh_table(self):
        try:
            if self.table.columnCount() > 0:
                self.table.setColumnHidden(0, True)
        except Exception:
            pass
        try:
            current_width = self.table.columnWidth(OPCIONES_COL)
            if current_width < OPCIONES_MIN_WIDTH:
                self.table.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)
        except Exception:
            pass
        self._center_header()
        self._center_cells()
        self._colorize_option_buttons()
        try:
            form = getattr(self, '_form_main', None)
            if form is not None:
                menu_ref = getattr(form, 'menuPrincipalRef', None)
                if menu_ref:
                    menu_ref._apply_permissions_to_module_page("Proveedores", form)
        except Exception:
            pass

    def _center_header(self):
        try:
            self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass

    def _center_cells(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        for r in range(rows):
            for c in range(1, cols-1):
                it = self.table.item(r, c)
                if it is not None:
                    it.setTextAlignment(Qt.AlignCenter)
        for r in range(rows):
            cell = self.table.cellWidget(r, OPCIONES_COL)
            if cell:
                lay = cell.layout()
                if lay:
                    lay.setContentsMargins(0,0,0,0)
                    lay.setAlignment(Qt.AlignCenter)

    def _colorize_option_buttons(self):
        rows = self.table.rowCount()
        for r in range(rows):
            cell = self.table.cellWidget(r, OPCIONES_COL)
            if not cell:
                continue
            try:
                cell.setAutoFillBackground(False)
                cell.setAttribute(Qt.WA_StyledBackground, False)
                cell.setAttribute(Qt.WA_NoSystemBackground, True)
                cell.setStyleSheet("background: transparent; border: none;")
            except Exception:
                pass
            for btn in cell.findChildren(QPushButton):
                obj = (btn.objectName() or "").lower()
                perm = str(btn.property("perm_code") or "").lower()
                txt = (btn.text() or "").lower()
                variant = str(btn.property("variant") or "").lower()
                if "editar" in obj or "edit" in txt or perm.endswith(".update") or variant == "edit":
                    _style_action_button(btn, "edit")
                elif any(k in obj for k in ("eliminar", "borrar")) or \
                     any(k in txt for k in ("eliminar", "borrar", "del")) or \
                     perm.endswith(".delete") or variant == "delete":
                    _style_action_button(btn, "del")
                btn.style().unpolish(btn); btn.style().polish(btn)

    def exportar_excel_proveedores(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Proveedores.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtable_to_excel(self.table, ruta, title="Proveedores")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

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
        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(
            lambda: (
                guardar_registro(
                    self.ui_nuevo_proveedor,
                    self.formularioProveedor,
                    self.table,
                    self.abrir_formulario_editar,
                    Form,
                ),
                self._post_refresh_table(),
            )
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
        prov = obtener_proveedor_por_id(id_proveedor)
        if prov:
            _, nombre, tel, dire, mail = prov
            self.ui_nuevo_proveedor.lineEditNombre.setText(nombre)
            self.ui_nuevo_proveedor.lineEditTelefono.setText(str(tel))
            self.ui_nuevo_proveedor.lineEditDireccion.setText(dire)
            self.ui_nuevo_proveedor.lineEditCorreo.setText(mail)
        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(
            lambda: (
                editar_proveedor(
                    self.ui_nuevo_proveedor,
                    self.table,
                    id_proveedor,
                    self.formularioProveedor,
                    self.abrir_formulario_editar,
                    Form,
                ),
                self._post_refresh_table(),
            )
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
