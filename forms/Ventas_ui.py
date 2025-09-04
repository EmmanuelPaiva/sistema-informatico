import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import (
    QCoreApplication, QMetaObject, QRect, Qt, QPropertyAnimation, QObject, QEvent
)
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QWidget, QMainWindow, QFileDialog, QMessageBox,
    QSizePolicy, QFrame, QHBoxLayout
)

from forms.formularioVentas import Ui_Form as nuevaVentaUi
from db.conexion import conexion
from db.ventas_queries import (
    agrega_prodcuto_a_fila, agregar_filas, guardar_venta_en_db, cargar_ventas,
    actualizar_subtotal, actualizar_venta_en_db, buscar_ventas
)
from utils.utilsVentas import calcular_total_general, borrar_fila, toggle_subtabla
from reports.excel import export_qtable_to_excel

# === Estilos y helpers Rodler (paleta clara) ===
from forms.ui_helpers import (
    apply_global_styles, mark_title, make_primary, make_danger, style_search
)

# Ajustes para evitar corte de texto en Opciones
OPCIONES_MIN_WIDTH = 168     # subí el mínimo
BTN_MIN_WIDTH = 88           # ancho mínimo por botón
BTN_MIN_HEIGHT = 30          # altura un poco mayor para que no corte
ROW_HEIGHT = 46              # filas más cómodas


