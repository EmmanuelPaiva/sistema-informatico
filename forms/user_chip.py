# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)

# ====== Avatar generator ======
def avatar_pixmap(text: str, size: int = 40) -> QPixmap:
    """
    Genera un QPixmap circular con la inicial del texto dado.
    El color se estiliza vía QSS global; este azul es un fallback.
    """
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#2979FF"))  # color base (tema light fallback)
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)

    painter.setPen(Qt.white)
    font = QFont("Segoe UI", int(size * 0.48), QFont.Bold)
    painter.setFont(font)
    initial = (text or "?").strip()[:1].upper() or "?"
    painter.drawText(pm.rect(), Qt.AlignCenter, initial)
    painter.end()

    return pm


# ====== Mini Card Component ======
class UserCard(QFrame):
    """
    Tarjeta compacta para mostrar usuario: avatar + nombre + botón.
    Se integra con QSS global (usa propiedad [chip="true"]).
    """
    clicked_view = Signal(int)  # Emite el id del usuario al presionar "Ver información"

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user or {}
        self.setProperty("chip", True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # --- Avatar circular ---
        avatar = QLabel()
        avatar_text = user.get("full_name") or user.get("username") or "?"
        avatar.setPixmap(avatar_pixmap(avatar_text))
        avatar.setFixedSize(40, 40)
        avatar.setObjectName("avatarLbl")

        # --- Nombre ---
        name = QLabel(user.get("full_name") or user.get("username") or "—")
        name.setObjectName("nameLbl")

        # --- Botón acción ---
        btn = QPushButton("Ver información")
        btn.setObjectName("viewBtn")
        user_id = user.get("id")
        btn.clicked.connect(lambda: self._emit_user_id(user_id))

        # --- Layout interno ---
        text_box = QVBoxLayout()
        text_box.setSpacing(0)
        text_box.addWidget(name)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        layout.addWidget(avatar)
        layout.addLayout(text_box, 1)
        layout.addWidget(btn, 0, Qt.AlignRight)

    # --- Función auxiliar segura ---
    def _emit_user_id(self, user_id):
        """Emite la señal sólo si el id es válido."""
        if user_id is not None:
            self.clicked_view.emit(user_id)
