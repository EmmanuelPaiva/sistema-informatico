import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import QCoreApplication, QRect, Qt, QPropertyAnimation, QObject, QEvent, QTimer, QDate, QDateTime, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QHBoxLayout, QFileDialog, QMessageBox, QLineEdit,
    QSizePolicy, QListView, QDateEdit, QDateTimeEdit
)

from forms.formularioVentas import Ui_Form as nuevaCompraUi
from db.conexion import conexion
from db.compras_queries import (
    _ensure_producto_cache, agrega_prodcuto_a_fila, reiniciar_tabla_productos, SaveSellIntoDb, setRowsTreeWidget,
    on_proveedor_selected
)
from utils.utilsCompras import borrar_fila
from reports.excel import export_qtree_to_excel
from forms.ui_helpers import apply_global_styles, mark_title, make_primary, style_search
from main.themes import themed_icon

ROW_HEIGHT = 46
BTN_MIN_HEIGHT = 32
OPCIONES_COL = 6
OPCIONES_MIN_WIDTH = 140
ROLE_DETAILS_LOADED = Qt.UserRole + 101

def icon(name: str) -> QIcon:
    return themed_icon(name)

class _ResizeWatcher(QObject):
    def __init__(self, owner): super().__init__(); self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize: self.owner._ajustar_columnas()
        return False

