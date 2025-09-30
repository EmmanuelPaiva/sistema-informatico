# ventas_willow.py — reemplaza tu módulo de Ventas por este

import sys, os, platform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from PySide6.QtCore import (
    QCoreApplication, QMetaObject, QRect, Qt, QPropertyAnimation, QObject, QEvent, QSize
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QWidget, QMainWindow, QFileDialog, QMessageBox,
    QSizePolicy, QFrame, QHBoxLayout, QVBoxLayout
)

from forms.formularioVentas import Ui_Form as nuevaVentaUi
from db.conexion import conexion
from db.ventas_queries import (
    agrega_prodcuto_a_fila, agregar_filas, guardar_venta_en_db, cargar_ventas,
    actualizar_subtotal, actualizar_venta_en_db, buscar_ventas
)
from utils.utilsVentas import calcular_total_general, borrar_fila, toggle_subtabla
from reports.excel import export_qtable_to_excel

# Estilos/helpers existentes
from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, make_danger, style_search
)

# === Consistencia con Productos: mismos tamaños/colores ===
OPCIONES_MIN_WIDTH = 140
BTN_MIN_HEIGHT = 28
ROW_HEIGHT = 46
ICON_PX = 18
OPCIONES_COL = 7

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


# ---------------- QSS Willow (idéntico a Productos/Clientes) ----------------
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
  qproperty-iconSize: 18px 18px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

/* TreeWidget / Header / Selección */
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

