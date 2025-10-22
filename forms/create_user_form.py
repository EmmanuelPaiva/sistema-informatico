# -*- coding: utf-8 -*-
"""
Archivo: user_create_form.py
Un formulario centrado para crear usuarios:
- username
- password
- confirm_password
- role
- full_name
- phone
Botones: Guardar / Cancelar
Se expone la señal 'submitted' con un dict de los datos si la validación pasa.
"""

from PySide6.QtCore import Qt, Signal, QRegularExpression, QSize
from PySide6.QtGui import QIcon, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QFrame, QSizePolicy, QMessageBox, QCheckBox, QSpacerItem
)

FORM_WIDTH = 480  # ancho fijo para que el QDialog se adapte exactamente


class CreateUserForm(QWidget):
    # Emite los datos validados como dict: {username, password, role, full_name, phone}
    submitted = Signal(dict)
    cancelled = Signal()

    def __init__(self, parent=None, roles=("admin", "empleado")):
        super().__init__(parent)

        # ---- CLAVE: fijar ancho y políticas para que el contenedor (QDialog) no sobrepase ----
        self.setMinimumWidth(FORM_WIDTH)
        self.setMaximumWidth(FORM_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # ---------- CONTENEDOR CENTRAL (card) ----------
        self.setObjectName("CreateUserForm")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        # Espaciadores para “centrar” verticalmente en su contenedor
        root.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.card = QFrame(self)
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.StyledPanel)
        self.card.setProperty("card", True)
        # Preferido para no forzar a crecer más del contenido
        self.card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 24, 24, 16)
        card_layout.setSpacing(16)

        # ---------- TÍTULO ----------
        title = QLabel("Crear nuevo usuario", self.card)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignHCenter)
        card_layout.addWidget(title)

        # ---------- FORM ----------
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        # Campos
        self.txt_username = QLineEdit(self.card)
        self.txt_username.setObjectName("username")
        self.txt_username.setPlaceholderText("Ej.: empleado1")
        self.txt_username.setMaxLength(64)

        self.txt_full_name = QLineEdit(self.card)
        self.txt_full_name.setObjectName("full_name")
        self.txt_full_name.setPlaceholderText("Nombre y apellido")

        self.txt_phone = QLineEdit(self.card)
        self.txt_phone.setObjectName("phone")
        self.txt_phone.setPlaceholderText("Ej.: +595971000000")
        # Validador simple (num, +, espacios, guiones)
        phone_re = QRegularExpression(r"^[\+\d][\d\s\-]{5,20}$")
        self.txt_phone.setValidator(QRegularExpressionValidator(phone_re, self.txt_phone))

        self.cbo_role = QComboBox(self.card)
        self.cbo_role.setObjectName("role")
        self.cbo_role.addItems(list(roles))

        self.txt_password = QLineEdit(self.card)
        self.txt_password.setObjectName("password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Contraseña")

        self.txt_confirm = QLineEdit(self.card)
        self.txt_confirm.setObjectName("confirm_password")
        self.txt_confirm.setEchoMode(QLineEdit.Password)
        self.txt_confirm.setPlaceholderText("Confirmar contraseña")

        # Mostrar/ocultar contraseña
        show_pw = QCheckBox("Mostrar contraseñas", self.card)
        show_pw.stateChanged.connect(self._toggle_password_echo)

        # Agregar al formulario
        form.addRow("Usuario*", self.txt_username)
        form.addRow("Nombre completo*", self.txt_full_name)
        form.addRow("Teléfono", self.txt_phone)
        form.addRow("Rol*", self.cbo_role)
        form.addRow("Contraseña*", self.txt_password)
        form.addRow("Confirmar*", self.txt_confirm)
        form.addRow("", show_pw)

        card_layout.addLayout(form)

        # ---------- BOTONES ----------
        btns = QHBoxLayout()
        btns.addStretch(1)

        self.btn_cancel = QPushButton("Cancelar", self.card)
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setProperty("type", "secondary")
        self.btn_cancel.style().unpolish(self.btn_cancel); self.btn_cancel.style().polish(self.btn_cancel)
        self.btn_cancel.clicked.connect(self._on_cancel)

        self.btn_save = QPushButton("Guardar", self.card)
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setProperty("type", "primary")
        self.btn_save.style().unpolish(self.btn_save); self.btn_save.style().polish(self.btn_save)
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_submit)

        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_save)

        card_layout.addLayout(btns)

        root.addWidget(self.card, 0, Qt.AlignHCenter)
        # Espaciador inferior para centrar vertical
        root.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Atajos UX
        self.txt_username.returnPressed.connect(self.txt_full_name.setFocus)
        self.txt_full_name.returnPressed.connect(self.txt_phone.setFocus)
        self.txt_phone.returnPressed.connect(self.cbo_role.setFocus)
        self.txt_password.returnPressed.connect(self.txt_confirm.setFocus)
        self.txt_confirm.returnPressed.connect(self._on_submit)

    # dentro de CreateUserForm

    def _close_dialog_container(self):
        # Cierra el QDialog contenedor (transparente)
        from PySide6.QtWidgets import QDialog
        p = self.parent()
        while p and not isinstance(p, QDialog):
            p = p.parent()
        if p:
            p.close()

    def _on_cancel(self):
        self.cancelled.emit()
        self._close_dialog_container()


    # ---- sizeHint: reporta el ancho fijo para que el diálogo lo respete ----
    def sizeHint(self):
        sh = super().sizeHint()
        return QSize(FORM_WIDTH, sh.height())

    # ---------- Helpers ----------
    def _toggle_password_echo(self, state: int):
        mode = QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        self.txt_password.setEchoMode(mode)
        self.txt_confirm.setEchoMode(mode)

    def _on_cancel(self):
        self.cancelled.emit()

    def _on_submit(self):
        # Validaciones mínimas
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

        # Si pasó validación, emite datos
        payload = {
            "username": username,
            "password": pw,            # hashea en tu capa de servicio antes de guardar
            "role": role,
            "full_name": full_name,
            "phone": phone or None,
        }
        self.submitted.emit(payload)

    def _warn(self, msg: str, widget_to_focus: QWidget, clear: bool = False):
        if clear and isinstance(widget_to_focus, QLineEdit):
            widget_to_focus.clear()
        QMessageBox.warning(self, "Validación", msg)
        widget_to_focus.setFocus()

    # ---------- API pública ----------
    def set_roles(self, roles: list[str]):
        """Recarga las opciones del combo Rol."""
        self.cbo_role.clear()
        self.cbo_role.addItems(roles)

    def set_initial_values(self, data: dict):
        """Setea valores por defecto si vas a usarlo en modo edición."""
        self.txt_username.setText(data.get("username", ""))
        self.txt_full_name.setText(data.get("full_name", ""))
        self.txt_phone.setText(data.get("phone", ""))
        role = data.get("role", "")
        if role:
            idx = self.cbo_role.findText(role)
            if idx >= 0:
                self.cbo_role.setCurrentIndex(idx)
        # Por seguridad no seteamos contraseñas aquí


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    form = CreateUserForm(roles=["admin", "empleado", "gerente"])
    form.submitted.connect(print)
    form.cancelled.connect(app.quit)
    form.show()
    sys.exit(app.exec())