class _ParentResizeWatcher(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.ui._sync_form_geometry()
        if event.type() in (QEvent.PaletteChange, QEvent.StyleChange):
            QTimer.singleShot(0, self.ui._reapply_theme_dependent_styles)
        return False

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 660)
        self._host = Form
        self._slide_width = 450

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        self.headerCard = QFrame(Form)
        self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard)
        hl.setContentsMargins(16, 12, 16, 12)
        hl.setSpacing(10)

        self.labelCompras = QLabel("compras", self.headerCard)
        self.labelCompras.setObjectName("comprasTitle")
        self.labelCompras.setProperty("role", "pageTitle")
        f = QFont(self.labelCompras.font())
        f.setBold(False)
        f.setPointSize(28)
        f.setLetterSpacing(QFont.PercentageSpacing, 105)
        self.labelCompras.setFont(f)
        mark_title(self.labelCompras)
        self.labelCompras.setStyleSheet("""
            #comprasTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
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
        self.pushButtonExportar.setProperty("type", "primary")
        self.pushButtonExportar.setIcon(icon("file-spreadsheet"))
        make_primary(self.pushButtonExportar)
        self.pushButtonExportar.clicked.connect(self.exportar_excel_compras)
        hl.addWidget(self.pushButtonExportar)

        self.pushButtonNuevaCompra = QPushButton("Nueva compra", self.headerCard)
        self.pushButtonNuevaCompra.setObjectName("btnCompraNueva")
        self.pushButtonNuevaCompra.setProperty("perm_code", "compras.create")
        self.pushButtonNuevaCompra.setProperty("type", "primary")
        self.pushButtonNuevaCompra.setIcon(icon("plus"))
        make_primary(self.pushButtonNuevaCompra)
        self.pushButtonNuevaCompra.clicked.connect(lambda: self.abrir_formulario_nueva_compra(Form))
        hl.addWidget(self.pushButtonNuevaCompra)

        self.gridLayout.addWidget(self.headerCard, 0, 0, 1, 1)

        self.tableCard = QFrame(Form)
        self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard)
        tv.setContentsMargins(0, 0, 0, 0)

        self.treeWidget = QTreeWidget(self.tableCard)
        tv.addWidget(self.treeWidget)
        self.gridLayout.addWidget(self.tableCard, 1, 0, 1, 1)

        self.treeWidget.setColumnCount(7)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Proveedor", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setColumnHidden(0, True)
        self.treeWidget.setSelectionBehavior(QTreeWidget.SelectRows)
        self.treeWidget.setAllColumnsShowFocus(True)
        self.treeWidget.setStyleSheet(f"QTreeWidget::item{{height:{ROW_HEIGHT}px;}}")

        header = self.treeWidget.header()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in (1, 2, 3, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)
        try:
            header.setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass

        apply_global_styles(Form)

        self._center_header()
        self.searchBox.textChanged.connect(self._filtrar)
        self.treeWidget.itemDoubleClicked.connect(self._on_item_double_clicked)

        self._resizeWatcher = _ResizeWatcher(self)
        self.treeWidget.installEventFilter(self._resizeWatcher)
        self._parentWatcher = _ParentResizeWatcher(self)
        Form.installEventFilter(self._parentWatcher)

        self.labelCompras.setStyleSheet("""
            #comprasTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
        self.labelCompras.style().unpolish(self.labelCompras)
        self.labelCompras.style().polish(self.labelCompras)

        self.retranslateUi(Form)
        setRowsTreeWidget(self, Form)
        self._post_refresh()
        QTimer.singleShot(0, self._post_refresh)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Compras", None))

    def exportar_excel_compras(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Compras.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtree_to_excel(self.treeWidget, ruta, title="Compras")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    def _fix_combo_popup(self, combo):
        try:
            view = QListView(combo)
            view.setUniformItemSizes(True)
            view.setAlternatingRowColors(False)
            combo.setView(view)
            combo.setFrame(True)
        except Exception:
            pass

    def _style_form_cell_widgets(self, ui_form):
        tw = getattr(ui_form, "tableWidget", None)
        if tw is None:
            return
        vh = tw.verticalHeader()
        vh.setDefaultSectionSize(40)
        vh.setMinimumSectionSize(36)
        for r in range(tw.rowCount()):
            tw.setRowHeight(r, vh.defaultSectionSize())
            combo = tw.cellWidget(r, 0)
            if combo is not None:
                combo.setContentsMargins(0, 0, 0, 0)
                combo.setMinimumHeight(36)
  
                self._fix_combo_popup(combo)
            spin = tw.cellWidget(r, 1)
            if spin is not None:
                spin.setContentsMargins(0, 0, 0, 0)
                spin.setMinimumHeight(36)
      
        prev = tw.styleSheet() or ""
        tw.setStyleSheet(prev + "\nQTableWidget::item{ padding: 0; margin: 0; }\n")

    def _inflate_form_table(self, ui_form):
        tw = getattr(ui_form, "tableWidget", None)
        if tw is None:
            return
        tw.setMinimumHeight(260)
        self._style_form_cell_widgets(ui_form)

    def _restyle_form_tables(self):
        targets = []
        if hasattr(self, "ui_nueva_compra"):
            targets.append(getattr(self, "ui_nueva_compra", None))
        for form_ui in targets:
            if form_ui is None:
                continue
            self._style_form_cell_widgets(form_ui)

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
    
    # === REFRESH ===
    def refrescar(self):
        """
        Refresca completamente el módulo de Compras
        """
        try:
            self.searchBox.clear()
            setRowsTreeWidget(self, self._host)
            self._post_refresh()
        except Exception as e:
            print(f"[Compras.refrescar] Error: {e}")

    def abrir_formulario_nueva_compra(self, Form, edicion=False):
        if hasattr(self, 'formulario_nueva_compra') and self.formulario_nueva_compra.isVisible():
            return
        self.ui_nueva_compra = nuevaCompraUi()
        self.formulario_nueva_compra = QWidget(Form)
        self.ui_nueva_compra.setupUi(self.formulario_nueva_compra)
        if hasattr(self.ui_nueva_compra, "labelCliente"):
            self.ui_nueva_compra.labelCliente.setText("Proveedor")
        self._inflate_form_table(self.ui_nueva_compra)
        if not edicion:
            agrega_prodcuto_a_fila(self.ui_nueva_compra)
        self._inflate_form_table(self.ui_nueva_compra)
        self._set_today_default_date()
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
        QTimer.singleShot(0, lambda: self._inflate_form_table(self.ui_nueva_compra))
        self.anim.finished.connect(self._sync_form_geometry)
        if not edicion:
            try:
                with conexion() as c, c.cursor() as cur:
                    cur.execute("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre;")
                    proveedores = cur.fetchall()

                cb = self.ui_nueva_compra.comboBox
                cb.blockSignals(True)
                cb.clear()

                for idP, nombreP in proveedores:
                    cb.addItem(nombreP, idP)

                if cb.count() > 0:
                    cb.setCurrentIndex(0)

                cb.blockSignals(False)

                def init_proveedor():
                    proveedor_id = cb.currentData()
                    if proveedor_id is not None:
                        _ensure_producto_cache(self.ui_nueva_compra, proveedor_id)
                        on_proveedor_selected(self.ui_nueva_compra)
                        reiniciar_tabla_productos(self.ui_nueva_compra)
                        self._inflate_form_table(self.ui_nueva_compra)

                QTimer.singleShot(0, init_proveedor)

                cb.currentIndexChanged.connect(
                    lambda: (
                        reiniciar_tabla_productos(self.ui_nueva_compra),
                        on_proveedor_selected(self.ui_nueva_compra),
                        self._inflate_form_table(self.ui_nueva_compra)
                    )
                )

            except Exception as e:
                print(f"Error cargando proveedores: {e}")
                
        self.ui_nueva_compra.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_compra.pushButtonAgregarProducto.clicked.connect(
            lambda: (agrega_prodcuto_a_fila(self.ui_nueva_compra), self._inflate_form_table(self.ui_nueva_compra))
        )
        self.ui_nueva_compra.pushButtonQuitarProducto.clicked.connect(
            lambda: (borrar_fila(self.ui_nueva_compra), self._inflate_form_table(self.ui_nueva_compra))
        )
        self.ui_nueva_compra.pushButtonAceptar.clicked.connect(
            lambda: SaveSellIntoDb(self.ui_nueva_compra, ui=self, form=Form)
        )

    def _center_header(self):
        try:
            self.treeWidget.header().setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass
        hi = self.treeWidget.headerItem()
        for col in range(self.treeWidget.columnCount()):
            hi.setTextAlignment(col, Qt.AlignCenter)

    def _filtrar(self, texto: str):
        q = (texto or "").strip().lower()
        root = self.treeWidget.rootIndex()
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            proveedor = (item.text(2) or "").lower()
            medio = (item.text(4) or "").lower()
            factura = (item.text(5) or "").lower()
            visible = (q in proveedor) or (q in medio) or (q in factura)
            self.treeWidget.setRowHidden(i, root, not visible)
        self._post_refresh()

    def _post_refresh(self):
        self._ajustar_columnas()
        self._center_cells()
        self._neutralize_option_buttons()
        self._restyle_form_tables()
        try:
            current_width = self.treeWidget.columnWidth(OPCIONES_COL)
            if current_width < OPCIONES_MIN_WIDTH:
                self.treeWidget.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)
        except Exception:
            pass

    def _ajustar_columnas(self):
        header = self.treeWidget.header()
        for col in (1, 2, 3, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)
        self._center_header()

    def _center_cells(self):
        def process_item(item):
            for col in (1, 2, 3, 4, 5):
                item.setTextAlignment(col, Qt.AlignCenter)
            for k in range(item.childCount()):
                process_item(item.child(k))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(item, OPCIONES_COL)
            if w:
                lay = w.layout()
                if lay:
                    lay.setContentsMargins(0, 0, 0, 0)
                    lay.setAlignment(Qt.AlignCenter)

    def _neutralize_option_buttons(self):
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(item, OPCIONES_COL)
            if not w:
                continue
            for btn in w.findChildren(QPushButton):
                btn.setCursor(Qt.PointingHandCursor)
                btn.setMinimumHeight(BTN_MIN_HEIGHT)
                btn.setStyleSheet("QPushButton{background: transparent; border: none; color: palette(text);} QPushButton:disabled{opacity:0.6;}")
                btn.style().unpolish(btn); btn.style().polish(btn)
            lay = w.layout()
            if lay:
                lay.setContentsMargins(0, 0, 0, 0)
                lay.setAlignment(Qt.AlignCenter)

    def _reapply_theme_dependent_styles(self):
        self._neutralize_option_buttons()
        self._restyle_form_tables()

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        if item is None:
            return
        if item.parent() is not None:
            return
        if item.data(0, ROLE_DETAILS_LOADED):
            item.setExpanded(not item.isExpanded())
            return
        ok = self._cargar_detalles_compra(item)
        if ok:
            item.setData(0, ROLE_DETAILS_LOADED, True)
            item.setExpanded(True)

    def _format_money(self, value):
        try:
            return f"Gs. {float(value):,.0f}".replace(",", ".")
        except Exception:
            return str(value)

    def _cargar_detalles_compra(self, item_compra: QTreeWidgetItem) -> bool:
        compra_id = (item_compra.text(0) or "").strip()
        if not compra_id:
            return False
        detalles = None
        try:
            with conexion() as c, c.cursor() as cur:
                try:
                    cur.execute("""
                        SELECT p.nombre, cd.cantidad, cd.precio_unitario, (cd.cantidad * cd.precio_unitario) AS subtotal
                        FROM compras_detalle cd
                        JOIN productos p ON p.id_producto = cd.id_producto
                        WHERE cd.id_compra = %s
                        ORDER BY p.nombre;
                    """, (compra_id,))
                    detalles = cur.fetchall()
                except Exception:
                    detalles = None
                if not detalles:
                    try:
                        cur.execute("""
                            SELECT descripcion, cantidad, precio, (cantidad*precio) AS subtotal
                            FROM compras_detalle
                            WHERE id_compra = %s
                            ORDER BY 1;
                        """, (compra_id,))
                        detalles = cur.fetchall()
                    except Exception:
                        detalles = None
                if not detalles:
                    try:
                        cur.execute("""
                            SELECT COALESCE(nombre, descripcion) AS desc, COALESCE(cantidad, 1) AS cant,
                                   COALESCE(precio_unitario, precio, 0) AS pu,
                                   COALESCE(subtotal, COALESCE(cantidad,1)*COALESCE(precio_unitario, precio,0)) AS subtotal
                            FROM compras_detalle
                            WHERE id_compra = %s
                            ORDER BY 1;
                        """, (compra_id,))
                        detalles = cur.fetchall()
                    except Exception:
                        detalles = []
        except Exception:
            detalles = []
        if detalles is None:
            detalles = []
        for fila in detalles:
            try:
                nombre = str(fila[0])
                cant = fila[1]
                pu = fila[2]
                sub = fila[3]
            except Exception:
                nombre = str(fila[0]) if len(fila) > 0 else ""
                cant = fila[1] if len(fila) > 1 else ""
                pu = fila[2] if len(fila) > 2 else ""
                sub = fila[3] if len(fila) > 3 else ""
            child = QTreeWidgetItem(item_compra, ["", "", f"• {nombre}", self._format_money(sub), "", "", ""])
            child.setFirstColumnSpanned(True)
            child.setTextAlignment(2, Qt.AlignLeft | Qt.AlignVCenter)
            child.setTextAlignment(3, Qt.AlignCenter)
            self.treeWidget.setItemWidget(child, OPCIONES_COL, QWidget())
        return len(detalles) > 0

    def _set_today_default_date(self):
        today = QDate.currentDate()
        edits = self.formulario_nueva_compra.findChildren(QDateEdit)
        if edits:
            for e in edits:
                e.setDate(today)
            return
        dt_edits = self.formulario_nueva_compra.findChildren(QDateTimeEdit)
        if dt_edits:
            for e in dt_edits:
                try:
                    e.setDate(today)
                except Exception:
                    e.setDateTime(QDateTime.currentDateTime())
            return
        lines = self.formulario_nueva_compra.findChildren(QLineEdit)
        for le in lines:
            name = (le.objectName() or "").lower()
            ph = (le.placeholderText() or "").lower()
            if "fecha" in name or "fecha" in ph or "date" in name:
                le.setText(today.toString("yyyy-MM-dd"))
                return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QToolTip {
        color: white;
        background-color: #2b2b2b;
        border: 1px solid #555;
    }
    """)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
