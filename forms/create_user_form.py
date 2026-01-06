# -*- coding: utf-8 -*-
"""
Archivo: user_create_form.py

Formulario centrado para crear usuarios:
- username
- password
- confirm_password
- role
- full_name
- phone

Soporta cambio automático de tema (claro / oscuro)
usando el estado global de la aplicación.
"""

from PySide6.QtCore import Qt, Signal, QRegularExpression, QSize
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QFrame, QSizePolicy, QMessageBox, QSpacerItem
)

from themes import themed_icon, is_dark_mode

FORM_WIDTH = 480


class CreateUserForm(QWidget):
    submitted = Signal(dict)
    cancelled = Signal()

    def __init__(self, parent=None, roles=("admin", "empleado")):
        super().__init__(parent)

        self.setMinimumWidth(FORM_WIDTH)
        self.setMaximumWidth(FORM_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.setObjectName("CreateUserForm")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        root.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.card = QFrame(self)
        self.card.setObjectName("card")
        self.card.setProperty("card", True)
        self.card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 24, 24, 16)
        card_layout.setSpacing(16)

        title = QLabel("Crear nuevo usuario", self.card)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignHCenter)
        card_layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.txt_username = QLineEdit(self.card)
        self.txt_username.setPlaceholderText("Ej.: empleado1")
        self.txt_username.setMaxLength(64)

        self.txt_full_name = QLineEdit(self.card)
        self.txt_full_name.setPlaceholderText("Nombre y apellido")

        self.txt_phone = QLineEdit(self.card)
        self.txt_phone.setPlaceholderText("Ej.: +595971000000")
        phone_re = QRegularExpression(r"^[\+\d][\d\s\-]{5,20}$")
        self.txt_phone.setValidator(QRegularExpressionValidator(phone_re))

        self.cbo_role = QComboBox(self.card)
        self.cbo_role.addItems(list(roles))

        self.txt_password = QLineEdit(self.card)
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Contraseña")

        self.txt_confirm = QLineEdit(self.card)
        self.txt_confirm.setEchoMode(QLineEdit.Password)
        self.txt_confirm.setPlaceholderText("Confirmar contraseña")

        # ---- Botón mostrar / ocultar contraseña ----
        self.btn_toggle_pw = QPushButton(self.card)
        self.btn_toggle_pw.setCheckable(True)
        self.btn_toggle_pw.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pw.setObjectName("btn_toggle_pw")
        self.btn_toggle_pw.setToolTip("Mostrar / ocultar contraseñas")
        self.btn_toggle_pw.toggled.connect(self._toggle_password)
        self._update_pw_icon()

        pw_row = QHBoxLayout()
        pw_row.addWidget(self.txt_password)
        pw_row.addWidget(self.btn_toggle_pw)

        form.addRow("Usuario", self.txt_username)
        form.addRow("Nombre completo", self.txt_full_name)
        form.addRow("Teléfono", self.txt_phone)
        form.addRow("Rol", self.cbo_role)
        form.addRow("Contraseña", pw_row)
        form.addRow("Confirmar", self.txt_confirm)

        card_layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch(1)

        self.btn_cancel = QPushButton("Cancelar", self.card)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setProperty("type", "secondary")
        self.btn_cancel.clicked.connect(self._on_cancel)

        self.btn_save = QPushButton("Guardar", self.card)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setProperty("type", "primary")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_submit)

        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_save)

        card_layout.addLayout(btns)

        root.addWidget(self.card, 0, Qt.AlignHCenter)
        root.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # ---------- Tema / Iconos ----------

    def _update_pw_icon(self):
        dark = is_dark_mode()
        icon = "eye-off" if self.btn_toggle_pw.isChecked() else "eye"
        self.btn_toggle_pw.setIcon(themed_icon(icon, dark))

    def _toggle_password(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.txt_password.setEchoMode(mode)
        self.txt_confirm.setEchoMode(mode)
        self._update_pw_icon()

    # ---------- Acciones ----------

    def _on_submit(self):
        username = self.txt_username.text().strip()
        full_name = self.txt_full_name.text().strip()
        phone = self.txt_phone.text().strip()
        role = self.cbo_role.currentText().strip()
        pw = self.txt_password.text()
        pw2 = self.txt_confirm.text()

        if not username:
            return self._warn("El campo Usuario es obligatorio.", self.txt_username)
        if not full_name:
            return self._warn("El campo Nombre completo es obligatorio.", self.txt_full_name)
        if not role:
            return self._warn("Debes seleccionar un rol.", self.cbo_role)
        if not pw:
            return self._warn("La contraseña es obligatoria.", self.txt_password)
        if pw != pw2:
            return self._warn("Las contraseñas no coinciden.", self.txt_confirm, clear=True)

        self.submitted.emit({
            "username": username,
            "password": pw,
            "role": role,
            "full_name": full_name,
            "phone": phone or None,
        })

    def _warn(self, msg, widget, clear=False):
        if clear and isinstance(widget, QLineEdit):
            widget.clear()
        QMessageBox.warning(self, "Validación", msg)
        widget.setFocus()

    def _on_cancel(self):
        self.cancelled.emit()
        self._close_dialog_container()

    def _close_dialog_container(self):
        from PySide6.QtWidgets import QDialog
        p = self.parent()
        while p and not isinstance(p, QDialog):
            p = p.parent()
        if p:
            p.close()

    def sizeHint(self):
        sh = super().sizeHint()
        return QSize(FORM_WIDTH, sh.height())
