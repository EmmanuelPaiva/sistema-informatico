import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt, QPropertyAnimation, QObject, QEvent)
from PySide6.QtGui import QFontMetrics
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

# ==== Estilos/helpers del sistema ====
from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, make_danger, style_search
)


# --- Constantes (más aire y sin cortes) ---
ROW_HEIGHT = 48                 # altura de fila
OPCIONES_BASE_MIN = 210         # mínimo base más generoso
BTN_MIN_HEIGHT = 34             # alto mínimo botón
BTN_HPADDING = 36               # padding horizontal total (izq+der)
BTN_SPACING_IN_CELL = 8         # espacio entre botones dentro de la celda
BTN_MIN_WIDTH_FLOOR = 96        # mínimo por botón


class _ResizeWatcher(QObject):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner._ajustar_columnas()
            self.owner._ensure_options_width()
        return False


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1000, 660)

        # ====== Layout raíz ======
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        # ====== Título ======
        self.labelCompras = QLabel(Form)
        self.labelCompras.setObjectName(u"labelCompras")
        self.labelCompras.setText("Compras")
        mark_title(self.labelCompras)
        self.gridLayout.addWidget(self.labelCompras, 0, 0, 1, 1)

        # ====== Fila de controles ======
        self.controlsFrame = QFrame(Form)
        self.controlsFrame.setFrameShape(QFrame.NoFrame)
        controlsLayout = QHBoxLayout(self.controlsFrame)
        controlsLayout.setContentsMargins(0, 0, 0, 0)
        controlsLayout.setSpacing(10)

        self.searchBox = QLineEdit(self.controlsFrame)
        self.searchBox.setPlaceholderText("Buscar por proveedor, factura o medio…")
        self.searchBox.setClearButtonEnabled(True)
        self.searchBox.setMinimumWidth(280)
        self.searchBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        style_search(self.searchBox)
        controlsLayout.addWidget(self.searchBox, 1)

        self.pushButtonExportar = QPushButton(self.controlsFrame)
        self.pushButtonExportar.setText("Exportar")
        self.pushButtonExportar.setCursor(Qt.PointingHandCursor)
        self.pushButtonExportar.setMinimumHeight(BTN_MIN_HEIGHT)
        self.pushButtonExportar.setMinimumWidth(BTN_MIN_WIDTH_FLOOR)
        make_primary(self.pushButtonExportar)
        self.pushButtonExportar.clicked.connect(self.exportar_excel_compras)
        controlsLayout.addWidget(self.pushButtonExportar)

        self.pushButtonNuevaCompra = QPushButton(self.controlsFrame)
        self.pushButtonNuevaCompra.setText("Nueva compra")
        self.pushButtonNuevaCompra.setCursor(Qt.PointingHandCursor)
        self.pushButtonNuevaCompra.setMinimumHeight(BTN_MIN_HEIGHT)
        self.pushButtonNuevaCompra.setMinimumWidth(BTN_MIN_WIDTH_FLOOR)
        make_primary(self.pushButtonNuevaCompra)
        self.pushButtonNuevaCompra.clicked.connect(lambda: self.abrir_formulario_nueva_compra(Form))
        controlsLayout.addWidget(self.pushButtonNuevaCompra)

        self.gridLayout.addWidget(self.controlsFrame, 1, 0, 1, 1)

        # ====== Wrapper de tabla ======
        self.tableWrapper = QFrame(Form)
        self.tableWrapper.setObjectName("tablaWrapper")
        self.tableWrapper.setStyleSheet(f"""
        #tablaWrapper {{
            background: #ffffff;
            border: 1px solid #dfe7f5;
            border-radius: 12px;
        }}
        QTreeWidget {{
            background: #ffffff;
            border: none;
        }}
        QHeaderView {{
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            background: transparent;
        }}
        QHeaderView::section {{
            background: #f7f9fc;
            color: #0d1b2a;
            padding: 10px; /* un poco más de padding en header */
            border: none;
            border-right: 1px solid #dfe7f5;
        }}
        QHeaderView::section:first {{
            border-top-left-radius: 12px;
        }}
        QHeaderView::section:last {{
            border-top-right-radius: 12px;
            border-right: none;
        }}
        QTreeView::item {{
            height: {ROW_HEIGHT}px;  /* más aire entre filas */
        }}
        QTreeWidget::item:selected {{
            background: rgba(144,202,249,.25);
            color: #0d1b2a;
        }}
        """)
        wrapperLayout = QHBoxLayout(self.tableWrapper)
        wrapperLayout.setContentsMargins(0, 0, 0, 0)
        wrapperLayout.setSpacing(0)

        # ====== Tabla maestro/detalle ======
        self.treeWidget = QTreeWidget(self.tableWrapper)
        self.treeWidget.setObjectName(u"treeWidget")
        wrapperLayout.addWidget(self.treeWidget)
        self.gridLayout.addWidget(self.tableWrapper, 2, 0, 1, 1)

        self.treeWidget.setColumnCount(7)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Proveedor", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setColumnHidden(0, True)

        header = self.treeWidget.header()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (oculto)
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Fecha
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Proveedor
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Total
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Medio
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Factura
        header.setSectionResizeMode(6, QHeaderView.Interactive)       # Opciones -> lo controlamos nosotros

        # Señales
        self.searchBox.textChanged.connect(self._filtrar)

        # Watcher resize
        self._resizeWatcher = _ResizeWatcher(self)
        self.treeWidget.installEventFilter(self._resizeWatcher)

        # Estilos globales
        apply_global_styles(Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

        # Cargar datos
        setRowsTreeWidget(self, Form)
        self._post_refresh()

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Compras", None))
        self.pushButtonNuevaCompra.setText(QCoreApplication.translate("Form", u"Nueva compra", None))
        self.pushButtonExportar.setText(QCoreApplication.translate("Form", u"Exportar", None))
        self.labelCompras.setText(QCoreApplication.translate("Form", u"Compras", None))

    # ====== Exportar ======
    def exportar_excel_compras(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(
                None,
                "Guardar como",
                "Compras.xlsx",
                "Excel (*.xlsx)"
            )
            if not ruta:
                return
            export_qtree_to_excel(self.treeWidget, ruta, title="Compras")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    # ====== Slide-in ======
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

    def abrir_formulario_nueva_compra(self, Form, edicion=False):
        if hasattr(self, 'formulario_nueva_compra') and self.formulario_nueva_compra.isVisible():
            return

        self.ui_nueva_compra = nuevaCompraUi()
        self.formulario_nueva_compra = QWidget(Form)
        self.ui_nueva_compra.setupUi(self.formulario_nueva_compra)

        # Cambiar label "Cliente" -> "Proveedor"
        if hasattr(self.ui_nueva_compra, "labelCliente"):
            self.ui_nueva_compra.labelCliente.setText("Proveedor")

        # Primera fila
        agrega_prodcuto_a_fila(self.ui_nueva_compra)

        # Slide-in
        ancho_formulario = 450
        alto_formulario = Form.height()
        self.formulario_nueva_compra.setGeometry(Form.width(), 0, ancho_formulario, alto_formulario)
        self.formulario_nueva_compra.show()
        self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Cargar proveedores
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

        # Botones del formulario
        self.ui_nueva_compra.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_compra.pushButtonAgregarProducto.clicked.connect(lambda: agrega_prodcuto_a_fila(self.ui_nueva_compra))
        self.ui_nueva_compra.pushButtonQuitarProducto.clicked.connect(lambda: borrar_fila(self.ui_nueva_compra))
        self.ui_nueva_compra.pushButtonAceptar.clicked.connect(lambda: SaveSellIntoDb(self.ui_nueva_compra, ui=self, form=Form))

    # ====== Utilidades de UI ======
    def _filtrar(self, texto: str):
        """Filtra por Proveedor (col 2), Factura (col 5) o Medio (col 4)."""
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
        self._colorize_op_buttons()
        self._ensure_options_width()

    def _ajustar_columnas(self):
        header = self.treeWidget.header()
        for col in (1, 2, 3, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

    def _colorize_op_buttons(self):
        """Aplica estilos y mínimos a botones dentro de la columna 'Opciones'."""
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(item, 6)
            if not w:
                continue
            if hasattr(w, "layout") and w.layout():
                w.layout().setContentsMargins(0, 0, 0, 0)
                w.layout().setSpacing(BTN_SPACING_IN_CELL)
            for btn in w.findChildren(QPushButton):
                txt = (btn.text() or "").strip()
                fm = QFontMetrics(btn.font())
                text_w = fm.horizontalAdvance(txt)
                min_w = max(text_w + BTN_HPADDING, BTN_MIN_WIDTH_FLOOR)
                btn.setMinimumWidth(min_w)
                btn.setMinimumHeight(BTN_MIN_HEIGHT)
                btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                # un poco más de padding por si el style no lo aplica
                btn.setStyleSheet("padding-left:12px; padding-right:12px;")
                lower = txt.lower()
                if "eliminar" in lower or "borrar" in lower:
                    make_danger(btn)
                elif "editar" in lower:
                    make_primary(btn)

    def _ensure_options_width(self):
        """Calcula el ancho real necesario de 'Opciones' y lo fija (Interactive)."""
        max_needed = OPCIONES_BASE_MIN
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(item, 6)
            if not w:
                continue
            total = 0
            count = 0
            for btn in w.findChildren(QPushButton):
                total += max(btn.minimumWidth(), btn.sizeHint().width())
                count += 1
            if count > 1:
                total += BTN_SPACING_IN_CELL * (count - 1)
            total += 16  # margen extra
            if total > max_needed:
                max_needed = total
        current = self.treeWidget.columnWidth(6)
        if current < max_needed:
            self.treeWidget.setColumnWidth(6, max_needed)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
