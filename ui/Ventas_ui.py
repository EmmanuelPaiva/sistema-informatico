import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Qt, QPropertyAnimation)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QWidget, QMainWindow
)
from forms.formularioVentas import Ui_Form as nuevaVentaUi
from db.conexion import conexion
from db.ventas_queries import (
    agrega_prodcuto_a_fila, agregar_filas, guardar_venta_en_db, cargar_ventas,
    actualizar_subtotal, actualizar_venta_en_db, buscar_ventas
)
from utils.utilsVentas import calcular_total_general, borrar_fila, toggle_subtabla


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(653, 475)

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")

        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 2, 0, 1, 1)

        self.pushButton_3 = QPushButton(Form)
        self.pushButton_3.setObjectName(u"pushButton_3")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.AddressBookNew))
        self.pushButton_3.setIcon(icon)
        self.gridLayout.addWidget(self.pushButton_3, 2, 2, 1, 1)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 3, 1, 1)

        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 2, 3, 1, 1)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        # TABLA (árbol con subfilas)
        self.treeWidget = QTreeWidget(Form)
        self.treeWidget.setObjectName(u"treeWidget")
        self.gridLayout.addWidget(self.treeWidget, 3, 0, 1, 4)

        Form.resize(400, 600)
        Form.setMinimumWidth(300)

        self.treeWidget.setColumnCount(8)
        self.treeWidget.setHeaderLabels(["ID", "Fecha", "Cliente", "Cantidad", "Total", "Medio", "Factura", "Opciones"])
        self.treeWidget.setColumnHidden(0, True)
        header = self.treeWidget.header()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # señales
        self.treeWidget.itemClicked.connect(lambda item, col: toggle_subtabla(item))
        self.lineEdit.textChanged.connect(lambda: buscar_ventas(self, self.lineEdit.text(), Form))

        # botón nueva venta
        self.pushButton.clicked.connect(lambda: self.abrir_formulario_nueva_venta(Form))

        # cargar ventas
        cargar_ventas(self, Form)

        # estilos
        Form.setStyleSheet("""
            QWidget { font-family: Segoe UI, sans-serif; font-size: 14px; background-color: #f9fbfd; }
            QLineEdit, QDateTimeEdit, QComboBox {
                padding: 8px; border: 1px solid #b0c4de; border-radius: 8px; background-color: #ffffff;
            }
            QLineEdit:focus, QDateTimeEdit:focus, QComboBox:focus { border: 1px solid #5dade2; background-color: #eef7ff; }
            QPushButton { padding: 10px 18px; background-color: #5dade2; color: white; font-weight: bold; border-radius: 10px; border: none; }
            QPushButton:hover { background-color: #3498db; }
            QPushButton:pressed { background-color: #2e86c1; }
            QLabel { font-weight: bold; color: #2c3e50; }
        """)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Ventas", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Buscar venta", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Filtrar", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Nueva venta", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"Exportar", None))
        self.label.setText(QCoreApplication.translate("Form", u"Ventas", None))

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
