# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, Qt, QMetaObject, QPropertyAnimation, QRect, QEvent, QObject)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QTableWidget, QHeaderView)
from forms.AgregarEmpleados import Ui_Form as FormularioEmpleados
from db.clientes_queries import (
    guardar_registro,
    cargar_clientes,
    buscar_clientes,
    editar_cliente,
    obtener_cliente_por_id,
)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(939, 672)
        Form.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: Arial;
            }
            QLineEdit {
                border: none;
                border-bottom: 2px solid #00bcd4;
                padding: 4px;
                color: #333;
                min-height: 30px;
                font-size: 14px;
            }
            QLineEdit:focus {
                color: #000;
            }
            QPushButton {
                background-color: #00bcd4;
                color: white;
                padding: 8px 16px;
                min-height: 22px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00acc1;
            }
            QLabel {
                color: #00bcd4;
                font-weight: bold;
                font-size: 18px;
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                background-color: #ffffff;
                font-size: 14px;
                alternate-background-color: #f6f6f6;
                gridline-color: #d0d0d0;
                selection-background-color: #00bcd4;
                selection-color: white;
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
                color: #333;
            }

            QTableWidget::item:selected {
                background-color: #00acc1;
                color: white;
            }

            QHeaderView::section {
                background-color: #00bcd4;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 14px;
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
        self.label_title.setText("Empleados")
        self.header_layout.addWidget(self.label_title)

        # Search + Button aligned
        self.search_layout = QHBoxLayout()
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_layout.setSpacing(10)

        self.lineEdit = QLineEdit(self.header_frame)
        self.lineEdit.setPlaceholderText("Buscar por nombre o RUC/CI")
        self.lineEdit.setMinimumWidth(int(Form.width() * 0.5))
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.search_layout.addWidget(self.lineEdit)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.search_layout.addWidget(spacer)

        self.newButton = QPushButton(self.header_frame)
        self.newButton.setText("Nuevo empleado")
        self.newButton.setFixedWidth(150)
        self.newButton.setMinimumHeight(22)   
        self.search_layout.addWidget(self.newButton)
        self.newButton.clicked.connect(lambda: self.abrir_formulario(Form))
        
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
        header.setStretchLastSection(True)
        for col in range(self.tableWidget.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        self.verticalLayout.addWidget(self.tableWidget)

        self.gridLayout.addWidget(self.table_frame, 1, 0, 1, 1)

        # Conectar búsqueda en tiempo real
        self.lineEdit.textChanged.connect(
            lambda text: buscar_clientes(text, self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)
        )

        # Cargar clientes inicialmente (pasa el callback de edición y el widget Form)
        cargar_clientes(self.tableWidget, edit_callback=self.abrir_formulario_editar, main_form_widget=Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Clientes", None))
        
    def cancelar(self, Form):
        if hasattr(self, 'formularioCliente') and self.formularioEmpleados.isVisible():
            self.formularioEmpleados.close()
        
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

        self.ui_nuevo_empleados = FormularioEmpleados()
        self.formularioEmpleados = QWidget()
        self.ui_nuevo_cliente.setupUi(self.formularioEmpleados)

        self.formularioEmpleados.setParent(Form)
        self.formularioEmpleados.show()
        
        # Reordenar layout para mostrar formulario
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.formularioEmpleados, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)
        
        # Ajustes de tamaño y animación
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioEmpleados.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()

        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioEmpleados.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioEmpleados, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioEmpleados)
        Form.installEventFilter(self.resize_filter)
        
        # Conectar botones del formulario recién creado
        # Asumo que en forms.AgregarClientes los botones se llaman pushButton (guardar) y pushButtonCancelar
        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: guardar_registro(self.ui_nuevo_cliente, self.formularioEmpleados, self.tableWidget, self.abrir_formulario_editar, Form)
        )

    def abrir_formulario_editar(self, Form, id_cliente):
        # Cerrar cualquier formulario abierto y abrir uno nuevo pre-llenado
        if hasattr(self, 'formularioCliente') and self.formularioEmpleados.isVisible():
            self.formularioEmpleados.close()

        self.ui_nuevo_cliente = FormularioEmpleados()
        self.formularioEmpleados = QWidget()
        self.ui_nuevo_cliente.setupUi(self.formularioEmpleados)

        self.formularioEmpleados.setParent(Form)
        self.formularioEmpleados.show()

        # Reordenar layout
        try:
            self.gridLayout.removeWidget(self.header_frame)
            self.gridLayout.removeWidget(self.table_frame)
        except Exception:
            pass

        self.gridLayout.addWidget(self.header_frame, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.formularioEmpleados, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.table_frame, 2, 0, 1, 1)

        # Ajustes y animación
        def ajustar_formulario():
            ancho_formulario = Form.width()
            alto_formulario = int(Form.height() * 0.40)
            self.formularioEmpleados.setGeometry(0, 0, ancho_formulario, alto_formulario)

        ajustar_formulario()

        ancho_formulario = Form.width()
        alto_formulario = int(Form.height() * 0.40)

        self.formularioEmpleados.setGeometry(0, -alto_formulario, ancho_formulario, alto_formulario)
        self.anim = QPropertyAnimation(self.formularioEmpleados, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(0, -alto_formulario, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(0, 0, ancho_formulario, alto_formulario))
        self.anim.start()

        # Reajustar el formulario si el Form cambia de tamaño
        self.resize_filter = ResizeHandler(Form, self.formularioEmpleados)
        Form.installEventFilter(self.resize_filter)

        # Cargar datos del cliente y setear en los campos
        cliente = obtener_cliente_por_id(id_cliente)
        if cliente:
            # cliente expected: (id, nombre, email, telefono, ruc_ci)
            _, nombre, email, telefono, ruc_ci = cliente
            # Ajustar campos según los nombres del form
            self.ui_nuevo_cliente.lineEditNombre.setText(nombre)
            self.ui_nuevo_cliente.lineEditRuc_Ci.setText(str(ruc_ci) if ruc_ci is not None else "")
            self.ui_nuevo_cliente.lineEditTelefono.setText(str(telefono) if telefono is not None else "")
            self.ui_nuevo_cliente.lineEditCorreo.setText(email if email is not None else "")

        # Conectar botones: cancelar y guardar (que llamará a editar_cliente)
        self.ui_nuevo_cliente.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nuevo_cliente.pushButtonAceptar.clicked.connect(
            lambda: editar_cliente(self.ui_nuevo_cliente, self.tableWidget, id_cliente, self.formularioEmpleados, self.abrir_formulario_editar, Form)
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
