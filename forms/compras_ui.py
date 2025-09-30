# compras_willow.py
import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt, QPropertyAnimation, QObject, QEvent)
from PySide6.QtGui import QIcon
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
    apply_global_styles, mark_title, make_primary, make_danger, style_search
)

# ---- Constantes UI
ROW_HEIGHT = 48
BTN_MIN_HEIGHT = 32   # alineado con Productos (alto ~32px)
OPCIONES_COL = 6      # índice de "Opciones"

# ---- Iconos (rodlerIcons en escritorio/OneDrive)
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

# ---- QSS Willow (mismo que módulos anteriores)
QSS_WILLOW = """
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background: transparent; }

/* Cards */
#headerCard, #tableCard, QTreeWidget {
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

/* Botones icon-only base */
QPushButton[type="icon"] {
  background: transparent;
  border: none;
  color:#64748B;
  padding:6px 10px;
  border-radius:8px;
  qproperty-iconSize: 18px 18px;
}
QPushButton[type="icon"]:hover {
  background: rgba(41,121,255,.10);
  color:#0F172A;
}

/* Variantes coloreadass*/
QPushButton[type="icon"][variant="edit"] {
  background:#2979FF;
  color:#FFFFFF;
}
QPushButton[type="icon"][variant="edit"]:hover {
  background:#DCEBFF;
  color:#1E40AF;
}
QPushButton[type="icon"][variant="delete"] {
  background:#FEECEC;
  color:#DC2626;
}
QPushButton[type="icon"][variant="delete"]:hover {
  background:#FDDDDD;
  color:#B91C1C;
}

/* Header/selección tabla */
QHeaderView::section {
  background:#F8FAFF;
  color:#0F172A;
  padding:10px;
  border:none;
  border-right:1px solid #E8EEF6;
}
QTreeWidget {
  selection-background-color: rgba(41,121,255,.15);
  selection-color:#0F172A;
  border:1px solid #E8EEF6;
  border-radius:16px;
}
"""

class _ResizeWatcher(QObject):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner._ajustar_columnas()
        return False


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 660)

        # ===== Layout raíz
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        # ===== Header (misma línea: título + buscador + botones)
        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16,12,16,12); hl.setSpacing(10)

        self.labelCompras = QLabel("Compras", self.headerCard)
        self.labelCompras.setProperty("role", "pageTitle")
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

        # Watcher resize
        self._resizeWatcher = _ResizeWatcher(self)
        self.treeWidget.installEventFilter(self._resizeWatcher)

        # Estilos globales + Willow
        apply_global_styles(Form)
        Form.setStyleSheet(QSS_WILLOW)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

        # Cargar datos y post-estética
        setRowsTreeWidget(self, Form)
        self._post_refresh()

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Compras", None))

    # ===== Exportar
    def exportar_excel_compras(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Compras.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtree_to_excel(self.treeWidget, ruta, title="Compras")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    # ===== Slide-out cancelar
    def cancelar(self, Form):
        if hasattr(self, 'formulario_nueva_compra'):
            ancho_formulario = self.formulario_nueva_compra.width()
            alto_formulario = Form.height()
            self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
            self.anim.setDuration(300)
            self.anim.setStartValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
            self.anim.setEndValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
            self.anim.start()
            self.formulario_nueva_compra.close()

    # ===== Alta compra
    def abrir_formulario_nueva_compra(self, Form, edicion=False):
        if hasattr(self, 'formulario_nueva_compra') and self.formulario_nueva_compra.isVisible():
            return

        self.ui_nueva_compra = nuevaCompraUi()
        self.formulario_nueva_compra = QWidget(Form)
        self.ui_nueva_compra.setupUi(self.formulario_nueva_compra)

        if hasattr(self.ui_nueva_compra, "labelCliente"):
            self.ui_nueva_compra.labelCliente.setText("Proveedor")

        agrega_prodcuto_a_fila(self.ui_nueva_compra)

        ancho_formulario = 450
        alto_formulario = Form.height()
        self.formulario_nueva_compra.setGeometry(Form.width(), 0, ancho_formulario, alto_formulario)
        self.formulario_nueva_compra.show()
        self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        if not edicion:
            try:
                with conexion() as c:
                    with c.cursor() as cur:
                        cur.execute("SELECT id_proveedor, nombre FROM proveedores;")
                        proveedores = cur.fetchall()
                for idP, nombreP in proveedores:
                    self.ui_nueva_compra.comboBox.addItem(nombreP, idP)
                if self.ui_nueva_compra.comboBox.count() > 0:
                    self.ui_nueva_compra.comboBox.setCurrentIndex(0)
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
        """Filtra por Proveedor (2), Factura (5) o Medio (4)."""
        q = (texto or "").strip().lower()
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            proveedor = (item.text(2) or "").lower()
            medio     = (item.text(4) or "").lower()
            factura   = (item.text(5) or "").lower()
            visible = (q in proveedor) or (q in medio) or (q in factura)
            self.treeWidget.setRowHidden(i, self.treeWidget.rootIndex(), not visible)
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

    # Centrado de contenido
    def _center_cells(self):
        def process_item(item):
            for col in (1,2,3,4,5):
                item.setTextAlignment(col, Qt.AlignCenter)
            for k in range(item.childCount()):
                process_item(item.child(k))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))

    # Botones de Opciones: icon-only con color (igual que Productos)
    def _iconize_option_buttons(self):
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(item, OPCIONES_COL)
            if not w:
                continue
            for btn in w.findChildren(QPushButton):
                lower = (btn.text() or "").lower()
                if "edit" in lower or "editar" in lower:
                    btn.setProperty("type", "icon")
                    btn.setProperty("variant", "edit")     # AZUL
                    btn.setIcon(icon("edit"))
                    btn.setText("")
                    btn.setToolTip("Editar compra")
                elif "del" in lower or "elimin" in lower or "borrar" in lower:
                    btn.setProperty("type", "icon")
                    btn.setProperty("variant", "delete")   # ROJO
                    btn.setIcon(icon("trash"))
                    btn.setText("")
                    btn.setToolTip("Eliminar compra")
                else:
                    continue

                btn.setMinimumHeight(BTN_MIN_HEIGHT)
                btn.setCursor(Qt.PointingHandCursor)
                # refrescar estilo para que tome las nuevas props
                btn.style().unpolish(btn); btn.style().polish(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