/* Evitar fondo gris en contenedores embebidos */
QTreeWidget QWidget { background: transparent; border: none; }
"""


class _ResizeWatcher(QObject):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner.ajustar_columnas()
        return False


def _style_action_button(btn: QPushButton, kind: str):
    """
    Aplica estilo sólido azul/rojo, icon-only, sin fondo gris del contenedor,
    iconSize 18px, altura mínima 28px (igual que Productos).
    """
    if kind == "edit":
        btn.setStyleSheet(
            "QPushButton{background:#2979FF;border:1px solid #2979FF;color:#FFFFFF;border-radius:8px;padding:6px;}"
            "QPushButton:hover{background:#3b86ff;}"
        )
        btn.setIcon(icon("edit"))
        btn.setToolTip("Editar venta")
    else:
        btn.setStyleSheet(
            "QPushButton{background:#EF5350;border:1px solid #EF5350;color:#FFFFFF;border-radius:8px;padding:6px;}"
            "QPushButton:hover{background:#f26461;}"
        )
        btn.setIcon(icon("trash"))
        btn.setToolTip("Eliminar venta")
    btn.setText("")  # icon-only
    btn.setCursor(Qt.PointingHandCursor)
    btn.setMinimumHeight(BTN_MIN_HEIGHT)
    btn.setIconSize(QSize(ICON_PX, ICON_PX))


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 620)

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        # ---------------- Header (título + search + botones) ----------------
        self.headerCard = QFrame(Form); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16,12,16,12); hl.setSpacing(10)

        self.label = QLabel("Ventas", self.headerCard)
        self.label.setProperty("role", "pageTitle")
        mark_title(self.label)
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
        self.btnNueva.setProperty("type","primary")
        self.btnNueva.setIcon(icon("plus"))
        make_primary(self.btnNueva)
        hl.addWidget(self.btnNueva)

        self.gridLayout.addWidget(self.headerCard, 0, 0, 1, 1)

        # ---------------- Tabla (TreeWidget) ----------------
        self.tableCard = QFrame(Form); self.tableCard.setObjectName("tableCard")
        tv = QVBoxLayout(self.tableCard); tv.setContentsMargins(0,0,0,0)

        self.treeWidget = QTreeWidget(self.tableCard)
        tv.addWidget(self.treeWidget)
        self.gridLayout.addWidget(self.tableCard, 1, 0, 1, 1)

        # Config básica
        self.treeWidget.setColumnCount(8)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Cliente", "Cantidad", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setColumnHidden(0, True)  # ID siempre oculta
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setStyleSheet(f"QTreeWidget::item {{ height: {ROW_HEIGHT}px; }}")

        header = self.treeWidget.header()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for col in (1,2,3,4,5,6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)

        # Señales
        self.treeWidget.itemClicked.connect(lambda item, col: toggle_subtabla(item))
        self.lineEdit.textChanged.connect(self._buscar_y_postprocesar)
        self.btnNueva.clicked.connect(lambda: self.abrir_formulario_nueva_venta(Form))

        # Datos iniciales
        cargar_ventas(self, Form)
        self._post_refresh()

        # Watcher
        self._resizeWatcher = _ResizeWatcher(self)
        self.treeWidget.installEventFilter(self._resizeWatcher)

        # Estilos
        apply_global_styles(Form)
        Form.setStyleSheet(QSS_WILLOW)

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

    def cancelar(self, Form):
        if not hasattr(self, 'formulario_nueva_venta'):
            return
        ancho_formulario = 300
        alto_formulario = Form.height()
        self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.start()
        self.formulario_nueva_venta.close()

    # ----- Alta / edición -----
    def abrir_formulario_nueva_venta(self, Form, edicion=False):
        if hasattr(self, 'formulario_nueva_venta') and self.formulario_nueva_venta.isVisible():
            return
        self.ui_nueva_venta = nuevaVentaUi()
        self.formulario_nueva_venta = QWidget(Form)
        self.ui_nueva_venta.setupUi(self.formulario_nueva_venta)

        agregar_filas(self.ui_nueva_venta)

        ancho_formulario = 450
        alto_formulario = Form.height()
        self.formulario_nueva_venta.setGeometry(Form.width(), 0, ancho_formulario, alto_formulario)
        self.formulario_nueva_venta.show()

        self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        if not edicion:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            cursor.execute("SELECT id, nombre FROM clientes;")
            clientes = cursor.fetchall()
            for idC, nombreC in clientes:
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

        self.ui_nueva_venta.pushButtonAgregarProducto.clicked.connect(lambda: agrega_prodcuto_a_fila(self.ui_nueva_venta))
        self.ui_nueva_venta.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_venta.pushButtonQuitarProducto.clicked.connect(lambda: borrar_fila(self.ui_nueva_venta))

    # ---------- Buscar + postprocesado ----------
    def _buscar_y_postprocesar(self, texto: str):
        buscar_ventas(self, texto, None)
        self._post_refresh()

    # ---------- Post-carga ----------
    def _post_refresh(self):
        self.ajustar_columnas()
        self._center_cells()
        self._colorize_option_buttons()

    def ajustar_columnas(self):
        header = self.treeWidget.header()
        for col in (1,2,3,4,5,6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(OPCIONES_COL, QHeaderView.ResizeToContents)
        current_width = self.treeWidget.columnWidth(OPCIONES_COL)
        if current_width < OPCIONES_MIN_WIDTH:
            self.treeWidget.setColumnWidth(OPCIONES_COL, OPCIONES_MIN_WIDTH)

    # Centramos contenido en columnas visibles
    def _center_cells(self):
        def process_item(item):
            for col in (1,2,3,4,5,6):
                item.setTextAlignment(col, Qt.AlignCenter)
            for i in range(item.childCount()):
                process_item(item.child(i))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))

    # Botones de Opciones: mismo color/tamaño que Productos (icon-only azul/rojo)
    def _colorize_option_buttons(self):
        def process_item(item):
            w = self.treeWidget.itemWidget(item, OPCIONES_COL)
            if w is not None:
                # asegurar que el contenedor no pinte fondo gris
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
            for i in range(item.childCount()):
                process_item(item.child(i))
        for i in range(self.treeWidget.topLevelItemCount()):
            process_item(self.treeWidget.topLevelItem(i))


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self.ui, 'formulario_nueva_venta'):
            ancho_formulario = self.ui.formulario_nueva_venta.width()
            alto_formulario = self.height()
            self.ui.formulario_nueva_venta.setGeometry(
                self.width() - ancho_formulario, 0,
                ancho_formulario, alto_formulario
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
