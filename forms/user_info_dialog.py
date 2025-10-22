# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QFrame
)
from db.conexion import get_conn

# ==== Estilos/helpers del sistema (compat como en proveedores_willow) ====
try:
    from ui_helpers import apply_global_styles, mark_title, style_table
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles, mark_title, style_table


def fmt_dt(dt):
    try:
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt) if dt else "—"


def _get(row, key, idx=None):
    """
    Obtiene un valor de la fila soportando DictRow/dict o tuple.
    Si no hay key (o no es dict), usa idx (si se provee).
    """
    try:
        if hasattr(row, "keys") and key in row:
            return row[key]
    except Exception:
        pass
    if idx is not None:
        try:
            return row[idx]
        except Exception:
            return None
    return None


# cambios en encabezado de la clase
class UserDetailWindow(QWidget):
    def __init__(self, user_id: int, parent=None, embedded: bool = False):
        super().__init__(parent)
        self.setObjectName("UserDetailWindow")
        self.user_id = user_id
        self.setWindowTitle("Información de usuario")
        self._embedded = bool(embedded)

        root = QVBoxLayout(self)
        # si está embebido en el QDialog transparente, sin márgenes extra
        if self._embedded:
            root.setContentsMargins(0, 0, 0, 0)
        else:
            root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        # ---------- HEADER CARD (datos generales) ----------
        self.headerCard = QFrame(self)
        self.headerCard.setObjectName("headerCard")
        headerLayout = QVBoxLayout(self.headerCard)
        headerLayout.setContentsMargins(16, 12, 16, 12)
        headerLayout.setSpacing(10)

        # Título
        self.lblTitle = QLabel("Información de usuario", self.headerCard)
        self.lblTitle.setProperty("role", "pageTitle")
        mark_title(self.lblTitle)
        headerLayout.addWidget(self.lblTitle)

        # Grid de datos
        header = QGridLayout()
        header.setVerticalSpacing(6)

        self.lblNombre = QLabel("—")
        self.lblUsuario = QLabel("—")
        self.lblTelefono = QLabel("—")
        self.lblEstado = QLabel("—")
        self.lblCreado = QLabel("—")
        self.lblActualizado = QLabel("—")
        self.lblUltimoLogin = QLabel("—")
        self.lblLogins = QLabel("—")

        header.addWidget(QLabel("<b>Nombre completo:</b>", self.headerCard), 0, 0)
        header.addWidget(self.lblNombre, 0, 1)
        header.addWidget(QLabel("<b>Usuario:</b>", self.headerCard), 1, 0)
        header.addWidget(self.lblUsuario, 1, 1)
        header.addWidget(QLabel("<b>Teléfono:</b>", self.headerCard), 2, 0)
        header.addWidget(self.lblTelefono, 2, 1)
        header.addWidget(QLabel("<b>Estado:</b>", self.headerCard), 3, 0)
        header.addWidget(self.lblEstado, 3, 1)

        header.addWidget(QLabel("<b>Creado:</b>", self.headerCard), 0, 2)
        header.addWidget(self.lblCreado, 0, 3)
        header.addWidget(QLabel("<b>Actualizado:</b>", self.headerCard), 1, 2)
        header.addWidget(self.lblActualizado, 1, 3)
        header.addWidget(QLabel("<b>Último login:</b>", self.headerCard), 2, 2)
        header.addWidget(self.lblUltimoLogin, 2, 3)
        header.addWidget(QLabel("<b>Logins totales:</b>", self.headerCard), 3, 2)
        header.addWidget(self.lblLogins, 3, 3)

        headerLayout.addLayout(header)
        root.addWidget(self.headerCard)

        # ---------- TABLE CARD (historial de inicios de sesión) ----------
        self.tableCard = QFrame(self)
        self.tableCard.setObjectName("tableCard")
        tableWrap = QVBoxLayout(self.tableCard)
        tableWrap.setContentsMargins(0, 0, 0, 0)
        tableWrap.setSpacing(0)

        self.table = QTableWidget(self.tableCard)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Fecha y hora"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header_view = self.table.horizontalHeader()
        header_view.setStretchLastSection(True)
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)

        style_table(self.table)  # igual que en proveedores
        tableWrap.addWidget(self.table)
        root.addWidget(self.tableCard, 1)

        # ---------- Estilos globales ----------
        apply_global_styles(self)

        # Estilo local del detalle
        self.setStyleSheet("""
            #UserDetailWindow #headerCard {
                background: palette(window);
                border-bottom: 1px solid rgba(0,0,0,0.06);
            }
            #UserDetailWindow QLabel[role="pageTitle"] {
                font-size: 18px; font-weight: 800; padding: 8px 4px;
            }
            #UserDetailWindow #tableCard {
                background: palette(base);
                border: none;
            }
        """)

        if self._embedded:
            from PySide6.QtWidgets import QSizePolicy
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            
        # ---------- Cargar datos ----------
        self._load_user()
        self._load_sessions()

    # ---------- Data loaders ----------
    def _load_user(self):
        try:
            conn = get_conn(); cur = conn.cursor()
            # Alias explícitos para soportar DictCursor y tuplas
            cur.execute("""
                SELECT
                    id            AS id,
                    username      AS username,
                    full_name     AS full_name,
                    phone         AS phone,
                    is_active     AS is_active,
                    created_at    AS created_at,
                    updated_at    AS updated_at,
                    last_login_at AS last_login_at,
                    login_count   AS login_count
                FROM rodler_auth.users
                WHERE id = %s
            """, (self.user_id,))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Usuarios", f"No se pudo cargar el usuario.\n\n{e}")
            return

        if not row:
            return

        username      = _get(row, "username", 1)
        full_name     = _get(row, "full_name", 2)
        phone         = _get(row, "phone", 3)
        is_active     = _get(row, "is_active", 4)
        created_at    = _get(row, "created_at", 5)
        updated_at    = _get(row, "updated_at", 6)
        last_login_at = _get(row, "last_login_at", 7)
        login_count   = _get(row, "login_count", 8)

        self.lblUsuario.setText(username or "—")
        self.lblNombre.setText((full_name or username) or "—")
        self.lblTelefono.setText(phone or "—")
        self.lblEstado.setText("Activo" if bool(is_active) else "Inactivo")
        self.lblCreado.setText(fmt_dt(created_at))
        self.lblActualizado.setText(fmt_dt(updated_at))
        self.lblUltimoLogin.setText(fmt_dt(last_login_at))
        self.lblLogins.setText(str(login_count or 0))

    def _load_sessions(self):
        """Carga SOLO las fechas de inicio de sesión (sin tokens)."""
        try:
            conn = get_conn(); cur = conn.cursor()
            cur.execute("""
                SELECT created_at AS login_at
                FROM rodler_auth.sessions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 300
            """, (self.user_id,))
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Usuarios", f"No se pudo cargar el historial de sesiones.\n\n{e}")
            return

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            # Soporta dict o tupla
            login_at = _get(r, "login_at", 0)
            self.table.setItem(i, 0, QTableWidgetItem(fmt_dt(login_at)))
