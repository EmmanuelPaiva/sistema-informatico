# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QFrame, QSizePolicy, QPushButton, QStackedLayout, QDialog
)

from db.conexion import get_conn
from forms.user_chip import UserCard
from forms.user_info_dialog import UserDetailWindow

# ==== Estilos/helpers del sistema (igual que proveedores_willow) ====
try:
    from ui_helpers import apply_global_styles
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles


FORM_WIDTH = 480  # mismo ancho que el formulario de "nuevo usuario"


class UsersListWindow(QWidget):
    """
    Lista de usuarios + detalle embebido en el mismo widget (sin abrir otro QDialog).
    - Ancho fijo (FORM_WIDTH) para calzar perfecto en el QDialog padre.
    - Botón de cierre (✕) arriba a la derecha del widget (no del contenedor).
    - Al pulsar "Ver información" se cambia a la vista detalle en el mismo stacked.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UsersListWindow")
        self.setWindowTitle("Usuarios")

        # ---- ancho/size policy: clave para que el diálogo se adapte ----
        self.setMinimumWidth(FORM_WIDTH)
        self.setMaximumWidth(FORM_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Layout raíz (sin márgenes extra)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Header con título + ✕ (cierra el QDialog contenedor)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)

        title = QLabel("Usuarios", self)
        title.setProperty("role", "pageTitle")

        btn_close = QPushButton("✕", self)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedWidth(30)
        btn_close.setObjectName("usersCloseBtn")
        btn_close.clicked.connect(self._close_dialog_container)

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(btn_close)
        root.addLayout(header)

        # Card contenedora con un QStackedLayout para LISTA / DETALLE
        self.card = QFrame(self)
        self.card.setObjectName("tableCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(8)

        self.stack = QStackedLayout()
        self.stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # Página LISTA
        self.page_list = QFrame(self.card)
        list_layout = QVBoxLayout(self.page_list)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(10)

        self.list_container = QFrame(self.page_list)
        self.list_container.setObjectName("usersContainer")
        self.vlist = QVBoxLayout(self.list_container)
        self.vlist.setContentsMargins(0, 0, 0, 0)
        self.vlist.setSpacing(10)

        list_layout.addWidget(self.list_container)
        self.stack.addWidget(self.page_list)

        # Página DETALLE (se crea al vuelo)
        self.page_detail = None
        self.detail_widget = None

        card_layout.addLayout(self.stack)
        root.addWidget(self.card, 0, Qt.AlignTop)

        # Estado interno
        self._users = []

        # Estilos globales
        apply_global_styles(self)

        # Datos iniciales
        self._load_users()
        self._rebuild_list()

    # ---------- helpers ----------
    def _close_dialog_container(self):
        """Cierra el QDialog padre (contenedor transparente)."""
        p = self.parent()
        while p and not isinstance(p, QDialog):
            p = p.parent()
        if p:
            p.close()

    # ---------- Data ----------
    def _load_users(self):
        """Carga usuarios desde rodler_auth.users. Soporta cursor tipo tupla o dict."""
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    id        AS id,
                    username  AS username,
                    full_name AS full_name
                FROM rodler_auth.users
                ORDER BY COALESCE(NULLIF(full_name,''), username), username
            """)
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            self._users = []
            self._clear_list()
            self.vlist.addWidget(QLabel(f"Error al cargar usuarios:\n{e}"))
            return

        def _get(r, key, idx):
            try:
                if hasattr(r, "keys"):
                    return r.get(key)
            except Exception:
                pass
            try:
                return r[idx]
            except Exception:
                return None

        users = []
        for r in rows:
            uid = _get(r, "id", 0)
            uname = _get(r, "username", 1)
            fname = _get(r, "full_name", 2)
            display = fname if (fname and str(fname).strip()) else uname
            users.append({"id": uid, "username": uname, "full_name": display})
        self._users = users

    # ---------- UI ----------
    def _clear_list(self):
        for i in reversed(range(self.vlist.count())):
            item = self.vlist.itemAt(i)
            w = item.widget()
            if w:
                w.setParent(None)

    def _rebuild_list(self):
        """Reconstruye la lista vertical de mini-cards (una sola columna)."""
        self._clear_list()
        for u in self._users:
            card = UserCard(u)  # espera keys: id, username, full_name
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.clicked_view.connect(self._open_detail_embedded)
            self.vlist.addWidget(card)
        self.vlist.addStretch(1)
        self.stack.setCurrentWidget(self.page_list)

    def _open_detail_embedded(self, user_id: int):
        """
        Crea el widget de detalle y lo muestra en la segunda página del stack,
        con el MISMO ancho que la lista (FORM_WIDTH). No abre otro QDialog.
        """
        try:
            if self.page_detail is None:
                self.page_detail = QFrame(self.card)
                pd_layout = QVBoxLayout(self.page_detail)
                pd_layout.setContentsMargins(0, 0, 0, 0)
                pd_layout.setSpacing(10)

                # Header del detalle con botón "Volver" y "✕" (cierra diálogo)
                header = QHBoxLayout()
                header.setContentsMargins(0, 0, 0, 0)
                header.setSpacing(6)

                lbl = QLabel("Información de usuario", self.page_detail)
                lbl.setProperty("role", "pageTitle")

                btn_back = QPushButton("← Volver", self.page_detail)
                btn_back.setCursor(Qt.PointingHandCursor)
                btn_back.clicked.connect(self._back_to_list)

                btn_close = QPushButton("✕", self.page_detail)
                btn_close.setCursor(Qt.PointingHandCursor)
                btn_close.setFixedWidth(30)
                btn_close.clicked.connect(self._close_dialog_container)

                header.addWidget(lbl)
                header.addStretch(1)
                header.addWidget(btn_back)
                header.addWidget(btn_close)
                pd_layout.addLayout(header)

                # Lugar donde insertamos el UserDetailWindow (como QWidget)
                self.detail_holder = QFrame(self.page_detail)
                dh_layout = QVBoxLayout(self.detail_holder)
                dh_layout.setContentsMargins(0, 0, 0, 0)
                dh_layout.setSpacing(0)
                pd_layout.addWidget(self.detail_holder)

                self.stack.addWidget(self.page_detail)

            # Limpiar detalle anterior
            if self.detail_widget:
                self.detail_widget.setParent(None)
                self.detail_widget.deleteLater()
                self.detail_widget = None

            # Crear detalle embebido (ajustado al ancho)
            self.detail_widget = UserDetailWindow(user_id, parent=self.detail_holder, embedded=True)
            self.detail_widget.setMinimumWidth(FORM_WIDTH)
            self.detail_widget.setMaximumWidth(FORM_WIDTH)
            self.detail_holder.layout().addWidget(self.detail_widget)

            self.stack.setCurrentWidget(self.page_detail)
            # (El QDialog se ajusta solo vía sizeHint del contenido; no tocamos nada más)

        except Exception as e:
            QMessageBox.critical(self, "Usuarios", f"No se pudo abrir el detalle del usuario.\n\n{e}")

    def _back_to_list(self):
        self.stack.setCurrentWidget(self.page_list)

    # ---- sizeHint coherente con el ancho fijo ----
    def sizeHint(self):
        sh = super().sizeHint()
        return QSize(FORM_WIDTH, sh.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UsersListWindow()
    w.show()
    sys.exit(app.exec())

