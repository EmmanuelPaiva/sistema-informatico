# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDateTimeEdit, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget, QWidget,
    QFrame, QHBoxLayout, QVBoxLayout, QHeaderView
)

from forms.ui_helpers import (
    apply_global_styles, make_primary, make_danger, style_table
)

# ===== QSS WILLOW COMPACTO =====
QSS_WILLOW = """
* { font-family:"Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background:transparent; }

/* Cards */
#card, #tablaWrapper, QTableWidget {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Inputs más chicos */
QLineEdit, QComboBox, QDateTimeEdit {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:8px;
  padding:6px 10px;
  min-height:28px;
  font-size:12px;
}
QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
  border:1px solid #90CAF9;
  background:#FFFFFF;
}

/* Botones primarios/danger compactos */
QPushButton[type="primary"] {
  background:#2979FF;
  border:1px solid #2979FF;
  color:#FFFFFF;
  border-radius:8px;
  padding:6px 12px;
  min-height:28px;
  font-size:12px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

QPushButton[type="danger"] {
  background:#EF5350;
  border:1px solid #EF5350;
  color:#FFFFFF;
  border-radius:8px;
  padding:6px 12px;
  min-height:28px;
  font-size:12px;
}
QPushButton[type="danger"]:hover { background:#f26461; }

/* Botoncitos +/- */
QPushButton[role="iconSmall"] {
  min-width:28px; max-width:34px; min-height:28px;
  padding:0; font-size:16px; font-weight:700;
}

/* Tabla */
QHeaderView::section {
  background:#F8FAFF;
  color:#0F172A;
  padding:8px;
  border:none;
  border-right:1px solid #E8EEF6;
  font-size:12px;
}
QTableWidget {
  selection-background-color: rgba(41,121,255,.15);
  selection-color:#0F172A;
  border:none;
}
"""

class Ui_Form(object):
    def setupUi(self, Form: QWidget):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(520, 640)

        self.root = QVBoxLayout(Form)
        self.root.setContentsMargins(12, 12, 12, 12)
        self.root.setSpacing(10)

        self.page = QFrame(Form)
        self.page.setObjectName("card")
        self.pageLayout = QVBoxLayout(self.page)
        self.pageLayout.setContentsMargins(16, 16, 16, 16)
        self.pageLayout.setSpacing(12)

        # Grid superior
        topGrid = QGridLayout()
        topGrid.setHorizontalSpacing(8)
        topGrid.setVerticalSpacing(6)

        self.labelFecha = QLabel("Fecha")
        topGrid.addWidget(self.labelFecha, 0, 0)

        self.dateTimeEditCliente = QDateTimeEdit()
        self.dateTimeEditCliente.setCalendarPopup(True)
        self.dateTimeEditCliente.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        topGrid.addWidget(self.dateTimeEditCliente, 0, 1, 1, 3)

        self.labelCliente = QLabel("Cliente")
        topGrid.addWidget(self.labelCliente, 1, 0)

        self.comboBox = QComboBox()
        topGrid.addWidget(self.comboBox, 1, 1, 1, 3)

        self.labelErrorProveedor = QLabel("Este proveedor no tiene productos registrados.")
        self.labelErrorProveedor.setStyleSheet("color:#D32F2F; font-size:11px;")
        self.labelErrorProveedor.setVisible(False)
        topGrid.addWidget(self.labelErrorProveedor, 2, 1, 1, 3)

        self.labelMedioPago = QLabel("Método de pago")
        topGrid.addWidget(self.labelMedioPago, 3, 0)

        self.comboBoxMedioPago = QComboBox()
        self.comboBoxMedioPago.addItems(["Efectivo", "Transferencia"])
        topGrid.addWidget(self.comboBoxMedioPago, 3, 1, 1, 3)

        self.pageLayout.addLayout(topGrid)

        # Detail bar
        detailBar = QHBoxLayout()
        lblDetalle = QLabel("Detalle de productos")
        detailBar.addWidget(lblDetalle)
        detailBar.addStretch(1)

        self.pushButtonQuitarProducto = QPushButton("–")
        self.pushButtonQuitarProducto.setProperty("type", "danger")
        self.pushButtonQuitarProducto.setProperty("role", "iconSmall")
        make_danger(self.pushButtonQuitarProducto)
        detailBar.addWidget(self.pushButtonQuitarProducto)

        self.pushButtonAgregarProducto = QPushButton("+")
        self.pushButtonAgregarProducto.setProperty("type", "primary")
        self.pushButtonAgregarProducto.setProperty("role", "iconSmall")
        make_primary(self.pushButtonAgregarProducto)
        detailBar.addWidget(self.pushButtonAgregarProducto)

        self.pageLayout.addLayout(detailBar)

        # Tabla
        self.tableWrapper = QFrame(self.page)
        self.tableWrapper.setObjectName("tablaWrapper")
        wrapperLay = QVBoxLayout(self.tableWrapper)
        wrapperLay.setContentsMargins(0, 0, 0, 0)

        self.tableWidget = QTableWidget(self.tableWrapper)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unitario", "Subtotal"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(52)

        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        style_table(self.tableWidget)
        wrapperLay.addWidget(self.tableWidget)
        self.pageLayout.addWidget(self.tableWrapper, 1)

        # Total
        totalBar = QHBoxLayout()
        self.labelPrecioTotal = QLabel("Precio total")
        totalBar.addStretch(1)
        totalBar.addWidget(self.labelPrecioTotal)

        self.lineEditPrecioTotal = QLineEdit()
        self.lineEditPrecioTotal.setReadOnly(True)
        self.lineEditPrecioTotal.setPlaceholderText("0,00")
        self.lineEditPrecioTotal.setFixedWidth(120)
        totalBar.addWidget(self.lineEditPrecioTotal)

        self.pageLayout.addLayout(totalBar)

        # Botones inferiores más chicos
        bottomBar = QHBoxLayout()
        bottomBar.addStretch(1)

        self.pushButtonAceptar = QPushButton("Aceptar")
        self.pushButtonAceptar.setProperty("type", "primary")
        self.pushButtonAceptar.setProperty("perm_code", "ventas.create")
        self.pushButtonAceptar.setObjectName("btnAceptarVenta")          # PATCH permisos
        make_primary(self.pushButtonAceptar)
        self.pushButtonAceptar.setMinimumHeight(28)
        bottomBar.addWidget(self.pushButtonAceptar)

        self.pushButtonCancelar = QPushButton("Cancelar")
        self.pushButtonCancelar.setMinimumHeight(28)
        bottomBar.addWidget(self.pushButtonCancelar)

        self.pageLayout.addLayout(bottomBar)

        self.root.addWidget(self.page)

        apply_global_styles(Form)
        # Styles are applied globally via main/themes

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Nueva venta", None))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