class _ResizeWatcher(QObject):
    """Observa resizeEvent del QTreeWidget para reajustar columnas."""
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.owner.ajustar_columnas()
        return False


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1000, 620)

        # ===== Layout raíz =====
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(10)

        # ===== Encabezado (Título) =====
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setText("Ventas")
        mark_title(self.label)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        # === Fila de controles: Buscador + Exportar + Nueva venta (alineados) ===
        self.controlsFrame = QFrame(Form)
        self.controlsFrame.setFrameShape(QFrame.NoFrame)
        controlsLayout = QHBoxLayout(self.controlsFrame)
        controlsLayout.setContentsMargins(0, 0, 0, 0)
        controlsLayout.setSpacing(10)

        # Buscador
        self.lineEdit = QLineEdit(self.controlsFrame)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setPlaceholderText("Buscar venta…")
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setMinimumWidth(260)
        self.lineEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        style_search(self.lineEdit)
        controlsLayout.addWidget(self.lineEdit, 1)

        # Botón Exportar (primario)
        self.pushButton_2 = QPushButton(self.controlsFrame)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setText("Exportar")
        self.pushButton_2.setCursor(Qt.PointingHandCursor)
        self.pushButton_2.setMinimumHeight(BTN_MIN_HEIGHT)
        self.pushButton_2.setMinimumWidth(BTN_MIN_WIDTH)
        make_primary(self.pushButton_2)
        self.pushButton_2.clicked.connect(self.exportar_excel_ventas)
        controlsLayout.addWidget(self.pushButton_2)

        # Botón Nueva venta (primario)
        self.pushButton = QPushButton(self.controlsFrame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setText("Nueva venta")
        self.pushButton.setCursor(Qt.PointingHandCursor)
        self.pushButton.setMinimumHeight(BTN_MIN_HEIGHT)
        self.pushButton.setMinimumWidth(BTN_MIN_WIDTH)
        make_primary(self.pushButton)
        controlsLayout.addWidget(self.pushButton)

        # Fila controles debajo del título, misma columna
        self.gridLayout.addWidget(self.controlsFrame, 1, 0, 1, 1)

        # ===== Wrapper de tabla con borde redondeado (como Productos) =====
        self.tableWrapper = QFrame(Form)
        self.tableWrapper.setObjectName("tablaWrapper")
        self.tableWrapper.setStyleSheet("""
        #tablaWrapper {
            background: #ffffff;
            border: 1px solid #dfe7f5;
            border-radius: 12px;
        }
        QTreeWidget {
            background: #ffffff;
            border: none; /* el borde lo pone el wrapper */
        }
        QHeaderView {
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            background: transparent; /* evita “baldosa” cuadrada */
        }
        QHeaderView::section {
            background: #f7f9fc;
            color: #0d1b2a;
            padding: 8px;
            border: none;
            border-right: 1px solid #dfe7f5;
        }
        QHeaderView::section:first {
            border-top-left-radius: 12px;
        }
        QHeaderView::section:last {
            border-top-right-radius: 12px;
            border-right: none; /* sin línea en el borde derecho */
        }
        QTreeWidget::item:selected {
            background: rgba(144,202,249,.25);
            color: #0d1b2a;
        }
        """)
        wrapperLayout = QHBoxLayout(self.tableWrapper)
        # Margen en 0 para que el header calce EXACTO con el borde redondeado
        wrapperLayout.setContentsMargins(0, 0, 0, 0)
        wrapperLayout.setSpacing(0)

        # ===== TABLA (árbol con subfilas) =====
        self.treeWidget = QTreeWidget(self.tableWrapper)
        self.treeWidget.setObjectName(u"treeWidget")
        wrapperLayout.addWidget(self.treeWidget)
        self.gridLayout.addWidget(self.tableWrapper, 2, 0, 1, 1)

        # Config básica
        self.treeWidget.setColumnCount(8)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Cliente", "Cantidad", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setColumnHidden(0, True)
        self.treeWidget.setRootIsDecorated(False)   # look más “tabla”
        self.treeWidget.setUniformRowHeights(True)  # performance y altura consistente
        self.treeWidget.setIndentation(0)
        self.treeWidget.setStyleSheet(f"QTreeWidget::item {{ height: {ROW_HEIGHT}px; }}")

        # Header y tamaños
        header = self.treeWidget.header()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)

        # Columnas visibles y equilibradas: 1..6 Stretch; 7 (Opciones) a contenido con mínimo.
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (oculto)
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Fecha
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Cliente
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Cantidad
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Total
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Medio
        header.setSectionResizeMode(6, QHeaderView.Stretch)           # Factura
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Opciones

        # Señales
        self.treeWidget.itemClicked.connect(lambda item, col: toggle_subtabla(item))

        # Buscador: llama a buscar_ventas y luego retoca (colores y columnas)
        self.lineEdit.textChanged.connect(self._buscar_y_postprocesar)

        # Botón nueva venta
        self.pushButton.clicked.connect(lambda: self.abrir_formulario_nueva_venta(Form))

        # Cargar ventas inicial
        cargar_ventas(self, Form)
        self._post_refresh()

        # Watcher para recalcular columnas en resize
        self._resizeWatcher = _ResizeWatcher(self)
        self.treeWidget.installEventFilter(self._resizeWatcher)

        # Estilos globales claros
        apply_global_styles(Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Ventas", None))

    # ======= Exportar =======
    def exportar_excel_ventas(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(
                None,
                "Guardar como",
                "Ventas.xlsx",
                "Excel (*.xlsx)"
            )
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

    # FORMULARIO DE VENTAS (alta / edición)
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

        # Animación deslizable
        self.anim = QPropertyAnimation(self.formulario_nueva_venta, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Cargar combos sólo en ALTA
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

            # primer cálculo
            actualizar_subtotal(0, self.ui_nueva_venta)
            calcular_total_general(self.ui_nueva_venta)
            self.ui_nueva_venta.pushButtonAceptar.clicked.connect(
                lambda: guardar_venta_en_db(self.ui_nueva_venta, self, Form)
            )

        self.ui_nueva_venta.pushButtonAgregarProducto.clicked.connect(lambda: agrega_prodcuto_a_fila(self.ui_nueva_venta))
        self.ui_nueva_venta.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_venta.pushButtonQuitarProducto.clicked.connect(lambda: borrar_fila(self.ui_nueva_venta))

    # ---------- BÚSQUEDA + postprocesado ----------
    def _buscar_y_postprocesar(self, texto: str):
        """Aplica buscar_ventas y luego ajusta estilos/anchos/botones."""
        buscar_ventas(self, texto, None)  # la función ya usa self y actualiza el tree
        self._post_refresh()

    # ---------- Post-carga: columnas + color botones ----------
    def _post_refresh(self):
        """Ajusta columnas y colorea botones de Opciones."""
        self.ajustar_columnas()
        self._colorize_op_buttons()

    # ---------- Ajustes de columnas ----------
    def ajustar_columnas(self):
        """Asegura columnas 1..6 iguales y 7 (Opciones) más chica con mínimo."""
        header = self.treeWidget.header()
        for col in (1, 2, 3, 4, 5, 6):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        current_width = self.treeWidget.columnWidth(7)
        if current_width < OPCIONES_MIN_WIDTH:
            self.treeWidget.setColumnWidth(7, OPCIONES_MIN_WIDTH)

    # ---------- Colorear botones Editar/Eliminar ----------
    def _colorize_op_buttons(self):
        """Busca widgets en columna 'Opciones' y aplica make_primary / make_danger, evitando cortes."""
        def process_item(item):
            w = self.treeWidget.itemWidget(item, 7)
            if w is not None:
                for btn in w.findChildren(QPushButton):
                    text = (btn.text() or "").strip().lower()
                    btn.setMinimumHeight(BTN_MIN_HEIGHT)
                    btn.setMinimumWidth(BTN_MIN_WIDTH)
                    btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                    if "eliminar" in text or "borrar" in text:
                        make_danger(btn)
                    elif "editar" in text:
                        make_primary(btn)
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
