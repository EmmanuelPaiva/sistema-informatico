# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, Qt, QMetaObject, QPropertyAnimation, QRect, QEvent, QObject)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QTableWidget, QHeaderView,
                               QFileDialog, QMessageBox)  # <-- añadidos para exportar
from forms.agregarProveedor import Ui_Form as FormularioProv
from db.prov_queries import (
    guardar_registro,
    cargar_proveedores,
    buscar_proveedores,
    editar_proveedor,
    obtener_proveedor_por_id,
)

# ==== Estilos/helpers del sistema ====
try:
    from ui_helpers import apply_global_styles, mark_title, make_primary, style_table, style_search
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles, mark_title, make_primary, style_table, style_search

# Exportar a Excel
from reports.excel import export_qtable_to_excel

ROW_HEIGHT = 46   # filas un poquito más separadas

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(939, 672)
        Form.setStyleSheet("""
            QWidget {
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
                background-color: #f9fbfd;
            }

            /* Controles */
            QLineEdit, QDateTimeEdit, QComboBox {
                padding: 8px;
                border: 1px solid #b0c4de;
                border-radius: 8px;
                background-color: #ffffff;
            }

            QLineEdit:focus, QDateTimeEdit:focus, QComboBox:focus {
                border: 1px solid #5dade2;
                background-color: #eef7ff;
            }

            /* Botones */
            QPushButton {
                padding: 10px 18px;
                background-color: #5dade2;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }

            QPushButton:hover {
                background-color: #3498db;
            }

            QPushButton:pressed {
                background-color: #2e86c1;
            }

            /* Labels */
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }

            /* Tabla */
            QTableWidget {
                border: 1px solid #d6eaf8;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #d0d0d0;
            }

            QTableWidget::item {
                padding: 6px;
                font-size: 12px;
                color: #333333;
                height: 40px;
            }

            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-size: 13px;
            }

            QTableCornerButton::section {
                background-color: #3498db;
            }

            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #a0c4ff;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setSpacing(10)

        # ---- Header ----
        self.header_frame = QFrame(Form)
        self.header_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.header_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.header_layout = QVBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(15)

        # Title
        self.label_title = QLabel(self.header_frame)
        self.label_title.setText("Proveedores")
        self.header_layout.addWidget(self.label_title)
        # estilos del sistema para título
        mark_title(self.label_title)

        # Search + Buttons aligned
        self.search_layout = QHBoxLayout()
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_layout.setSpacing(10)

        self.lineEdit = QLineEdit(self.header_frame)
        self.lineEdit.setPlaceholderText("Buscar proveedor")
        self.lineEdit.setMinimumWidth(int(Form.width() * 0.5))
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_layout.addWidget(self.lineEdit)
        # estilo buscador
        style_search(self.lineEdit)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.search_layout.addWidget(spacer)

        # Botón Exportar (nuevo)
        self.btnExportar = QPushButton(self.header_frame)
        self.btnExportar.setText("Exportar")
        self.btnExportar.setFixedWidth(120)
        self.btnExportar.setMinimumHeight(22)
        self.btnExportar.clicked.connect(self.exportar_excel_proveedores)
        self.search_layout.addWidget(self.btnExportar)
        make_primary(self.btnExportar)

        self.newButton = QPushButton(self.header_frame)
        self.newButton.setText("Nuevo proveedor")
        self.newButton.setFixedWidth(150)
        self.newButton.setMinimumHeight(22)   
        self.search_layout.addWidget(self.newButton)
        self.newButton.clicked.connect(lambda: self.abrir_formulario(Form))
        make_primary(self.newButton)

        self.header_layout.addLayout(self.search_layout)
        self.gridLayout.addWidget(self.header_frame, 0, 0, 1, 1)

        # ---- Table ----
        self.table_frame = QFrame(Form)
        self.table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.table_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout = QVBoxLayout(self.table_frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.tableWidget = QTableWidget(self.table_frame)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Dirección", "Email", "Opciones"])
        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(False)  # control manual de "Opciones"
        # tamaños de columna: datos Stretch y Opciones a contenido
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Teléfono
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Dirección
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Email
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Opciones (no se corta)
        # filas con un poco más de aire
        self.tableWidget.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        # estilos de tabla del sistema
        style_table(self.tableWidget)

        self.verticalLayout.addWidget(self.tableWidget)

        self.gridLayout.addWidget(self.table_frame, 1, 0, 1, 1)

        # Conectar búsqueda en tiempo real
        self.lineEdit.textChanged.connect(
            lambda text: buscar_proveedores(text, self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        )

        # Cargar proveedores inicialmente (pasa el callback de edición y el widget Form)
        cargar_proveedores(self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)

        # aplicar estilos globales del sistema
        apply_global_styles(Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Proveedores", None))
    
    # Exportar a Excel
    def exportar_excel_proveedores(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(
                None,
                "Guardar como",
                "Proveedores.xlsx",
                "Excel (*.xlsx)"
            )
            if not ruta:
                return
            export_qtable_to_excel(self.tableWidget, ruta, title="Proveedores")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")
        
    def cancelar(self, Form):
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            self.formularioProveedor.close()
        
        # Reagregamos header y tabla en su posición por si fueron movidos
        try:
            # Si el formulario fue removido del grid, intentamos restaurar el orden
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        # Añadimos header y tabla a sus posiciones por defecto
        try:
            self.gridLayout.addWidget(self.header_frame, 0, 0, 1, 1)
            self.gridLayout.addWidget(self.table_frame, 1, 0, 1, 1)
        except Exception:
            pass
        
    def abrir_formulario(self, Form):
        # Evitar abrir múltiples formularios
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            return

        self.ui_nuevo_proveedor = FormularioProv()
        self.formularioProveedor = QWidget()
        self.ui_nuevo_proveedor.setupUi(self.formularioProveedor)

        self.formularioProveedor.setParent(Form)
        self.formularioProveedor.show()
        
        # Eliminar widgets anteriores del gridLayout (si existen) y reordenar
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass
    
        # Agregar el formulario arriba, el header abajo, y la tabla aún más abajo
        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)

        self.gridLayout.addWidget(self.formularioProveedor, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)
        
        # Funciones internas para ajustar altura y posición
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioProveedor.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()  # llamada inicial

        # Animación para deslizar desde arriba hacia abajo
        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioProveedor.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioProveedor, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioProveedor)
        Form.installEventFilter(self.resize_filter)
        
        # Conectar botones del formulario recién creado
        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(
            lambda: guardar_registro(self.ui_nuevo_proveedor, self.formularioProveedor, self.tableWidget, self.abrir_formulario_editar, Form)
        )

    def abrir_formulario_editar(self, Form, id_proveedor):
        # Cerrar cualquier formulario abierto y abrir uno nuevo pre-llenado
        if hasattr(self, 'formularioProveedor') and self.formularioProveedor.isVisible():
            self.formularioProveedor.close()

        self.ui_nuevo_proveedor = FormularioProv()
        self.formularioProveedor = QWidget()
        self.ui_nuevo_proveedor.setupUi(self.formularioProveedor)

        self.formularioProveedor.setParent(Form)
        self.formularioProveedor.show()

        # Reordenar layout como en "abrir_formulario"
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.formularioProveedor, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)

        # Ajustes y animación
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioProveedor.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()

        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioProveedor.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioProveedor, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioProveedor)
        Form.installEventFilter(self.resize_filter)

        # Cargar datos del proveedor y setear en los campos
        proveedor = obtener_proveedor_por_id(id_proveedor)
        if proveedor:
            _, nombre, telefono, direccion, correo = proveedor
            self.ui_nuevo_proveedor.lineEditNombre.setText(nombre)
            self.ui_nuevo_proveedor.lineEditDireccion.setText(direccion)
            self.ui_nuevo_proveedor.lineEditTelefono.setText(str(telefono))
            self.ui_nuevo_proveedor.lineEditCorreo.setText(correo)

        # Conectar botones: cancelar y guardar (que llamará a editar_proveedor)
        self.ui_nuevo_proveedor.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_proveedor.pushButton.clicked.connect(
            lambda: editar_proveedor(self.ui_nuevo_proveedor, self.tableWidget, id_proveedor, self.formularioProveedor, self.abrir_formulario_editar, Form)
        )


class ResizeHandler(QObject):
    def __init__(self, form, widget):
        super().__init__()
        self.form = form
        self.widget = widget

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            ancho = self.form.width()
            alto = int(self.form.height() * 0.40)
            self.widget.setGeometry(0, 0, ancho, alto)
        return False
        
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
