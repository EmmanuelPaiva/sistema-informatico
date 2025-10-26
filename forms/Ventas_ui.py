# ventas_willow.py — reemplaza tu módulo de Ventas por este

import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from PySide6.QtCore import (
    QCoreApplication, QMetaObject, QRect, Qt, QPropertyAnimation, QObject, QEvent, QSize, QTimer,
    QDate, QDateTime
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QWidget, QFileDialog, QMessageBox,
    QSizePolicy, QFrame, QHBoxLayout, QVBoxLayout, QMainWindow, QListView,
    QDateEdit, QDateTimeEdit
)

from forms.formularioVentas import Ui_Form as nuevaVentaUi
from db.conexion import conexion
from db.ventas_queries import (
    agrega_prodcuto_a_fila, agregar_filas, guardar_venta_en_db, cargar_ventas,
    actualizar_subtotal, actualizar_venta_en_db, buscar_ventas
)
from utils.utilsVentas import calcular_total_general, borrar_fila, toggle_subtabla
from reports.excel import export_qtable_to_excel

from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, style_search
)

from main.themes import themed_icon

OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ROW_HEIGHT = 46
ICON_PX = 18
OPCIONES_COL = 7
SLIDE_WIDTH = 450

def icon(name: str) -> QIcon:
    return themed_icon(name)


class _ResizeWatcher(QObject):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner.ajustar_columnas()
        return False


