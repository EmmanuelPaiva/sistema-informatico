# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, Qt, QMetaObject, QPropertyAnimation, QRect, QEvent, QObject)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QTableWidget, QHeaderView,
                               QFileDialog, QMessageBox)
from forms.AgregarClientes import Ui_Form as FormularioClientes
from db.clientes_queries import (
    guardar_registro,
    cargar_clientes,
    buscar_clientes,
    editar_cliente,
    obtener_cliente_por_id,
)
from reports.excel import export_qtable_to_excel

# >>> Estilos del sistema (ui_helpers.py)
try:
    from ui_helpers import apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search  # noqa
except ModuleNotFoundError:
    # fallback por si está dentro de forms/
    from forms.ui_helpers import apply_global_styles, mark_title, make_primary, make_danger, style_table, style_search  # noqa


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
        self.label_title.setText("Clientes")
        self.header_layout.addWidget(self.label_title)

        # >>> Título con estilo del sistema
        mark_title(self.label_title)

        # Search + Button aligned
        self.search_layout = QHBoxLayout()
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_layout.setSpacing(10)

        self.lineEdit = QLineEdit(self.header_frame)
        self.lineEdit.setPlaceholderText("Buscar por nombre o RUC/CI")
        self.lineEdit.setMinimumWidth(int(Form.width() * 0.5))
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_layout.addWidget(self.lineEdit)

        # >>> Estilo del buscador
        style_search(self.lineEdit)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.search_layout.addWidget(spacer)

        # Botón Exportar (nuevo)
        self.btnExportar = QPushButton(self.header_frame)
        self.btnExportar.setText("Exportar")
        self.btnExportar.setFixedWidth(120)
        self.btnExportar.setMinimumHeight(22)
        self.btnExportar.clicked.connect(self.exportar_excel_clientes)
        self.search_layout.addWidget(self.btnExportar)

        # >>> Botones con estilo primario
        make_primary(self.btnExportar)

        self.newButton = QPushButton(self.header_frame)
        self.newButton.setText("Nuevo cliente")
        self.newButton.setFixedWidth(150)
        self.newButton.setMinimumHeight(22)   
        self.search_layout.addWidget(self.newButton)
        self.newButton.clicked.connect(lambda: self.abrir_formulario(Form))

        # >>> Botones con estilo primario
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
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "CI/RUC", "Email", "Opciones"])
        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(False)  # para controlar "Opciones"
        # Ajustes de columnas para visibilidad:
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Teléfono
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # CI/RUC
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Email
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Opciones (a contenido)
        # Filas un poquito más separadas
        self.tableWidget.verticalHeader().setDefaultSectionSize(46)

        # >>> Estilo de tabla del sistema
        style_table(self.tableWidget)

        self.verticalLayout.addWidget(self.tableWidget)

        self.gridLayout.addWidget(self.table_frame, 1, 0, 1, 1)

        # Conectar búsqueda en tiempo real
        self.lineEdit.textChanged.connect(
            lambda text: buscar_clientes(text, self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        )

        # Cargar clientes inicialmente (pasa el callback de edición y el widget Form)
        cargar_clientes(self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)

        # >>> Aplicar estilos globales del sistema al final
        apply_global_styles(Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Clientes", None))
    
    def exportar_excel_clientes(self):
        try:
            ruta, _ = QFileDialog.getSaveFileName(
                None,
                "Guardar como",
                "Clientes.xlsx",
                "Excel (*.xlsx)"
            )
            if not ruta:
                return
            export_qtable_to_excel(self.tableWidget, ruta, title="Clientes")
            QMessageBox.information(None, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo exportar:\n{e}")

    def cancelar(self, Form):
        if hasattr(self, 'formularioCliente') and self.formularioCliente.isVisible():
            self.formularioCliente.close()
        
        # Reagregamos header y tabla en su posición por si fueron movidos
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        try:
            self.gridLayout.addWidget(self.header_frame, 0, 0, 1, 1)
            self.gridLayout.addWidget(self.table_frame, 1, 0, 1, 1)
        except Exception:
            pass
        
    def abrir_formulario(self, Form):
        # Evitar abrir múltiples formularios
        if hasattr(self, 'formularioCliente') and self.formularioCliente.isVisible():
            return

        self.ui_nuevo_cliente = FormularioClientes()
        self.formularioCliente = QWidget()
        self.ui_nuevo_cliente.setupUi(self.formularioCliente)

        self.formularioCliente.setParent(Form)
        self.formularioCliente.show()
        
        # Reordenar layout para mostrar formulario
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.formularioCliente, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)
        
        # Ajustes de tamaño y animación
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioCliente.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()

        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioCliente.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioCliente, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioCliente)
        Form.installEventFilter(self.resize_filter)
        
        # Conectar botones del formulario recién creado
        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: guardar_registro(self.ui_nuevo_cliente, self.formularioCliente, self.tableWidget, self.abrir_formulario_editar, Form)
        )

    def abrir_formulario_editar(self, Form, id_cliente):
        # Cerrar cualquier formulario abierto y abrir uno nuevo pre-llenado
        if hasattr(self, 'formularioCliente') and self.formularioCliente.isVisible():
            self.formularioCliente.close()

        self.ui_nuevo_cliente = FormularioClientes()
        self.formularioCliente = QWidget()
        self.ui_nuevo_cliente.setupUi(self.formularioCliente)

        self.formularioCliente.setParent(Form)
        self.formularioCliente.show()

        # Reordenar layout
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.formularioCliente, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)

        # Ajustes y animación
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioCliente.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()

        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioCliente.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioCliente, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioCliente)
        Form.installEventFilter(self.resize_filter)

        # Cargar datos del cliente y setear en los campos
        cliente = obtener_cliente_por_id(id_cliente)
        if cliente:
            # cliente expected: (id, nombre, email, telefono, ruc_ci)
            _, nombre, email, telefono, ruc_ci = cliente
            self.ui_nuevo_cliente.lineEditNombre.setText(nombre)
            self.ui_nuevo_cliente.lineEditRuc_Ci.setText(str(ruc_ci) if ruc_ci is not None else "")
            self.ui_nuevo_cliente.lineEditTelefono.setText(str(telefono) if telefono is not None else "")
            self.ui_nuevo_cliente.lineEditCorreo.setText(email if email is not None else "")

        # Conectar botones: cancelar y guardar (que llamará a editar_cliente)
        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: editar_cliente(self.ui_nuevo_cliente, self.tableWidget, id_cliente, self.formularioCliente, self.abrir_formulario_editar, Form)
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
