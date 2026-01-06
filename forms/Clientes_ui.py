import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from PySide6.QtCore import Qt, QSize, QCoreApplication, QMetaObject
from PySide6.QtGui import QIcon, QFont
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

ROW_HEIGHT = 46
OPCIONES_COL = 5
OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ICON_PX = 18

from main.themes import themed_icon
def icon(name: str) -> QIcon:
    return themed_icon(name)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 680)

        self.grid = QGridLayout(Form)
        self.grid.setContentsMargins(12, 12, 12, 12)
        self.grid.setSpacing(10)

        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16,12,16,12); hl.setSpacing(10)

        self.lblTitle = QLabel("clientes", self.headerCard)
        self.lblTitle.setObjectName("clientesTitle")
        self.lblTitle.setProperty("role", "pageTitle")
        f = QFont(self.lblTitle.font()); f.setBold(False); f.setPointSize(26)
        self.lblTitle.setFont(f)
        mark_title(self.lblTitle)
        self.lblTitle.setStyleSheet("""
            #clientesTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
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
        self.btnNuevo.setObjectName("btnClienteNuevo")
        self.btnNuevo.setProperty("type","primary")
        self.btnNuevo.setProperty("perm_code", "clientes.create")
        self.btnNuevo.setIcon(icon("plus"))
        make_primary(self.btnNuevo)
        self.btnNuevo.clicked.connect(lambda: self.abrir_formulario(Form))
        hl.addWidget(self.btnNuevo)

        self.grid.addWidget(self.headerCard, 0, 0, 1, 1)

        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.tableWidget = QTableWidget(self.tableCard)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID","Nombre","Teléfono","CI/RUC","Email","Opciones"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in (1,2,3,4):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)
        try:
            header.setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass

        style_table(self.tableWidget)

        # ← Revertimos a la tabla por defecto (grid nativo)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.setStyleSheet("")  # sin QSS que altere líneas o bordes

        tv.addWidget(self.tableWidget)
        self.grid.addWidget(self.tableCard, 1, 0, 1, 1)

        self.search.textChanged.connect(
            lambda text: buscar_clientes(
                text, self.tableWidget,
                edit_callback=self.abrir_formulario_editar,
                main_form_widget=Form
            ) or self._post_refresh_table()
        )

        cargar_clientes(self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        self._post_refresh_table()

        apply_global_styles(Form)
        self.lblTitle.setStyleSheet("""
            #clientesTitle {
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
            if self.tableWidget.columnCount() > 0:
                self.tableWidget.setColumnHidden(0, True)
        except Exception:
            pass
        try:
            current_width = self.tableWidget.columnWidth(OPCIONES_COL)
            if current_width < OPCIONES_MIN_WIDTH:
                self.tableWidget.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)
        except Exception:
            pass
        self._center_header()
        self._center_cells()
        self._restyle_option_buttons()

    def _center_header(self):
        try:
            self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass

    def _center_cells(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()
        for r in range(rows):
            for c in range(1, cols-1):
                it = self.tableWidget.item(r, c)
                if it is not None:
                    it.setTextAlignment(Qt.AlignCenter)
        for r in range(rows):
            cell = self.tableWidget.cellWidget(r, OPCIONES_COL)
            if cell:
                lay = cell.layout()
                if lay:
                    lay.setContentsMargins(0,0,0,0)
                    lay.setAlignment(Qt.AlignCenter)

    def _restyle_option_buttons(self):
        col = OPCIONES_COL
        rows = self.tableWidget.rowCount()
        for r in range(rows):
            cell = self.tableWidget.cellWidget(r, col)
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
                if "editar" in obj or "editar" in txt or "edit" in txt or perm.endswith(".update"):
                    self._style_action_button(btn, "edit")
                elif any(k in obj for k in ("eliminar", "borrar")) or \
                     any(k in txt for k in ("eliminar", "borrar", "del")) or \
                     perm.endswith(".delete"):
                    self._style_action_button(btn, "del")
                else:
                    # default heuristics: treat icon buttons with no text but already variant set
                    variant = str(btn.property("variant") or "").lower()
                    if variant == "edit":
                        self._style_action_button(btn, "edit")
                    elif variant == "delete":
                        self._style_action_button(btn, "del")
                btn.style().unpolish(btn); btn.style().polish(btn)

    def _style_action_button(self, btn: QPushButton, kind: str):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(BTN_MIN_HEIGHT)
        btn.setIconSize(QSize(ICON_PX, ICON_PX))
        if kind == "edit":
            style_edit_button(btn, "Editar cliente")
        else:
            style_delete_button(btn, "Eliminar cliente")

    def exportar_excel_clientes(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Clientes.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtable_to_excel(self.tableWidget, ruta, title="Clientes")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

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
        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: guardar_registro(self.ui_nuevo_cliente, self.formularioCliente,
                                     self.tableWidget, self.abrir_formulario_editar, Form) or self._post_refresh_table()
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
                                   self.formularioCliente, self.abrir_formulario_editar, Form) or self._post_refresh_table()
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