class _ParentResizeWatcher(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.ui._sync_form_geometry()
        return False


def _style_action_button(btn: QPushButton, kind: str):
    btn.setText("")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(BTN_MIN_HEIGHT)
    btn.setIconSize(QSize(ICON_PX, ICON_PX))
    btn.setProperty("type", "icon")
    if kind == "edit":
        btn.setProperty("variant", "edit")
        btn.setIcon(icon("edit"))
        btn.setToolTip("Editar venta")
    else:
        btn.setProperty("variant", "delete")
        btn.setIcon(icon("trash"))
        btn.setToolTip("Eliminar venta")
    btn.style().unpolish(btn); btn.style().polish(btn)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 620)

        self._host = Form
        self._slide_width = SLIDE_WIDTH

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        # ---------------- Header (título + search + botones) ----------------
        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16,12,16,12); hl.setSpacing(10)

        self.label = QLabel("Ventas", self.headerCard)
        self.label.setObjectName("ventasTitle")
        self.label.setProperty("role", "pageTitle")
        f = QFont(self.label.font())
        f.setBold(False)
        f.setPointSize(26)  # respaldo; el QSS manda
        self.label.setFont(f)
        mark_title(self.label)
        self.label.setStyleSheet("""
            #ventasTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
        hl.addWidget(self.label)
        hl.addStretch(1)

        self.lineEdit = QLineEdit(self.headerCard)
        self.lineEdit.setObjectName("searchBox")
        self.lineEdit.setPlaceholderText("Buscar venta…")
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setMinimumWidth(260)
        self.lineEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lineEdit.addAction(icon("search"), QLineEdit.LeadingPosition)
        style_search(self.lineEdit)
        hl.addWidget(self.lineEdit, 1)

        self.btnExportar = QPushButton("Exportar", self.headerCard)
        self.btnExportar.setProperty("type","primary")
        self.btnExportar.setIcon(icon("file-spreadsheet"))
        make_primary(self.btnExportar)
        self.btnExportar.clicked.connect(self.exportar_excel_ventas)
        hl.addWidget(self.btnExportar)

        self.btnNueva = QPushButton("Nueva venta", self.headerCard)
        self.btnNueva.setObjectName("btnVentaNueva")
        self.btnNueva.setProperty("type","primary")
        self.btnNueva.setProperty("perm_code", "ventas.create")
        self.btnNueva.setIcon(icon("plus"))
        make_primary(self.btnNueva)
        self.btnNueva.clicked.connect(lambda: self.abrir_formulario_nueva_venta(Form))
        hl.addWidget(self.btnNueva)

        self.gridLayout.addWidget(self.headerCard, 0, 0, 1, 1)

        # ---------------- Tabla (TreeWidget) ----------------
        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.treeWidget = QTreeWidget(self.tableCard)
        tv.addWidget(self.treeWidget)
        self.gridLayout.addWidget(self.tableCard, 1, 0, 1, 1)

        self.treeWidget.setColumnCount(8)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Cliente", "Cantidad", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setColumnHidden(0, True)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setStyleSheet(
            f"""
            QTreeWidget::item {{
                height: {ROW_HEIGHT}px;
                border-bottom: 1px solid palette(mid);
                margin-left: 24px;
                margin-right: 24px;
            }}
            QTreeWidget::item:selected {{
                border-bottom: 1px solid palette(mid);
            }}
            """
        )

        header = self.treeWidget.header()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in (1,2,3,4,5,6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)

        # Centrar header
        self._center_header()

        # Señales
        self.treeWidget.itemClicked.connect(lambda item, col: toggle_subtabla(item))
        self.lineEdit.textChanged.connect(self._buscar_y_postprocesar)

        # Datos iniciales
        cargar_ventas(self, Form)
        self._post_refresh()

        # Watchers
        self._resizeWatcher = _ResizeWatcher(self)
        self.treeWidget.installEventFilter(self._resizeWatcher)
        self._parentWatcher = _ParentResizeWatcher(self)
        Form.installEventFilter(self._parentWatcher)

        # Estilos globales
        apply_global_styles(Form)
        self.label.setStyleSheet("""
            #ventasTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Ventas", None))

    # ======= Exportar =======
    def exportar_excel_ventas(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(None, "Guardar como", "Ventas.xlsx", "Excel (*.xlsx)")
            if not ruta:
                return
            export_qtable_to_excel(self.treeWidget, ruta, title="Ventas")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    # ======= Helpers del slide-out =======
    def _fix_combo_popup(self, combo):
        try:
            view = QListView(combo)
            view.setUniformItemSizes(True)
            view.setAlternatingRowColors(False)
            view.setStyleSheet(
                "QListView{"
                " background: palette(base);"
                " color: palette(text);"
                " border: 1px solid palette(mid);"
                " padding: 0; margin: 0;"
                "}"
                "QListView::item{ padding: 6px 8px; }"
                "QListView::item:selected{"
                " background: palette(highlight);"
                " color: palette(highlighted-text);"
                "}"
            )
            combo.setView(view)
            combo.setStyleSheet(
                "QComboBox{"
                " background: palette(base);"
                " color: palette(text);"
                "}"
                "QComboBox QAbstractItemView{"
                " background: palette(base);"
                " color: palette(text);"
                "}"
            )
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
                spin.setStyleSheet(
                    "QAbstractSpinBox{ background: palette(base); color: palette(text); }"
                )

        prev = tw.styleSheet() or ""
        tw.setStyleSheet(prev + "\nQTableWidget::item{ padding: 0; margin: 0; }\n")

    def _inflate_form_table(self, ui_form):
        tw = getattr(ui_form, "tableWidget", None)
        if tw is None:
            return
        tw.setMinimumHeight(260)
        self._style_form_cell_widgets(ui_form)

    def _sync_form_geometry(self):
        if not hasattr(self, 'formulario_nueva_venta') or not self.formulario_nueva_venta.isVisible():
            return
        host_w = max(self._host.width(), 0)
        host_h = max(self._host.height(), 0)
        panel_w = min(SLIDE_WIDTH, max(280, host_w))
        x = host_w - panel_w
        self.formulario_nueva_venta.setGeometry(x, 0, panel_w, host_h)

    def cancelar(self, Form):
        if not hasattr(self, 'formulario_nueva_venta'):
            return
        if self.formulario_nueva_venta.isVisible():
            w = self.formulario_nueva_venta.width()
            h = Form.height()
            self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
            self.anim.setDuration(300)
            self.anim.setStartValue(QRect(Form.width() - w, 0, w, h))
            self.anim.setEndValue(QRect(Form.width(), 0, w, h))
            self.anim.finished.connect(self.formulario_nueva_venta.close)
            self.anim.start()

    # ----- Alta / edición -----
    def abrir_formulario_nueva_venta(self, Form, edicion=False):
        if hasattr(self, 'formulario_nueva_venta') and self.formulario_nueva_venta.isVisible():
            return
        self.ui_nueva_venta = nuevaVentaUi()
        self.formulario_nueva_venta = QWidget(Form)
        self.ui_nueva_venta.setupUi(self.formulario_nueva_venta)

        self._inflate_form_table(self.ui_nueva_venta)
        agregar_filas(self.ui_nueva_venta)
        self._inflate_form_table(self.ui_nueva_venta)

        # Fecha por defecto: hoy
        self._set_today_default_date()

        w = min(SLIDE_WIDTH, max(280, Form.width()))
        h = Form.height()
        self.formulario_nueva_venta.setGeometry(Form.width(), 0, w, h)
        self.formulario_nueva_venta.show()

        self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, w, h))
        self.anim.setEndValue(QRect(Form.width() - w, 0, w, h))
        self.anim.start()

        QTimer.singleShot(0, self._sync_form_geometry)
        QTimer.singleShot(0, lambda: self._inflate_form_table(self.ui_nueva_venta))
        self.anim.finished.connect(self._sync_form_geometry)

        if not edicion:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            cursor.execute("SELECT id, nombre FROM clientes;")
            for idC, nombreC in cursor.fetchall():
                self.ui_nueva_venta.comboBox.addItem(nombreC, idC)
            if self.ui_nueva_venta.comboBox.count() > 0:
                self.ui_nueva_venta.comboBox.setCurrentIndex(0)
            cursor.close()
            conexion_db.close()

            actualizar_subtotal(0, self.ui_nueva_venta)
            calcular_total_general(self.ui_nueva_venta)
            self.ui_nueva_venta.pushButtonAceptar.clicked.connect(
                lambda: guardar_venta_en_db(self.ui_nueva_venta, self, Form)
            )

        self.ui_nueva_venta.pushButtonAgregarProducto.clicked.connect(
            lambda: (agrega_prodcuto_a_fila(self.ui_nueva_venta), self._inflate_form_table(self.ui_nueva_venta))
        )
        self.ui_nueva_venta.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_venta.pushButtonQuitarProducto.clicked.connect(
            lambda: (borrar_fila(self.ui_nueva_venta), self._inflate_form_table(self.ui_nueva_venta))
        )

    # ---------- Buscar + postprocesado ----------
    def _buscar_y_postprocesar(self, texto: str):
        buscar_ventas(self, texto, None)
        self._post_refresh()

    # ---------- Post-carga ----------
    def _post_refresh(self):
        self.ajustar_columnas()
        self._center_cells()
        self._colorize_option_buttons()
        self._center_header()

    def ajustar_columnas(self):
        header = self.treeWidget.header()
        for col in (1,2,3,4,5,6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)
        if self.treeWidget.columnWidth(OPCIONES_COL) < OPCIONES_MIN_WIDTH:
            self.treeWidget.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)

    def _center_header(self):
        try:
            self.treeWidget.header().setDefaultAlignment(Qt.AlignCenter)
        except Exception:
            pass
        hi = self.treeWidget.headerItem()
        for col in range(self.treeWidget.columnCount()):
            hi.setTextAlignment(col, Qt.AlignCenter)

    def _center_cells(self):
        def process_item(node):
            for col in (1,2,3,4,5,6):
                node.setTextAlignment(col, Qt.AlignCenter)
            for i in range(node.childCount()):
                process_item(node.child(i))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))
        for i in range(self.treeWidget.topLevelItemCount()):
            node = self.treeWidget.topLevelItem(i)
            w = self.treeWidget.itemWidget(node, OPCIONES_COL)
            if w is not None:
                lay = w.layout()
                if lay:
                    lay.setContentsMargins(0,0,0,0)
                    lay.setAlignment(Qt.AlignCenter)

    def _colorize_option_buttons(self):
        def process_item(node):
            w = self.treeWidget.itemWidget(node, OPCIONES_COL)
            if w is not None:
                try:
                    w.setAutoFillBackground(False)
                    w.setAttribute(Qt.WA_StyledBackground, False)
                    w.setAttribute(Qt.WA_NoSystemBackground, True)
                    w.setStyleSheet("background: transparent; border: none;")
                except Exception:
                    pass
                for btn in w.findChildren(QPushButton):
                    txt = (btn.text() or "").lower()
                    if "edit" in txt or "editar" in txt:
                        _style_action_button(btn, "edit")
                    elif "del" in txt or "elimin" in txt or "borrar" in txt:
                        _style_action_button(btn, "delete")
                    btn.style().unpolish(btn); btn.style().polish(btn)
                lay = w.layout()
                if lay:
                    lay.setContentsMargins(0,0,0,0)
                    lay.setAlignment(Qt.AlignCenter)
            for i in range(node.childCount()):
                process_item(node.child(i))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))

    # ======= Fecha por defecto: hoy =======
    def _set_today_default_date(self):
        today = QDate.currentDate()
        edits = self.formulario_nueva_venta.findChildren(QDateEdit)
        if edits:
            for e in edits:
                e.setDate(today)
            return
        dt_edits = self.formulario_nueva_venta.findChildren(QDateTimeEdit)
        if dt_edits:
            for e in dt_edits:
                try:
                    e.setDate(today)
                except Exception:
                    e.setDateTime(QDateTime.currentDateTime())
            return
        lines = self.formulario_nueva_venta.findChildren(QLineEdit)
        for le in lines:
            name = (le.objectName() or "").lower()
            ph   = (le.placeholderText() or "").lower()
            if "fecha" in name or "fecha" in ph or "date" in name:
                le.setText(today.toString("yyyy-MM-dd"))
                return


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self.ui, 'formulario_nueva_venta') and self.ui.formulario_nueva_venta.isVisible():
            self.ui._sync_form_geometry()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
