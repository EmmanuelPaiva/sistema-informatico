# -*- coding: utf-8 -*-

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt, QSize)
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QWidget, QVBoxLayout, QFrame, QHBoxLayout
)

# ===== QSS Willow (mismo look&feel que el resto) =====
QSS_WILLOW = """
* { font-family:"Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background:transparent; }

/* Card contenedor */
#card {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Etiquetas */
QLabel[role="fieldLabel"] {
  font-weight:600; color:#0F172A; margin-bottom:4px;
}

/* Inputs estilo pill compactos */
QLineEdit {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:10px;
  padding:6px 10px;
  min-height:28px;
  selection-background-color: rgba(41,121,255,.25);
}
QLineEdit:focus {
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
QPushButton[type="secondary"]:hover { border-color:#cfe0f5; }
"""

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(700, 240)
        Form.setMinimumSize(QSize(560, 0))

        # ===== Root =====
        self.root = QVBoxLayout(Form)
        self.root.setContentsMargins(12, 12, 12, 12)
        self.root.setSpacing(10)

        # ===== Card =====
        self.card = QFrame(Form)
        self.card.setObjectName("card")
        cardLay = QVBoxLayout(self.card)
        cardLay.setContentsMargins(16, 16, 16, 16)
        cardLay.setSpacing(14)

        # ===== Grid (2 columnas) =====
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        # Nombre
        self.labelNombre = QLabel("Nombre")
        self.labelNombre.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelNombre, 0, 0)
        self.lineEditNombre = QLineEdit()
        self.lineEditNombre.setObjectName("lineEditNombre")
        self.lineEditNombre.setPlaceholderText("Ingresar nombre del proveedor")
        grid.addWidget(self.lineEditNombre, 1, 0)

        # Dirección
        self.labelDireccion = QLabel("Dirección")
        self.labelDireccion.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelDireccion, 0, 1)
        self.lineEditDireccion = QLineEdit()
        self.lineEditDireccion.setObjectName("lineEditDireccion")
        self.lineEditDireccion.setPlaceholderText("Ej.: Av. Principal 123, Asunción")
        grid.addWidget(self.lineEditDireccion, 1, 1)

        # Teléfono
        self.labelTelefono = QLabel("Teléfono")
        self.labelTelefono.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelTelefono, 2, 0)
        self.lineEditTelefono = QLineEdit()
        self.lineEditTelefono.setObjectName("lineEditTelefono")
        self.lineEditTelefono.setPlaceholderText("Ej.: +595 981 000 000")
        grid.addWidget(self.lineEditTelefono, 3, 0)

        # Correo
        self.labelCorreo = QLabel("Correo")
        self.labelCorreo.setProperty("role", "fieldLabel")
        grid.addWidget(self.labelCorreo, 2, 1)
        self.lineEditCorreo = QLineEdit()
        self.lineEditCorreo.setObjectName("lineEditCorreo")
        self.lineEditCorreo.setPlaceholderText("proveedor@correo.com")
        grid.addWidget(self.lineEditCorreo, 3, 1)

        cardLay.addLayout(grid)

        # ===== Botonera =====
        btnBar = QHBoxLayout()
        btnBar.addStretch(1)

        self.pushButtonCancelar = QPushButton("Cancelar")
        self.pushButtonCancelar.setObjectName("pushButtonCancelar")
        self.pushButtonCancelar.setProperty("type", "secondary")
        btnBar.addWidget(self.pushButtonCancelar)

        self.pushButton = QPushButton("Guardar")
        self.pushButton.setObjectName("btnAceptarProveedor")               # objectName para permisos
        self.pushButton.setProperty("perm_code", "proveedores.create")     # permiso requerido
        self.pushButton.setProperty("type", "primary")                     # estilo QSS
        btnBar.addWidget(self.pushButton)

        cardLay.addLayout(btnBar)
        self.root.addWidget(self.card)

        # Estilos Willow
        Form.setStyleSheet(QSS_WILLOW)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Nuevo proveedor", None))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
