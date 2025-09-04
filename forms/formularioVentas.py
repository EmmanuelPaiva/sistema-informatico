# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDateTimeEdit, QGridLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget, QWidget,
    QFrame, QHBoxLayout, QVBoxLayout
)

# ==== Estilos/helpers del sistema ====
from forms.ui_helpers import (
    apply_global_styles, make_primary, make_danger, style_table
)


class Ui_Form(object):
    def setupUi(self, Form: QWidget):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(420, 600)

        # ====== Layout raíz (SIN márgenes) ======
        self.root = QVBoxLayout(Form)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        # ====== Contenedor principal ======
        self.page = QWidget(Form)
        self.pageLayout = QVBoxLayout(self.page)
        self.pageLayout.setContentsMargins(12, 12, 12, 12)
        self.pageLayout.setSpacing(10)

        # ====== Grid superior: Fecha / Cliente ======
        topGrid = QGridLayout()
        topGrid.setContentsMargins(0, 0, 0, 0)
        topGrid.setHorizontalSpacing(10)
        topGrid.setVerticalSpacing(6)

        self.labelFecha = QLabel(self.page)
        self.labelFecha.setText("Fecha")
        topGrid.addWidget(self.labelFecha, 0, 0, 1, 1)

        self.dateTimeEditCliente = QDateTimeEdit(self.page)
        self.dateTimeEditCliente.setCalendarPopup(True)
        self.dateTimeEditCliente.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        topGrid.addWidget(self.dateTimeEditCliente, 0, 1, 1, 3)

        self.labelCliente = QLabel(self.page)
        self.labelCliente.setText("Cliente")
        topGrid.addWidget(self.labelCliente, 1, 0, 1, 1)

        self.comboBox = QComboBox(self.page)
        self.comboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        topGrid.addWidget(self.comboBox, 1, 1, 1, 3)

        # Mensaje de error de proveedor
        self.labelErrorProveedor = QLabel(self.page)
        self.labelErrorProveedor.setText("Este proveedor no tiene productos registrados.")
        self.labelErrorProveedor.setStyleSheet("color: #d32f2f; font-size: 12px;")
        self.labelErrorProveedor.setVisible(False)
        topGrid.addWidget(self.labelErrorProveedor, 2, 1, 1, 3)

        # Método de pago
        self.labelMedioPago = QLabel(self.page)
        self.labelMedioPago.setText("Método de pago")
        topGrid.addWidget(self.labelMedioPago, 3, 0, 1, 1)

        self.comboBoxMedioPago = QComboBox(self.page)
        self.comboBoxMedioPago.addItems(["Efectivo", "Transferencia"])
        self.comboBoxMedioPago.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        topGrid.addWidget(self.comboBoxMedioPago, 3, 1, 1, 3)

        self.pageLayout.addLayout(topGrid)

        # ====== Barra de controles del detalle ======
        detailBar = QHBoxLayout()
        detailBar.setContentsMargins(0, 0, 0, 0)
        detailBar.setSpacing(10)

        lblDetalle = QLabel("Detalle de productos")
        detailBar.addWidget(lblDetalle)
        detailBar.addStretch(1)

        self.pushButtonQuitarProducto = QPushButton("–")
        self.pushButtonQuitarProducto.setToolTip("Quitar fila seleccionada")
        self.pushButtonQuitarProducto.setMinimumSize(34, 34)
        self.pushButtonQuitarProducto.setMaximumWidth(40)
        make_danger(self.pushButtonQuitarProducto)
        detailBar.addWidget(self.pushButtonQuitarProducto)

        self.pushButtonAgregarProducto = QPushButton("+")
        self.pushButtonAgregarProducto.setToolTip("Agregar una fila")
        self.pushButtonAgregarProducto.setMinimumSize(34, 34)
        self.pushButtonAgregarProducto.setMaximumWidth(40)
        make_primary(self.pushButtonAgregarProducto)
        detailBar.addWidget(self.pushButtonAgregarProducto)

        self.pageLayout.addLayout(detailBar)

        # ====== Wrapper con borde redondeado para la tabla ======
        self.tableWrapper = QFrame(self.page)
        self.tableWrapper.setObjectName("tablaWrapper")
        self.tableWrapper.setStyleSheet("""
        #tablaWrapper {
            background: #ffffff;
            border: 1px solid #dfe7f5;
            border-radius: 12px;
        }
        QTableWidget {
            background: #ffffff;
            border: none;
        }
        QHeaderView {
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            background: transparent;
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
            border-right: none;
        }
        QTableWidget::item:selected {
            background: rgba(144,202,249,.25);
            color: #0d1b2a;
        }
        """)
        wrapperLay = QVBoxLayout(self.tableWrapper)
        wrapperLay.setContentsMargins(0, 0, 0, 0)
        wrapperLay.setSpacing(0)

        # ====== Tabla ======
        self.tableWidget = QTableWidget(self.tableWrapper)   # <<< nombre original
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unitario", "Subtotal"])
        self.tableWidget.setWordWrap(False)
        self.tableWidget.setAlternatingRowColors(False)
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(42)

        header = self.tableWidget.horizontalHeader()
        header.setHighlightSections(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)          # Producto
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Cantidad
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Precio U.
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Subtotal

        style_table(self.tableWidget)

        wrapperLay.addWidget(self.tableWidget)
        self.pageLayout.addWidget(self.tableWrapper, 1)

        # ====== Total ======
        totalBar = QHBoxLayout()
        totalBar.setContentsMargins(0, 0, 0, 0)
        totalBar.setSpacing(10)

        self.labelPrecioTotal = QLabel("Precio total")
        totalBar.addStretch(1)
        totalBar.addWidget(self.labelPrecioTotal)

        self.lineEditPrecioTotal = QLineEdit()
        self.lineEditPrecioTotal.setReadOnly(True)
        self.lineEditPrecioTotal.setPlaceholderText("0,00")
        self.lineEditPrecioTotal.setFixedWidth(160)
        totalBar.addWidget(self.lineEditPrecioTotal)

        self.pageLayout.addLayout(totalBar)

        # ====== Botones inferiores ======
        bottomBar = QHBoxLayout()
        bottomBar.setContentsMargins(0, 0, 0, 0)
        bottomBar.setSpacing(10)

        bottomBar.addStretch(1)

        self.pushButtonAceptar = QPushButton("Aceptar")
        make_primary(self.pushButtonAceptar)
        self.pushButtonAceptar.setMinimumHeight(34)
        bottomBar.addWidget(self.pushButtonAceptar)

        self.pushButtonCancelar = QPushButton("Cancelar")
        self.pushButtonCancelar.setMinimumHeight(34)
        bottomBar.addWidget(self.pushButtonCancelar)

        self.pageLayout.addLayout(bottomBar)

        self.root.addWidget(self.page)

        # ====== Estilos globales (paleta clara) ======
        apply_global_styles(Form)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Nueva venta", None))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
