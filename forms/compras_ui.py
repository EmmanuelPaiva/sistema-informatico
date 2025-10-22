# compras_willow.py — UI con título mejorado e iconización estable
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import (QCoreApplication, QRect, Qt, QPropertyAnimation, QObject, QEvent, QTimer)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
    QTreeWidget, QHeaderView, QHBoxLayout, QFileDialog, QMessageBox, QLineEdit,
    QSizePolicy
)

from forms.formularioVentas import Ui_Form as nuevaCompraUi
from db.conexion import conexion
from db.compras_queries import (
    agrega_prodcuto_a_fila, reiniciar_tabla_productos, SaveSellIntoDb, setRowsTreeWidget,
    on_proveedor_selected
)
from utils.utilsCompras import borrar_fila
from reports.excel import export_qtree_to_excel

from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, style_search
)
from main.themes import themed_icon

# ---- Constantes UI
ROW_HEIGHT = 48
BTN_MIN_HEIGHT = 32
OPCIONES_COL = 6

def icon(name: str) -> QIcon:
    return themed_icon(name)

class _ResizeWatcher(QObject):
    def __init__(self, owner): super().__init__(); self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize: self.owner._ajustar_columnas()
        return False

class _ParentResizeWatcher(QObject):
    def __init__(self, ui): super().__init__(); self.ui = ui
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize: self.ui._sync_form_geometry()
        return False

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 660)

        self._host = Form
        self._slide_width = 450

        # ===== Layout raíz
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        # ===== Header
        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16,12,16,12); hl.setSpacing(10)

        self.labelCompras = QLabel("COMPRAS", self.headerCard)
        self.labelCompras.setProperty("role", "pageTitle")
        # estilo elegante en mayúsculas
        f = QFont(self.labelCompras.font())
        f.setBold(True)
        f.setPointSize(20)
        f.setLetterSpacing(QFont.PercentageSpacing, 105)  # +5%
        self.labelCompras.setFont(f)
        mark_title(self.labelCompras)

        hl.addWidget(self.labelCompras)
        hl.addStretch(1)

        self.searchBox = QLineEdit(self.headerCard)
        self.searchBox.setObjectName("searchBox")
        self.searchBox.setPlaceholderText("Buscar por proveedor, factura o medio…")
        self.searchBox.setClearButtonEnabled(True)
        self.searchBox.setMinimumWidth(280)
        self.searchBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.searchBox.addAction(icon("search"), QLineEdit.LeadingPosition)
        style_search(self.searchBox)
        hl.addWidget(self.searchBox, 1)

        self.pushButtonExportar = QPushButton("Exportar", self.headerCard)
        self.pushButtonExportar.setProperty("type","primary")
        self.pushButtonExportar.setIcon(icon("file-spreadsheet"))
        make_primary(self.pushButtonExportar)
        self.pushButtonExportar.clicked.connect(self.exportar_excel_compras)
        hl.addWidget(self.pushButtonExportar)

        self.pushButtonNuevaCompra = QPushButton("Nueva compra", self.headerCard)
        self.pushButtonNuevaCompra.setObjectName("btnCompraNueva")
        self.pushButtonNuevaCompra.setProperty("perm_code", "compras.create")
        self.pushButtonNuevaCompra.setProperty("type","primary")
        self.pushButtonNuevaCompra.setIcon(icon("plus"))
        make_primary(self.pushButtonNuevaCompra)
        self.pushButtonNuevaCompra.clicked.connect(lambda: self.abrir_formulario_nueva_compra(Form))
        hl.addWidget(self.pushButtonNuevaCompra)

        self.gridLayout.addWidget(self.headerCard, 0, 0, 1, 1)

        # ===== Tabla (card)
        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.treeWidget = QTreeWidget(self.tableCard)
        tv.addWidget(self.treeWidget)
        self.gridLayout.addWidget(self.tableCard, 1, 0, 1, 1)

        # Config tabla
        self.treeWidget.setColumnCount(7)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Proveedor", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setColumnHidden(0, True)
        self.treeWidget.setStyleSheet(f"QTreeWidget::item {{ height: {ROW_HEIGHT}px; }}")

        header = self.treeWidget.header()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in (1,2,3,4,5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)

        # Señales
        self.searchBox.textChanged.connect(self._filtrar)

        # Watchers
        self._resizeWatcher = _ResizeWatcher(self); self.treeWidget.installEventFilter(self._resizeWatcher)
        self._parentWatcher = _ParentResizeWatcher(self); Form.installEventFilter(self._parentWatcher)

        # Estilos globales
        apply_global_styles(Form)

        self.retranslateUi(Form)

        # Cargar datos (la función ahora resuelve el tree si cambiara el nombre/orden)
        setRowsTreeWidget(self, Form)
        self._post_refresh()

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Compras", None))

    # ===== Exportar
    def exportar_excel_compras(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Compras.xlsx", "Excel (*.xlsx)")
            if not ruta: return
            export_qtree_to_excel(self.treeWidget, ruta, title="Compras")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    # ===== Slide-out helpers
    def _sync_form_geometry(self):
        if not hasattr(self, 'formulario_nueva_compra') or not self.formulario_nueva_compra.isVisible():
            return
        host_w = max(self._host.width(), 0)
        host_h = max(self._host.height(), 0)
        panel_w = min(self._slide_width, max(280, host_w))
        x = host_w - panel_w
        self.formulario_nueva_compra.setGeometry(x, 0, panel_w, host_h)

    def cancelar(self, Form):
        if hasattr(self, 'formulario_nueva_compra') and self.formulario_nueva_compra.isVisible():
            w = self.formulario_nueva_compra.width()
            h = Form.height()
            self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
            self.anim.setDuration(300)
            self.anim.setStartValue(QRect(Form.width() - w, 0, w, h))
            self.anim.setEndValue(QRect(Form.width(), 0, w, h))
            self.anim.finished.connect(self.formulario_nueva_compra.close)
            self.anim.start()

    # ===== Alta/edición compra
    def abrir_formulario_nueva_compra(self, Form, edicion=False):
        if hasattr(self, 'formulario_nueva_compra') and self.formulario_nueva_compra.isVisible():
            return

        self.ui_nueva_compra = nuevaCompraUi()
        self.formulario_nueva_compra = QWidget(Form)
        self.ui_nueva_compra.setupUi(self.formulario_nueva_compra)

        if hasattr(self.ui_nueva_compra, "labelCliente"):
            self.ui_nueva_compra.labelCliente.setText("Proveedor")

        # ✅ SOLO agregamos la fila inicial cuando NO es edición
        if not edicion:
            agrega_prodcuto_a_fila(self.ui_nueva_compra)

        # Slide in
        w = min(self._slide_width, max(280, Form.width()))
        h = Form.height()
        self.formulario_nueva_compra.setGeometry(Form.width(), 0, w, h)
        self.formulario_nueva_compra.show()

        self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, w, h))
        self.anim.setEndValue(QRect(Form.width() - w, 0, w, h))
        self.anim.start()

        QTimer.singleShot(0, self._sync_form_geometry)
        self.anim.finished.connect(self._sync_form_geometry)

        if not edicion:
            try:
                with conexion() as c, c.cursor() as cur:
                    cur.execute("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre;")
                    proveedores = cur.fetchall()
                self.ui_nueva_compra.comboBox.clear()
                for idP, nombreP in proveedores:
                    self.ui_nueva_compra.comboBox.addItem(nombreP, idP)

                if self.ui_nueva_compra.comboBox.count() > 0:
                    self.ui_nueva_compra.comboBox.setCurrentIndex(0)

                # ✅ estas señales SOLO para alta nueva (para edición las manejamos nosotros)
                self.ui_nueva_compra.comboBox.currentIndexChanged.connect(
                    lambda: reiniciar_tabla_productos(self.ui_nueva_compra)
                )
                self.ui_nueva_compra.comboBox.currentIndexChanged.connect(
                    lambda: on_proveedor_selected(self.ui_nueva_compra)
                )
                on_proveedor_selected(self.ui_nueva_compra)
            except Exception as e:
                print(f"Error cargando proveedores: {e}")

        self.ui_nueva_compra.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_compra.pushButtonAgregarProducto.clicked.connect(lambda: agrega_prodcuto_a_fila(self.ui_nueva_compra))
        self.ui_nueva_compra.pushButtonQuitarProducto.clicked.connect(lambda: borrar_fila(self.ui_nueva_compra))
        self.ui_nueva_compra.pushButtonAceptar.clicked.connect(lambda: SaveSellIntoDb(self.ui_nueva_compra, ui=self, form=Form))

    # ===== Utilidades UI
    def _filtrar(self, texto: str):
        q = (texto or "").strip().lower()
        root = self.treeWidget.rootIndex()
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            proveedor = (item.text(2) or "").lower()
            medio     = (item.text(4) or "").lower()
            factura   = (item.text(5) or "").lower()
            visible = (q in proveedor) or (q in medio) or (q in factura)
            self.treeWidget.setRowHidden(i, root, not visible)
        self._post_refresh()

    def _post_refresh(self):
        self._ajustar_columnas()
        self._center_cells()
        self._iconize_option_buttons()

    def _ajustar_columnas(self):
        header = self.treeWidget.header()
        for col in (1, 2, 3, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)

    def _center_cells(self):
        def process_item(item):
            for col in (1,2,3,4,5):
                item.setTextAlignment(col, Qt.AlignCenter)
            for k in range(item.childCount()):
                process_item(item.child(k))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))

    def _iconize_option_buttons(self):
        # asegura que "Editar / Eliminar" siempre sean icon-only con color
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(item, OPCIONES_COL)
            if not w: continue
            for btn in w.findChildren(QPushButton):
                lower = (btn.text() or "").lower()
                if "edit" in lower or "editar" in lower:
                    btn.setProperty("type", "icon")
                    btn.setProperty("variant", "edit")
                    btn.setIcon(icon("edit"))
                    btn.setText("")
                    btn.setToolTip("Editar compra")
                elif "del" in lower or "elimin" in lower or "borrar" in lower:
                    btn.setProperty("type", "icon")
                    btn.setProperty("variant", "delete")
                    btn.setIcon(icon("trash"))
                    btn.setText("")
                    btn.setToolTip("Eliminar compra")
                else:
                    continue
                btn.setCursor(Qt.PointingHandCursor)
                btn.style().unpolish(btn); btn.style().polish(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
