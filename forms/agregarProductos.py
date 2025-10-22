# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QWidget,
    QVBoxLayout, QFrame, QHBoxLayout
)

QSS_RODLER = """
* { font-family:"Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background:transparent; }

/* Card contenedor */
#card {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Etiquetas pequeñas y prolijas */
QLabel[role="fieldLabel"] {
  font-weight:600; color:#0F172A; margin-bottom:4px;
}

/* Inputs estilo pill compactos */
QLineEdit, QComboBox {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:10px;
  padding:6px 10px;
  min-height:28px;
  selection-background-color: rgba(41,121,255,.25);
}
QLineEdit:focus, QComboBox:focus {
  border:1px solid #90CAF9;
  background:#FFFFFF;
}

/* Botón primario compacto */
QPushButton[type="primary"] {
  background:#2979FF;
  border:1px solid #2979FF;
  color:#FFFFFF;
  border-radius:10px;
  padding:6px 14px;
  min-height:28px;
  font-weight:600;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

/* Botón secundario (ghost) */
QPushButton[type="secondary"] {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  color:#0F172A;
  border-radius:10px;
  padding:6px 14px;
  min-height:28px;
}
QPushButton[type="secondary"]:hover {
  border-color:#cfe0f5;
}

/* Mini ayuda debajo del input */
QLabel[role="hint"] {
  color:#64748B; font-size:12px;
}
"""

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(680, 300)

        # Layout raíz
        self.root = QVBoxLayout(Form)
        self.root.setContentsMargins(12, 12, 12, 12)
        self.root.setSpacing(10)

        # Card contenedor
        self.card = QFrame(Form)
        self.card.setObjectName("card")
        cardLay = QVBoxLayout(self.card)
        cardLay.setContentsMargins(16, 16, 16, 16)
        cardLay.setSpacing(14)

        # Grid de campos (2 columnas visuales)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        # --- Precio ---
        self.labelPrecio = QLabel("Precio")
        self.labelPrecio.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelPrecio, 0, 0)
        self.lineEditPrecio = QLineEdit()
        self.lineEditPrecio.setPlaceholderText("0,00")
        grid.addWidget(self.lineEditPrecio, 1, 0)

        # --- Nombre ---
        self.labelNombre = QLabel("Nombre")
        self.labelNombre.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelNombre, 0, 1)
        self.lineEditNombre = QLineEdit()
        self.lineEditNombre.setPlaceholderText("Ej.: Ladrillo cerámico 6x18x33")
        grid.addWidget(self.lineEditNombre, 1, 1)

        # --- Descripción (ancha, ocupa 2 cols) ---
        self.labelDescripcion = QLabel("Descripción")
        self.labelDescripcion.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelDescripcion, 2, 0, 1, 2)
        self.lineEditDescripcion = QLineEdit()
        self.lineEditDescripcion.setPlaceholderText("Opcional")
        grid.addWidget(self.lineEditDescripcion, 3, 0, 1, 2)

        # --- Stock (solo lectura) + hint ---
        self.labelStock = QLabel("Stock")
        self.labelStock.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelStock, 4, 0)
        self.lineEditStock = QLineEdit()
        self.lineEditStock.setReadOnly(True)
        self.lineEditStock.setPlaceholderText("0")
        grid.addWidget(self.lineEditStock, 5, 0)
        self.hintStock = QLabel("El stock se ajusta desde Compras/Ventas/Obras/Ajustes.")
        self.hintStock.setProperty("role", "hint")
        grid.addWidget(self.hintStock, 6, 0)

        # --- Proveedor ---
        self.labelProveedor = QLabel("Proveedor")
        self.labelProveedor.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelProveedor, 4, 1)
        self.comboBoxProveedore = QComboBox()
        self.comboBoxProveedore.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(self.comboBoxProveedore, 5, 1)

        cardLay.addLayout(grid)

        # Barra de botones
        btnBar = QHBoxLayout()
        btnBar.addStretch(1)

        self.pushButton_2 = QPushButton("Cancelar")
        self.pushButton_2.setProperty("type", "secondary")
        btnBar.addWidget(self.pushButton_2)

        self.pushButton = QPushButton("Guardar")
        self.pushButton.setObjectName("btnGuardarProducto")           # PATCH permisos
        self.pushButton.setProperty("perm_code", "productos.create")
        self.pushButton.setProperty("type", "primary")
        btnBar.addWidget(self.pushButton)

        cardLay.addLayout(btnBar)

        self.root.addWidget(self.card)

        # Styles are applied globally via main/themes

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Nuevo producto", None))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
