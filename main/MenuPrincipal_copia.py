# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import (
    Qt, QPropertyAnimation, Signal, QTimer, QSize, QPoint, QRect,
    QObject, QEvent, QThread, Slot
)
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QPen, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton,
    QStackedWidget, QButtonGroup, QSizePolicy, QSpacerItem,
    QCheckBox, QApplication, QMessageBox, QDialog
)
from PySide6.QtSvg import QSvgRenderer

# === Temas ===
from main.themes  import QSS_RODLER_LIGHT, QSS_RODLER_DARK

# === Módulos de tu app ===
from forms.productos_ui import Ui_Form as ProductosForm
from forms.compras_ui import Ui_Form as ComprasForm
from forms.Obras_ui import ObrasWidget
from forms.Ventas_ui import Ui_Form as VentasForm
from forms.Clientes_ui import Ui_Form as ClientesForm
from forms.Proveedores_ui import Ui_Form as ProveedoresForm
from forms.users_panel import UsersListWindow  # panel de info de usuarios

# === Gráficos ===
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from sqlalchemy import text
from graficos.graficos_dashboard import (
    get_engine,
    create_ventas_vs_compras_mensuales,
    create_gastos_mensuales,
    create_presupuesto_vs_gasto_por_obra,
    create_distribucion_gastos_por_tipo,
)

from graficos import graficos_style as gs

# === Clima ===
from forms.weather_panel import DashboardWeatherPanel


# =========================
#   OPTIMIZACIONES CLAVE
# =========================
_ENGINE_SINGLETON = None
def _get_engine_cached():
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        _ENGINE_SINGLETON = get_engine()
    return _ENGINE_SINGLETON

_SQL_MONTH_BOUNDS = text("""
    SELECT date_trunc('month', CURRENT_DATE)::date AS ini,
           (date_trunc('month', CURRENT_DATE) + interval '1 month')::date AS fin
""")

_SQL_KPI_VENTAS = text("""
    SELECT COALESCE(SUM(total_venta),0)
    FROM ventas
    WHERE fecha_venta >= :ini AND fecha_venta < :fin
""")

_SQL_KPI_COMPRAS = text("""
    SELECT COALESCE(SUM(total_compra),0)
    FROM compras
    WHERE fecha >= :ini AND fecha < :fin
""")

_SQL_KPI_TOP_PROD = text("""
    SELECT p.nombre, COALESCE(SUM(vd.cantidad),0) AS u
    FROM ventas_detalle vd
    JOIN ventas v   ON v.id_venta = vd.id_venta
    JOIN productos p ON p.id_producto = vd.id_producto
    WHERE v.fecha_venta >= :ini AND v.fecha_venta < :fin
    GROUP BY p.nombre
    ORDER BY u DESC
    LIMIT 1
""")

_SQL_KPI_CRITICOS = text("""
    SELECT COUNT(*) FROM productos WHERE COALESCE(stock_actual,0) <= COALESCE(stock_minimo,0)
""")


# ---------------- Iconos ----------------
_THIS_DIR = os.path.dirname(__file__)
_REL_ICONS = os.path.normpath(os.path.join(_THIS_DIR, "..", "rodlerIcons"))
ABS_FALLBACK = r"C:\Users\mauri\OneDrive\Desktop\sistema-informatico\rodlerIcons"
ICONS_BASE = _REL_ICONS if os.path.isdir(_REL_ICONS) else ABS_FALLBACK

ICONS = {
    "inicio":         os.path.join(ICONS_BASE, "home.svg"),
    "productos":      os.path.join(ICONS_BASE, "box.svg"),
    "ventas":         os.path.join(ICONS_BASE, "receipt.svg"),
    "compras":        os.path.join(ICONS_BASE, "cart.svg"),
    "obras":          os.path.join(ICONS_BASE, "crane.svg"),
    "clientes":       os.path.join(ICONS_BASE, "users.svg"),
    "proveedores":    os.path.join(ICONS_BASE, "store.svg"),
    "logout":         os.path.join(ICONS_BASE, "logout.svg"),
    "chevron_left":   os.path.join(ICONS_BASE, "chevron-left.svg"),
    "chevron_right":  os.path.join(ICONS_BASE, "chevron-right.svg"),
    "chevron_down":   os.path.join(ICONS_BASE, "chevron-down.svg"),
    "chevron_up":     os.path.join(ICONS_BASE, "chevron-up.svg"),
    "user_add":       os.path.join(ICONS_BASE, "plus.svg"),
    "moon":           os.path.join(ICONS_BASE, "moon.svg"),
    "trash":          os.path.join(ICONS_BASE, "trash.svg"),
    "user_info":      os.path.join(ICONS_BASE, "users.svg"),
}

def _load_icon(key: str) -> tuple[QIcon, str]:
    path = ICONS.get(key, "")
    if path and os.path.exists(path):
        ic = QIcon(path)
        if not ic.isNull():
            return ic, ""
    fallback_txt = {
        "inicio": "🏠", "productos": "📦", "ventas": "🧾", "compras": "🛒",
        "obras": "🏗️", "clientes": "👥", "proveedores": "🏪", "logout": "⎋",
        "chevron_left": "❮", "chevron_right": "❯",
        "chevron_down": "▾", "chevron_up": "▴",
        "user_add": "➕", "moon": "🌙", "trash": "🗑️", "user_info": "👤",
    }.get(key, "")
    return QIcon(), fallback_txt

# --- Tintado SVG ---
_SVG_TINT_CACHE: dict[tuple[str, int, int, int, int, int, int], QIcon] = {}
def svg_icon_tinted(svg_path: str, color: QColor, size: QSize) -> QIcon:
    if not svg_path or not os.path.exists(svg_path): return QIcon()
    key=(svg_path,size.width(),size.height(),color.red(),color.green(),color.blue(),color.alpha())
    if key in _SVG_TINT_CACHE and not _SVG_TINT_CACHE[key].isNull(): return _SVG_TINT_CACHE[key]
    pm = QPixmap(size); pm.fill(Qt.transparent)
    try: r = QSvgRenderer(svg_path)
    except Exception: return QIcon()
    p = QPainter(pm); r.render(p, QRect(0,0,size.width(),size.height())); p.end()
    p = QPainter(pm); p.setCompositionMode(QPainter.CompositionMode_SourceIn); p.fillRect(pm.rect(), color); p.end()
    ic = QIcon(pm)
    if not ic.isNull(): _SVG_TINT_CACHE[key]=ic
    return ic

def themed_qicon(key: str, dark: bool, size: QSize | None = None) -> tuple[QIcon, str]:
    path = ICONS.get(key, "")
    if path and os.path.exists(path):
        if dark and path.lower().endswith(".svg"):
            ic = svg_icon_tinted(path, QColor("#FFFFFF"), size or ICON_SIZE)
            if not ic.isNull(): return ic, ""
        ic = QIcon(path)
        if not ic.isNull(): return ic, ""
    return _load_icon(key)

NAV_ITEMS = [
    ("Inicio",       "inicio",      None),
    ("Productos",    "productos",   ProductosForm),
    ("Ventas",       "ventas",      VentasForm),
    ("Compras",      "compras",     ComprasForm),
    ("Obras",        "obras",       ObrasWidget),
    ("Clientes",     "clientes",    ClientesForm),
    ("Proveedores",  "proveedores", ProveedoresForm),
]

EXPANDED_WIDTH = 240
COLLAPSED_WIDTH = 72
ICON_SIZE = QSize(18, 18)

# ===== Ajustes visuales =====
CHIP_MIN_WIDTH = 230
POPUP_RIGHT_FIX = 1

# ==== refrescar UI ====
def refrescar_sistema_completo():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# ===== Permisos =====
def _session_roles_perms(session: dict) -> tuple[set[str], set[str]]:
    return set((session or {}).get("roles") or []), set((session or {}).get("perms") or [])

def _can(roles: set[str], perms: set[str], code: str) -> bool:
    return ('admin' in roles) or (code in perms)

PERM_VIEW_BY_MODULE = {
    "Productos":    "productos.view",
    "Ventas":       "ventas.view",
    "Compras":      "compras.view",
    "Obras":        "obras.view",
    "Clientes":     "clientes.view",
    "Proveedores":  "proveedores.view",
}

PERM_ACTIONS_BY_MODULE = {
    "Productos":   {"create": "productos.create",   "update": "productos.update",   "delete": "productos.delete"},
    "Ventas":      {"create": "ventas.create",      "update": "ventas.update",      "delete": "ventas.delete"},
    "Compras":     {"create": "compras.create",     "update": "compras.update",     "delete": "compras.delete"},
    "Obras":       {"create": "obras.create",       "update": "obras.update",       "delete": "obras.delete"},
    "Clientes":    {"create": "clientes.create",    "update": "clientes.update",    "delete": "clientes.delete"},
    "Proveedores": {"create": "proveedores.create", "update": "proveedores.update", "delete": "proveedores.delete"},
}

ACTION_BUTTONS_BY_MODULE = {
    "Productos":   {"create": ["btnProductoNuevo", "btnAceptarProducto"], "update": ["btnProductoEditar"], "delete": ["btnProductoEliminar"]},
    "Ventas":      {"create": ["btnVentaNueva", "btnAceptarVenta"], "update": ["btnVentaEditar"], "delete": ["btnVentaEliminar"]},
    "Compras":     {"create": ["btnCompraNueva", "btnAceptarCompra"], "update": ["btnCompraEditar"], "delete": ["btnCompraEliminar"]},
    "Obras":       {"create": ["btnObraNueva", "btnAceptarObra"], "update": ["btnObraEditar"], "delete": ["btnObraEliminar"]},
    "Clientes":    {"create": ["btnClienteNuevo", "btnAceptarCliente"], "update": ["btnClienteEditar"], "delete": ["btnClienteEliminar"]},
    "Proveedores": {"create": ["btnProveedorNuevo", "btnAceptarProveedor"], "update": ["btnProveedorEditar"], "delete": ["btnProveedorEliminar"]},
}

# ---------------- Helpers ----------------
def _circle_pix(color="#2979FF", diameter=34, text=""):
    pm = QPixmap(diameter, diameter); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHints(QPainter.Antialiasing, True)
    p.setBrush(QBrush(QColor(color))); p.setPen(Qt.NoPen); p.drawEllipse(0,0,diameter,diameter)
    if text:
        p.setPen(QPen(Qt.white)); p.drawText(pm.rect(), Qt.AlignCenter, text[:1].upper())
    p.end(); return pm

def _initial_from_name(name: str) -> str:
    name = (name or "").strip()
    return name[0].upper() if name else "U"

def _resolver_user_fields(session: dict) -> tuple[str, str]:
    user = (session or {}).get("user") or session or {}
    first = (user.get("first_name") or user.get("nombre") or "").strip()
    last  = (user.get("last_name")  or user.get("apellido") or "").strip()
    username = (user.get("username") or user.get("usuario") or "").strip()
    display = f"{first} {last}".strip() if (first or last) else (username or "Usuario")
    role = (user.get("role") or user.get("rol") or user.get("user_role") or "Usuario").strip() or "Usuario"
    return display, role


class _FuncWorker(QObject):
    finished = Signal(object, object)  

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    @Slot()
    def run(self):
        try:
            res = self._fn(*self._args, **self._kwargs)
            self.finished.emit(res, None)
        except Exception as e:
            self.finished.emit(None, e)


# ======================= Widgets =======================
class KpiTile(QFrame):
    def __init__(self, title: str, icon: str = "📊", accent=None, parent=None, show_icon: bool = True):
        super().__init__(parent)
        self.setObjectName("tarjetaDashboard")
        self.setProperty("class", "kpiTile")
        if accent == "blue":
            self.setProperty("accent", "blue")

        lay = QVBoxLayout(self); lay.setContentsMargins(16, 14, 16, 14); lay.setSpacing(6)
        row = QHBoxLayout(); row.setSpacing(10)

        self.icon = QLabel(icon)
        self.icon.setVisible(show_icon)
        if show_icon: row.addWidget(self.icon)

        self.title = QLabel(title); self.title.setProperty("role", "subtitle")
        row.addWidget(self.title); row.addStretch(1); lay.addLayout(row)

        self.value = QLabel("—"); self.value.setProperty("role", "value"); lay.addWidget(self.value)
        self.note = QLabel(""); self.note.setProperty("role", "subtitle"); lay.addWidget(self.note)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, text: str, note: str = ""):
        self.value.setText(text); self.note.setText(note)

    def apply_kpi_theme(self, dark: bool):
        fam = "'Poppins', 'Segoe UI', 'Nunito Sans', sans-serif"
        if dark:
            c_title = "#E5EDFF"; c_value = "#E5EDFF"; c_note  = "#CBD5E1"; c_icon  = "#E5EDFF"
            card_bg = "#0B1220"; card_bd = "#243147"
        else:
            c_title = "#1E293B"; c_value = "#0F172A"; c_note  = "#64748B"; c_icon  = "#1E293B"
            card_bg = "#FFFFFF"; card_bd = "rgba(0,0,0,0.08)"

        self.setStyleSheet(f"""
            QFrame#tarjetaDashboard {{
                background: {card_bg};
                border: 1px solid {card_bd};
                border-radius: 14px;
            }}
            QFrame#tarjetaDashboard QLabel {{ background: transparent; }}
        """)
        self.icon.setStyleSheet(f"font-family:{fam}; font-size:18px; font-weight:500; color:{c_icon};")
        self.title.setStyleSheet(f"font-family:{fam}; font-size:15px; font-weight:500; letter-spacing:.2px; color:{c_title};")
        self.value.setStyleSheet(f"font-family:{fam}; font-size:28px; font-weight:600; color:{c_value};")
        self.note.setStyleSheet(f"font-family:{fam}; font-size:13px; font-weight:400; color:{c_note};")


# === Parámetros de contenedores de gráficos ===
_CHART_WRAPPER_MIN_H = 240
_CHART_MAX_H = 520
_CHART_CANVAS_MARGIN = 24


def _reset_figure_geometry(fig):
    """Restore the original inch size saved on the Matplotlib figure to avoid cumulative growth."""
    if fig is None:
        return
    try:
        base = getattr(fig, "_rodler_base_inches", None)
        if base is None:
            setattr(fig, "_rodler_base_inches", tuple(fig.get_size_inches()))
        else:
            fig.set_size_inches(base, forward=False)
    except Exception:
        pass
# ============================ Popup mini-chip ============================
class UserMenuPopup(QFrame):
    newUserRequested = Signal()
    userInfoRequested = Signal()
    themeToggled = Signal(bool)
    deleteAccountRequested = Signal()
    hidden = Signal()

    def __init__(self, parent=None, is_admin=False, dark_mode=False):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("userMenuPopup")
        self.setWindowFlag(Qt.NoDropShadowWindowHint, True)
        self._is_admin = is_admin
        self._dark = bool(dark_mode)
        self._rebuild_styles()

        lay = QVBoxLayout(self); lay.setContentsMargins(12, 10, 12, 12); lay.setSpacing(10)

        self.btnInfo = QPushButton(self)
        ic_info, _ = themed_qicon("user_info", self._dark)
        if not ic_info.isNull(): self.btnInfo.setIcon(ic_info)
        self.btnInfo.setText("  Información de usuarios")
        self.btnInfo.clicked.connect(lambda: (self.userInfoRequested.emit(), self.close()))
        lay.addWidget(self.btnInfo)

        self.btnNuevo = QPushButton(self)
        ic_plus, _ = themed_qicon("user_add", self._dark)
        if not ic_plus.isNull(): self.btnNuevo.setIcon(ic_plus)
        self.btnNuevo.setText("  Nuevo usuario")
        self.btnNuevo.clicked.connect(lambda: (self.newUserRequested.emit(), self.close()))
        self.btnNuevo.setVisible(self._is_admin)
        lay.addWidget(self.btnNuevo)

        row = QHBoxLayout(); row.setContentsMargins(10, 0, 10, 0); row.setSpacing(8); row.setAlignment(Qt.AlignVCenter)
        lbl = QLabel("Modo oscuro"); lbl.setStyleSheet("background: transparent;")
        self.themeSwitch = QCheckBox(); self.themeSwitch.setObjectName("themeSwitch"); self.themeSwitch.setChecked(self._dark)
        self.themeSwitch.toggled.connect(self.themeToggled)
        row.addWidget(lbl); row.addStretch(); row.addWidget(self.themeSwitch); lay.addLayout(row)

        self.btnBorrar = QPushButton(self)
        ic_trash, _ = themed_qicon("trash", self._dark)
        if not ic_trash.isNull(): self.btnBorrar.setIcon(ic_trash)
        self.btnBorrar.setText("  Borrar cuenta")
        self.btnBorrar.clicked.connect(lambda: (self.deleteAccountRequested.emit(), self.close()))
        lay.addWidget(self.btnBorrar)

    def _rebuild_styles(self):
        if self._dark:
            css = """
            #userMenuPopup { background:#0B1220; border:1px solid #243147; border-radius:12px; padding:8px 0; }
            #userMenuPopup QPushButton { text-align:left; padding:10px 14px; margin:6px 0; border-radius:8px; color:#E5EDFF; background:transparent; border:1px solid transparent; min-height:36px; }
            #userMenuPopup QPushButton:hover { background: rgba(56,189,248,.12); }
            QCheckBox#themeSwitch::indicator { width:40px; height:20px; border-radius:10px; background:#162036; border:1px solid #243147; }
            QCheckBox#themeSwitch::indicator:checked { background:#60A5FA; border-color:#60A5FA; }
            """
        else:
            css = """
            #userMenuPopup { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:12px; padding:8px 0; }
            #userMenuPopup QPushButton { text-align:left; padding:10px 14px; margin:6px 0; border-radius:8px; color:#0F172A; background:transparent; border:1px solid transparent; min-height:36px; }
            #userMenuPopup QPushButton:hover { background: rgba(41,121,255,.08); }
            QCheckBox#themeSwitch::indicator { width:40px; height:20px; border-radius:10px; background:#E2E8F0; border:1px solid #CBD5E1; }
            QCheckBox#themeSwitch::indicator:checked { background:#2979FF; border-color:#2979FF; }
            """
        self._closed_stylesheet = css
        self._open_stylesheet = css.replace("border-radius:12px;", "border-bottom-left-radius:12px; border-bottom-right-radius:12px;")
        self.setStyleSheet(self._closed_stylesheet)

    def set_is_admin(self, is_admin: bool):
        self._is_admin = is_admin
        if hasattr(self, "btnNuevo"): self.btnNuevo.setVisible(is_admin)

    def set_dark_mode(self, dark: bool):
        if self._dark == bool(dark): return
        self._dark = bool(dark)
        self._rebuild_styles()
        self.themeSwitch.blockSignals(True); self.themeSwitch.setChecked(self._dark); self.themeSwitch.blockSignals(False)
        for btn, key in ((getattr(self, "btnNuevo", None), "user_add"), (getattr(self, "btnBorrar", None), "trash"), (getattr(self, "btnInfo", None), "user_info")):
            if btn:
                ic, _ = themed_qicon(key, self._dark)
                btn.setIcon(ic if not ic.isNull() else QIcon())

    def hideEvent(self, e):
        super().hideEvent(e)
        try: self.hidden.emit()
        except Exception: pass


# ============================ Main Widget ============================
class MenuPrincipal(QWidget):
    logoutRequested = Signal()
    newUserRequested = Signal()
    themeToggled = Signal(bool)
    deleteAccountRequested = Signal()

    class _CenterOverlay(QDialog):
        def __init__(self, parent, content: QWidget,
                     min_size=(520, 380), max_size=(760, 620),
                     preferred_size=None):
            super().__init__(parent)
            self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            self.setModal(True)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            from PySide6.QtCore import QSize
            self._min = QSize(*min_size)
            self._max = QSize(*max_size)
            self._preferred = QSize(*preferred_size) if preferred_size else None

            self.setObjectName("centerDialog")
            self.setStyleSheet("#centerDialog { background: transparent; border: none; }")

            root = QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0); root.setSizeConstraint(QVBoxLayout.SetFixedSize)
            if content is None: content = QWidget()
            try: content.hide()
            except Exception: pass
            try:
                content.setParent(self)
                content.setWindowFlags(Qt.Widget)
                content.setAttribute(Qt.WA_DeleteOnClose, False)
                content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                content.show(); content.update()
            except Exception: pass
            root.addWidget(content, 0, Qt.AlignCenter)
            self._content = content

            self.setMinimumSize(self._min); self.setMaximumSize(self._max)
            if self._preferred: self.resize(self._preferred)
            else: self.adjustSize()

            self._wire_common_close_hooks(content)
            self._wire_resize_triggers(content)

        def _wire_common_close_hooks(self, content: QWidget):
            for sig_name in ("cancelled", "requestClose", "requestCloseDialog"):
                sig = getattr(content, sig_name, None)
                if callable(getattr(sig, "connect", None)):
                    try: sig.connect(self.close)
                    except Exception: pass
            try:
                from PySide6.QtWidgets import QPushButton
                btn_cancel = content.findChild(QPushButton, "btn_cancel")
                if btn_cancel: btn_cancel.clicked.connect(self.close)
            except Exception: pass
            try:
                from PySide6.QtWidgets import QPushButton
                users_close = content.findChild(QPushButton, "usersCloseBtn")
                if users_close: users_close.clicked.connect(self.close)
            except Exception: pass

        def _wire_resize_triggers(self, content: QWidget):
            try:
                from PySide6.QtWidgets import QStackedWidget
                for st in content.findChildren(QStackedWidget):
                    st.currentChanged.connect(lambda *_: self._sync_to_content())
            except Exception: pass
            content.installEventFilter(self)
            QTimer.singleShot(0, self._sync_to_content)
            QTimer.singleShot(1, self._sync_to_content)

        def eventFilter(self, obj, ev):
            if obj is self._content and ev.type() in (QEvent.LayoutRequest, QEvent.Resize, QEvent.Show):
                self._sync_to_content()
            return super().eventFilter(obj, ev)

        def _apply_screen_bounds(self):
            try:
                parent = self.parentWidget() or self
                center_point = parent.mapToGlobal(parent.rect().center())
                screen = QApplication.screenAt(center_point) or QApplication.primaryScreen()
                if not screen: return
                avail = screen.availableGeometry()
                safe_w = max(120, avail.width() - 16)
                safe_h = max(120, avail.height() - 16)
                from PySide6.QtCore import QSize
                screen_max = QSize(safe_w, safe_h)
                self.setMaximumSize(self._max.boundedTo(screen_max))
            except Exception: pass

        def _sync_to_content(self):
            try: hint = self._content.sizeHint()
            except Exception: hint = self.sizeHint()
            if hint.width() < self.minimumWidth():  self.setMinimumWidth(hint.width())
            if hint.height() < self.minimumHeight(): self.setMinimumHeight(hint.height())
            w = min(self.maximumWidth(), max(self.minimumWidth(), hint.width()))
            h = min(self.maximumHeight(), max(self.minimumHeight(), hint.height()))
            self.resize(w, h); self.adjustSize(); self._recenter()

        def _recenter(self):
            try:
                parent = self.parentWidget() or self
                center_point = parent.mapToGlobal(parent.rect().center()) if parent else QPoint(0, 0)
                screen = QApplication.screenAt(center_point) or QApplication.primaryScreen()
                if screen:
                    geo = screen.availableGeometry()
                    x = geo.x() + (geo.width() - self.width()) // 2
                    y = geo.y() + (geo.height() - self.height()) // 2
                    self.move(x, y)
            except Exception: pass

        def showEvent(self, e):
            super().showEvent(e); self._apply_screen_bounds(); self._sync_to_content()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape: self.close()
            else: super().keyPressEvent(e)


    def __init__(self, session: dict | None = None, parent=None):
        super().__init__(parent)
        self.session = session or {}
        self._sidebar_collapsed = False
        self._userMenuPopup = None
        self._current_dark = bool(((self.session or {}).get("user") or {}).get("dark_mode", False))

        # overlay persistente (mantenido)
        self._overlayHost = None
        self._overlayCard = None
        self._overlayBody = None

        # threads y job-ids
        self._threads: dict[str, dict] = {}
        self._job_seq = {"kpis": 0}

        # estado de cierre
        self._shutting_down = False

        self._build_ui()
        self._ensure_overlay_host()
        self._apply_theme(self._current_dark)

        self.installEventFilter(self); self.topBar.installEventFilter(self); self.userChip.installEventFilter(self)
        for w in (self.avatarLbl, self.nameLbl, self.roleLbl, self.userChipArrow):
            w.installEventFilter(self)

        self._ensure_perms_loaded()
        self._apply_permissions_global()
        QTimer.singleShot(0, self._refresh_inicio_data_async)
        

        self.newUserRequested.connect(self._on_new_user_requested)
        self.themeToggled.connect(self._on_theme_toggled)
        self.deleteAccountRequested.connect(self._on_delete_account_requested)

        # Inicio
        if self._user_can_dashboard():
            self._ensure_inicio_visible_widgets()
            self._refresh_inicio_data_async()
            self._render_dashboard_charts()  # construir gráficos desde cero
        else:
            self._blank_inicio()

        # --- Event filter
    def eventFilter(self, obj: QObject, ev: QEvent) -> bool:
        if obj in (getattr(self, "userChip", None), self.avatarLbl, self.nameLbl, self.roleLbl, self.userChipArrow):
            if ev.type() == QEvent.MouseButtonPress and hasattr(ev, "button") and ev.button() == Qt.LeftButton:
                self._toggle_user_menu_popup(); return True
        if obj in (self, getattr(self, "topBar", None), getattr(self, "userChip", None)):
            if ev.type() in (QEvent.Resize, QEvent.Move, QEvent.Show, QEvent.LayoutRequest):
                self._reposition_user_menu_popup()
                self._resize_overlay_host()
        return super().eventFilter(obj, ev)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._reposition_user_menu_popup()
        self._resize_overlay_host()

    # -------------------- UI --------------------
    def _build_ui(self):
        self.rootLayout = QGridLayout(self); self.rootLayout.setContentsMargins(0,0,0,0); self.rootLayout.setSpacing(0)

        mainContainer = QWidget(self); mainContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid = QGridLayout(mainContainer); grid.setContentsMargins(0,0,0,0); grid.setSpacing(0)

        # Top bar
        self.topBar = QWidget(mainContainer); self.topBar.setObjectName("topBar")
        self.topBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tb = QHBoxLayout(self.topBar); tb.setContentsMargins(8,6,8,6); tb.setSpacing(8)

        brandWrap = QFrame(self.topBar); brandWrap.setObjectName("brand")
        brandWrap.setStyleSheet("background: transparent; border: none;")
        brandL = QVBoxLayout(brandWrap); brandL.setContentsMargins(0,0,0,0)
        self.appTitle = QLabel("Rodler"); self.appTitle.setObjectName("appTitle"); brandL.addWidget(self.appTitle)
        self.appTitle.setCursor(Qt.PointingHandCursor)
        self.appTitle.setToolTip("Refrescar sistema")

        self.appTitle.mousePressEvent = lambda event: refrescar_sistema_completo()
        tb.addWidget(brandWrap); tb.addStretch(1)

        # Chip
        self.userChip = QFrame(self.topBar); self.userChip.setObjectName("userChip")
        self.userChip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.userChip.setMinimumWidth(CHIP_MIN_WIDTH)
        chipL = QHBoxLayout(self.userChip); chipL.setContentsMargins(12, 6, 12, 6); chipL.setSpacing(8); chipL.setAlignment(Qt.AlignCenter)

        self.avatarLbl = QLabel(); self.avatarLbl.setFixedSize(28, 28)
        self.nameLbl = QLabel(); self.nameLbl.setProperty("role", "name")
        self.roleLbl = QLabel(); self.roleLbl.setProperty("role", "role")
        txtBox = QVBoxLayout(); txtBox.setContentsMargins(0, 0, 0, 0); txtBox.setSpacing(0); txtBox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.nameLbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter); self.roleLbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        txtBox.addWidget(self.nameLbl); txtBox.addWidget(self.roleLbl)

        self.userChipArrow = QPushButton(); self.userChipArrow.setObjectName("userChipArrow")
        self.userChipArrow.setCursor(Qt.PointingHandCursor); self.userChipArrow.setToolTip("Abrir menú")
        ic_down, fb_down = themed_qicon("chevron_down", False)
        if not ic_down.isNull(): self.userChipArrow.setIcon(ic_down)
        else: self.userChipArrow.setText(fb_down or "▾")

        chipL.addWidget(self.avatarLbl, 0, Qt.AlignVCenter)
        chipL.addLayout(txtBox)
        chipL.addWidget(self.userChipArrow, 0, Qt.AlignVCenter)
        tb.addWidget(self.userChip, 0, Qt.AlignRight)

        self.update_user_info(self.session)
        grid.addWidget(self.topBar, 0, 0, 1, 2)

        # Sidebar
        self.menuLateral = QFrame(mainContainer); self.menuLateral.setObjectName("sidebar")
        self.menuLateral.setMaximumWidth(EXPANDED_WIDTH); self.menuLateral.setMinimumWidth(0)
        self.menuLateral.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.animation_sidebar = QPropertyAnimation(self.menuLateral, b"maximumWidth"); self.animation_sidebar.setDuration(220)

        sb = QVBoxLayout(self.menuLateral); sb.setContentsMargins(12,12,12,12); sb.setSpacing(10)

        header = QFrame(self.menuLateral); header.setObjectName("sidebarHeader")
        hLay = QHBoxLayout(header); hLay.setContentsMargins(0,0,0,0); hLay.addSpacerItem(QSpacerItem(1,1,QSizePolicy.Expanding,QSizePolicy.Minimum))

        che_left, fb_l = themed_qicon("chevron_left", self._current_dark)
        self.botonOcultarMenu = QPushButton(fb_l if che_left.isNull() else "")
        self.botonOcultarMenu.setIcon(che_left if not che_left.isNull() else QIcon())
        self.botonOcultarMenu.setIconSize(ICON_SIZE)
        self.botonOcultarMenu.setObjectName("toggleSidebarBtn")
        self.botonOcultarMenu.setCursor(Qt.PointingHandCursor); self.botonOcultarMenu.setToolTip("Colapsar menú")
        self.botonOcultarMenu.clicked.connect(self.toggleMenuLateral)
        hLay.addWidget(self.botonOcultarMenu); sb.addWidget(header)

        self.btn_group = QButtonGroup(self); self.btn_group.setExclusive(True)
        self.menu_buttons = {}; self.modulos = {}

        def _make_nav_button(nombre: str, icon_key: str):
            icon, fb = themed_qicon(icon_key, self._current_dark)
            btn = QPushButton(nombre if icon.isNull() else nombre)
            btn.setCheckable(True); btn.setProperty("nav", True); btn.setProperty("mini", False)
            btn.setCursor(Qt.PointingHandCursor); btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(36)
            if not icon.isNull(): btn.setIcon(icon); btn.setIconSize(ICON_SIZE)
            else: btn.setText(f"{fb}  {nombre}" if fb else nombre)
            return btn

        for nombre, icon_key, clase in NAV_ITEMS:
            self.modulos[nombre] = clase
            btn = _make_nav_button(nombre, icon_key)
            btn.clicked.connect(lambda checked, m=nombre: self.abrir_modulo(m))
            sb.addWidget(btn); self.btn_group.addButton(btn); self.menu_buttons[nombre] = btn

        sb.addStretch(1)

        lg_icon, lg_fb = themed_qicon("logout", self._current_dark)
        self.logoutBtn = QPushButton("Logout" if lg_icon.isNull() else "Logout")
        self.logoutBtn.setObjectName("logoutBtn"); self.logoutBtn.setCursor(Qt.PointingHandCursor)
        if not lg_icon.isNull(): self.logoutBtn.setIcon(lg_icon); self.logoutBtn.setIconSize(ICON_SIZE)
        else:
            if lg_fb: self.logoutBtn.setText(f"{lg_fb}  Logout")
        self.logoutBtn.setToolTip("Cerrar sesión"); self.logoutBtn.clicked.connect(self._do_logout)
        sb.addWidget(self.logoutBtn)

        grid.addWidget(self.menuLateral, 1, 0, 1, 1)

        # Stack contenido
        self.stackedWidget = QStackedWidget(mainContainer); self.stackedWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Dashboard (Inicio)
        self.paginaPrincipal = QWidget(); self.paginaPrincipal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        dashboard = QGridLayout(self.paginaPrincipal)
        dashboard.setContentsMargins(0,0,0,0)
        dashboard.setHorizontalSpacing(12); dashboard.setVerticalSpacing(12)

        # KPIs sin íconos
        self.kpi_ventas  = KpiTile("Ventas del mes", show_icon=False)
        self.kpi_compras = KpiTile("Compras del mes", show_icon=False)
        self.kpi_topprod = KpiTile("Producto más vendido (mes)", show_icon=False)
        self.kpi_stock   = KpiTile("Stock crítico", show_icon=False)

        # placeholders mientras carga
        self.kpi_ventas.set_value("Cargando…", "Total vendido")
        self.kpi_compras.set_value("Cargando…", "Total comprado")
        self.kpi_topprod.set_value("Cargando…", "")
        self.kpi_stock.set_value("—", "…")

        kpis = QHBoxLayout()
        for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock):
            w.setMinimumHeight(90)
            w.apply_kpi_theme(self._current_dark)
            kpis.addWidget(w)
        kpis_wrap = QFrame(); kpis_wrap.setLayout(kpis); kpis_wrap.setObjectName("transparent")
        kpis_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dashboard.addWidget(kpis_wrap, 0, 0, 1, 3)

        # === Gráficos (versión mínima estable 2x2) ===
        chartsWrap = QFrame(self.paginaPrincipal)
        chartsWrap.setObjectName("transparent")
        chartsWrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chartsLay = QVBoxLayout(chartsWrap); chartsLay.setContentsMargins(0,0,0,0); chartsLay.setSpacing(0)

        chartsGridWrap = QWidget(chartsWrap)
        self.chartGrid = QGridLayout(chartsGridWrap)
        self.chartGrid.setContentsMargins(0,0,0,0)
        self.chartGrid.setHorizontalSpacing(12)
        self.chartGrid.setVerticalSpacing(12)
        chartsLay.addWidget(chartsGridWrap)

        dashboard.addWidget(chartsWrap, 1, 0, 1, 3)

        # Clima
        self.weather = DashboardWeatherPanel(); self.weather.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dashboard.addWidget(self.weather, 2, 0, 1, 3)

        # Distribución vertical: la fila 1 absorbe el extra
        dashboard.setRowStretch(0, 0)   # KPIs
        dashboard.setRowStretch(1, 1)   # gráficos
        dashboard.setRowStretch(2, 0)   # clima

        dashboard.setColumnStretch(0, 1); dashboard.setColumnStretch(1, 1); dashboard.setColumnStretch(2, 1)

        self.stackedWidget.addWidget(self.paginaPrincipal)
        grid.addWidget(self.stackedWidget, 1, 1, 1, 1)

        grid.setRowStretch(0, 0); grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 0); grid.setColumnStretch(1, 1)

        self.rootLayout.addWidget(mainContainer, 0, 0)
        self.menu_buttons["Inicio"].setChecked(True)
        self.stackedWidget.setCurrentWidget(self.paginaPrincipal)

    # ---------- Overlay persistente ----------
    def _ensure_overlay_host(self):
        if self._overlayHost:
            self._resize_overlay_host()
            return
        ov = QFrame(self); ov.setObjectName("overlayHost")
        ov.setStyleSheet("""
            #overlayHost { background: rgba(0,0,0,.30); }
            #overlayCard { background: palette(base); border:1px solid rgba(0,0,0,.12); border-radius:12px; }
        """)
        ov.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        ov.hide()

        lay = QVBoxLayout(ov); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        centerWrap = QWidget(ov); cwL = QVBoxLayout(centerWrap); cwL.setAlignment(Qt.AlignCenter); cwL.setContentsMargins(0,0,0,0); cwL.setSpacing(0)
        card = QFrame(centerWrap); card.setObjectName("overlayCard")
        cardL = QVBoxLayout(card); cardL.setContentsMargins(16,16,16,16); cardL.setSpacing(10)

        btnClose = QPushButton("✕", card); btnClose.setCursor(Qt.PointingHandCursor); btnClose.setFixedWidth(34)
        btnClose.setStyleSheet("QPushButton{border:none;font-size:16px;} QPushButton:hover{background:rgba(0,0,0,.06); border-radius:6px;}")
        hdr = QHBoxLayout(); hdr.addStretch(1); hdr.addWidget(btnClose); cardL.addLayout(hdr)

        body = QFrame(card); body.setObjectName("overlayBody")
        bodyL = QVBoxLayout(body); bodyL.setContentsMargins(0,0,0,0); bodyL.setSpacing(0)
        cardL.addWidget(body)

        cwL.addWidget(card); lay.addWidget(centerWrap)

        self._overlayHost = ov; self._overlayCard = card; self._overlayBody = body

        btnClose.clicked.connect(self._hide_overlay)
        ov.installEventFilter(self)
        self._resize_overlay_host()

    def _resize_overlay_host(self):
        if self._overlayHost:
            self._overlayHost.setGeometry(self.rect())

    def _hide_overlay(self):
        if not self._overlayHost: return
        bodyL = self._overlayBody.layout()
        while bodyL.count():
            it = bodyL.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._overlayHost.hide()

    def _embed_as_widget(self, w: QWidget):
        if not w: return QWidget()
        try: w.hide()
        except Exception: pass
        try:
            w.setParent(self._overlayBody)
            w.setWindowFlags(Qt.Widget)
            w.setAttribute(Qt.WA_DeleteOnClose, False)
            w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        except Exception: pass
        return w

    def _show_overlay_with(self, content: QWidget, min_wh=(720,420), max_wh=(1100,800)):
        self._ensure_overlay_host()
        cont = self._embed_as_widget(content)
        try:
            self._overlayCard.setMinimumSize(*min_wh)
            self._overlayCard.setMaximumSize(*max_wh)
        except Exception: pass
        bodyL = self._overlayBody.layout()
        while bodyL.count():
            it = bodyL.takeAt(0)
            old = it.widget()
            if old:
                old.setParent(None)
                old.deleteLater()
        bodyL.addWidget(cont)
        self._resize_overlay_host()
        self._overlayHost.show()
        self._overlayHost.raise_()

    # ===== Helper para abrir el QDialog centrado =====
    def _show_center_overlay_dialog(self, content: QWidget, min_wh=(520,380), max_wh=(760,620)):
        dlg = self._CenterOverlay(self, content, min_size=min_wh, max_size=max_wh)
        dlg.exec()

    # -------------------- Tema --------------------
    def _refresh_all_icons(self):
        for nombre, icon_key, _ in NAV_ITEMS:
            btn = self.menu_buttons.get(nombre)
            if not btn: continue
            ic, fb = themed_qicon(icon_key, self._current_dark)
            if not ic.isNull():
                btn.setIcon(ic); btn.setIconSize(ICON_SIZE)
                btn.setText("" if self._sidebar_collapsed else nombre)
            else:
                btn.setIcon(QIcon())
                btn.setText((fb if self._sidebar_collapsed else (f"{fb}  {nombre}" if fb else nombre)) if fb else ("" if self._sidebar_collapsed else nombre))

        che_key = "chevron_right" if self._sidebar_collapsed else "chevron_left"
        ic, fb = themed_qicon(che_key, self._current_dark)
        if not ic.isNull():
            self.botonOcultarMenu.setIcon(ic); self.botonOcultarMenu.setIconSize(ICON_SIZE); self.botonOcultarMenu.setText("")
        else:
            self.botonOcultarMenu.setIcon(QIcon()); self.botonOcultarMenu.setText(fb or "")

        ic, fb = themed_qicon("logout", self._current_dark)
        if not ic.isNull():
            self.logoutBtn.setIcon(ic); self.logoutBtn.setIconSize(ICON_SIZE)
            self.logoutBtn.setText("" if self._sidebar_collapsed else "Logout")
        else:
            self.logoutBtn.setIcon(QIcon())
            self.logoutBtn.setText((fb or "Logout") if not self._sidebar_collapsed else (fb or ""))

        arrow_key = "chevron_up" if (self._userMenuPopup and self._userMenuPopup.isVisible()) else "chevron_down"
        ic, fb = themed_qicon(arrow_key, self._current_dark)
        if not ic.isNull():
            self.userChipArrow.setIcon(ic); self.userChipArrow.setIconSize(ICON_SIZE); self.userChipArrow.setText("")
        else:
            self.userChipArrow.setIcon(QIcon()); self.userChipArrow.setText(fb or ("▴" if arrow_key=="chevron_up" else "▾"))

        if self._userMenuPopup:
            for btn, key in ((getattr(self._userMenuPopup, "btnNuevo", None), "user_add"),
                             (getattr(self._userMenuPopup, "btnBorrar", None), "trash"),
                             (getattr(self._userMenuPopup, "btnInfo",  None), "user_info")):
                if btn:
                    ic, _ = themed_qicon(key, self._current_dark)
                    btn.setIcon(ic if not ic.isNull() else QIcon())

    def _apply_theme(self, dark: bool):
        qss = QSS_RODLER_DARK if dark else QSS_RODLER_LIGHT
        QApplication.instance().setStyleSheet(qss)
        self._current_dark = bool(dark)
        try: gs.apply_chart_theme(bool(dark))
        except Exception: pass
        try:
            display_name, _ = _resolver_user_fields(self.session)
            initial = _initial_from_name(display_name)
            self.avatarLbl.setPixmap(_circle_pix("#2979FF", 28, initial).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception: pass
        if self._userMenuPopup is not None:
            try:
                self._userMenuPopup.set_dark_mode(self._current_dark)
                self._userMenuPopup.setStyleSheet(self._userMenuPopup._open_stylesheet if self._userMenuPopup.isVisible() else self._userMenuPopup._closed_stylesheet)
            except Exception: pass

        self._refresh_all_icons()

        # Re-tintear KPIs
        for w in (getattr(self, "kpi_ventas", None),
                  getattr(self, "kpi_compras", None),
                  getattr(self, "kpi_topprod", None),
                  getattr(self, "kpi_stock", None)):
            if w: w.apply_kpi_theme(self._current_dark)

        # Re-render de gráficos con el tema vigente
        try:
            if self._user_can_dashboard() and self.stackedWidget.currentWidget() is self.paginaPrincipal:
                self._render_dashboard_charts()
        except Exception:
            pass

    # -------------------- Información de usuario --------------------
    def update_user_info(self, session: dict | None = None):
        if session is not None: self.session = session
        display_name, role = _resolver_user_fields(self.session)
        self.nameLbl.setText(display_name); self.roleLbl.setText(role)
        initial = _initial_from_name(display_name)
        avatar_pm = _circle_pix("#2979FF", 28, initial)
        self.avatarLbl.setPixmap(avatar_pm.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self._userMenuPopup is not None:
            roles, _ = _session_roles_perms(self.session)
            self._userMenuPopup.set_is_admin('admin' in roles)
            try: self._userMenuPopup.set_dark_mode(self._current_dark)
            except Exception: pass

    # -------------------- Popup del chip --------------------
    def _ensure_user_menu_popup(self):
        if self._userMenuPopup is None:
            roles, _ = _session_roles_perms(self.session)
            is_admin = ('admin' in roles)
            self._userMenuPopup = UserMenuPopup(parent=self, is_admin=is_admin, dark_mode=self._current_dark)
            self._userMenuPopup.newUserRequested.connect(self.newUserRequested)
            self._userMenuPopup.userInfoRequested.connect(self._open_users_info_overlay)
            self._userMenuPopup.themeToggled.connect(self._on_theme_toggled_proxy)
            self._userMenuPopup.deleteAccountRequested.connect(self.deleteAccountRequested)
            self._userMenuPopup.hidden.connect(self._on_user_menu_hidden)
        roles, _ = _session_roles_perms(self.session)
        self._userMenuPopup.set_is_admin('admin' in roles)
        self._userMenuPopup.set_dark_mode(self._current_dark)

    def _toggle_user_menu_popup(self):
        self._ensure_user_menu_popup()
        popup = self._userMenuPopup
        if popup.isVisible():
            popup.close(); self._refresh_all_icons(); return
        self.userChip.setStyleSheet("#userChip{border-bottom-left-radius:0px;border-bottom-right-radius:0px;}")
        popup.setStyleSheet(popup._open_stylesheet)
        popup.show(); popup.raise_()
        QTimer.singleShot(0, self._finalize_popup_open)
        QTimer.singleShot(1, self._finalize_popup_open)
        self._refresh_all_icons()

    def _finalize_popup_open(self): self._reposition_user_menu_popup()

    def _on_user_menu_hidden(self):
        try:
            self.userChip.setStyleSheet("")
            if self._userMenuPopup: self._userMenuPopup.setStyleSheet(self._userMenuPopup._closed_stylesheet)
        except Exception: pass
        self._refresh_all_icons()

    def _chip_global_rect(self) -> QRect:
        tl = self.userChip.mapToGlobal(QPoint(0, 0))
        br = self.userChip.mapToGlobal(QPoint(self.userChip.width(), self.userChip.height()))
        w = max(0, br.x() - tl.x()); h = max(0, br.y() - tl.y())
        return QRect(tl, QSize(w, h))

    def _reposition_user_menu_popup(self):
        popup = self._userMenuPopup
        if not popup or not popup.isVisible(): return
        chip_rect = self._chip_global_rect()
        chip_w = int(round(chip_rect.width()))
        fixed_w = max(0, chip_w - POPUP_RIGHT_FIX)
        popup.setMinimumWidth(fixed_w); popup.setMaximumWidth(fixed_w)
        bottom_left = QPoint(chip_rect.left(), chip_rect.bottom() + 1)
        h = popup.sizeHint().height()
        tgt = QRect(bottom_left, QSize(fixed_w, h))
        scr = QApplication.screenAt(bottom_left) or QApplication.primaryScreen()
        avail = scr.availableGeometry() if scr else QRect(0,0,10_000,10_000)
        if tgt.right() > avail.right(): tgt.moveLeft(min(bottom_left.x(), avail.right() - tgt.width()))
        if tgt.left() < avail.left():   tgt.moveLeft(avail.left())
        if tgt.bottom() > avail.bottom():
            above_top_left = QPoint(chip_rect.left(), chip_rect.top() - h - 1)
            tgt.moveTopLeft(above_top_left)
            if tgt.top() < avail.top(): tgt.moveTop(avail.top())
        popup.setGeometry(tgt); popup.update()

    def _on_theme_toggled_proxy(self, dark: bool):
        try: self.session.setdefault("user", {}); self.session["user"]["dark_mode"] = bool(dark)
        except Exception: pass
        self.themeToggled.emit(dark)

    def _on_theme_toggled(self, dark: bool):
        if getattr(self, "_shutting_down", False):
            return
        self._apply_theme(bool(dark))

    # -------------------- Acciones de overlay --------------------
    def _open_users_info_overlay(self):
        try:
            w = UsersListWindow(parent=None)
            self._show_center_overlay_dialog(w, min_wh=(520,380), max_wh=(760,620))
        except Exception as e:
            QMessageBox.critical(self, "Usuarios", f"No se pudo abrir la información de usuarios.\n\n{e}")

    def _on_new_user_requested(self):
        try:
            from forms import create_user_form as m
            if hasattr(m, "Ui_Form"):
                w = QWidget(); m.Ui_Form().setupUi(w)
            elif hasattr(m, "CreateUserForm"):
                w = m.CreateUserForm()
            else:
                raise RuntimeError("forms/create_user_form.py no define Ui_Form ni CreateUserForm.")
            self._show_center_overlay_dialog(w, min_wh=(700,420), max_wh=(1000,760))
        except Exception as e:
            QMessageBox.information(self, "Nuevo usuario", f"No se pudo abrir el formulario de alta.\n\n{e}")

    def _on_delete_account_requested(self):
        QMessageBox.information(self, "Cuenta", "Funcionalidad de borrado pendiente de implementación.")


        # -------------------- Logout & cierre seguro --------------------
    def _stop_all_threads(self, timeout_ms: int = 1500):
        items = list((self._threads or {}).items())
        self._threads.clear()
        for name, rec in items:
            th = (rec or {}).get("thread")
            if th is None:
                continue
            try:
                th.requestInterruption()
            except Exception:
                pass
            try:
                th.quit()
            except Exception:
                pass
            try:
                th.wait(timeout_ms)
            except Exception:
                pass

        # detener posibles timers del clima
        try:
            w = getattr(self, "weather", None)
            for m in ("stop", "shutdown", "request_stop", "stop_threads"):
                if hasattr(w, m) and callable(getattr(w, m)):
                    try:
                        getattr(w, m)()
                    except Exception:
                        pass
            for m in ("timer", "_timer", "refresh_timer"):
                t = getattr(w, m, None)
                try:
                    if t:
                        t.stop()
                except Exception:
                    pass
        except Exception:
            pass

    def _do_logout(self):
        self._shutting_down = True
        try:
            self._stop_all_threads()
        finally:
            try:
                self.logoutRequested.emit()
            finally:
                self.close()

    def closeEvent(self, e):
        self._shutting_down = True
        try:
            self._stop_all_threads()
        except Exception:
            pass
        super().closeEvent(e)

    # -------------------- permisos / dashboard --------------------
    def _ensure_perms_loaded(self):
        if (self.session or {}).get("perms"): return
        user = (self.session or {}).get("user") or {}
        username = (user.get("username") or "").strip().lower()
        if not username: return
        try:
            eng = _get_engine_cached()
            with eng.connect() as con:
                rows = con.execute(text("""
                    SELECT perm_code
                    FROM rodler_auth.v_user_permissions
                    WHERE lower(username) = :u
                    ORDER BY perm_code
                """), {"u": username}).fetchall()
                self.session.setdefault("perms", [r[0] for r in rows])
        except Exception as e:
            print("[MenuPrincipal] No se pudieron cargar permisos:", e)

    def _user_can_dashboard(self) -> bool:
        try:
            eng = _get_engine_cached()
            username = ((self.session or {}).get("user") or {}).get("username", "")
            if not username: return False
            with eng.connect() as con:
                row = con.execute(text("""
                    SELECT v.can_dashboard
                    FROM rodler_auth.v_user_can_dashboard v
                    JOIN rodler_auth.users u ON u.id = v.user_id
                    WHERE lower(u.username) = :u
                    LIMIT 1
                """), {"u": username.lower()}).fetchone()
                return bool(row[0]) if row else False
        except Exception:
            return False

    def _apply_permissions_global(self):
        roles, perms = _session_roles_perms(self.session)
        if self._user_can_dashboard(): self._ensure_inicio_visible_widgets()
        else: self._blank_inicio()

        # Modo permisivo si no hay permisos cargados
        perms_loaded = bool((self.session or {}).get("perms"))
        for nombre, btn in self.menu_buttons.items():
            code = PERM_VIEW_BY_MODULE.get(nombre)
            if not code:
                btn.setVisible(True)
            else:
                btn.setVisible(True if not perms_loaded else _can(roles, perms, code))

        if self.stackedWidget.currentWidget() is None:
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)

    def _blank_inicio(self):
        if getattr(self, "_inicio_blank", False): return
        self._inicio_blank = True
        try:
            for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock, self.weather):
                if w and w.parent(): w.setVisible(False)
            if not hasattr(self, "_lblInicioVacio"):
                self._lblInicioVacio = QLabel("", self.paginaPrincipal)
                self._lblInicioVacio.setStyleSheet("color:#94A3B8; font-size:13px; background: transparent;")
                lay = self.paginaPrincipal.layout()
                spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
                if lay:
                    lay.addItem(spacer); lay.addWidget(self._lblInicioVacio); lay.addItem(spacer)
            self._lblInicioVacio.setText(""); self._lblInicioVacio.setVisible(True)
        except Exception:
            pass

    def _ensure_inicio_visible_widgets(self):
        self._inicio_blank = False
        for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock, self.weather):
            try:
                if w: w.setVisible(True)
            except Exception:
                pass
        if hasattr(self, "_lblInicioVacio"): self._lblInicioVacio.setVisible(False)

    # -------------------- permisos por módulo --------------------
    def _apply_permissions_to_module_page(self, nombre_modulo: str, pagina: QWidget):
        if pagina is None:
            return

        roles, perms = _session_roles_perms(self.session)

        def _grey_disable(w):
            try:
                w.setEnabled(False)
                if hasattr(w, "setGraphicsEffect"):
                    try:
                        from PySide6.QtWidgets import QGraphicsOpacityEffect
                        eff = QGraphicsOpacityEffect(w)
                        eff.setOpacity(0.6)
                        w.setGraphicsEffect(eff)
                    except Exception:
                        pass
                st = w.style()
                st.unpolish(w); st.polish(w)
            except Exception:
                pass

        actions = PERM_ACTIONS_BY_MODULE.get(nombre_modulo) or {}
        lacks = {
            "create": not _can(roles, perms, actions.get("create", "")),
            "update": not _can(roles, perms, actions.get("update", "")),
            "delete": not _can(roles, perms, actions.get("delete", "")),
        }

        # 1) Por mapeo explícito de botones
        names_map = ACTION_BUTTONS_BY_MODULE.get(nombre_modulo, {})
        for kind, need in lacks.items():
            if not need:
                continue
            for obj_name in names_map.get(kind, []):
                btn = pagina.findChild(QPushButton, obj_name)
                if btn:
                    _grey_disable(btn)

        # 2) Por propiedad 'perm_code' en botones
        for b in pagina.findChildren(QPushButton):
            if not b.isEnabled():
                continue
            perm_code = (b.property("perm_code") or "").strip()
            if perm_code and not _can(roles, perms, perm_code):
                _grey_disable(b)

        # 3) Heurística textual (fallback)
        for b in pagina.findChildren(QPushButton):
            if not b.isEnabled():
                continue
            name = (b.objectName() or "").lower()
            text = (b.text() or "").lower()
            if lacks["create"] and any(k in name or k in text for k in ("nuevo","crear","guardar","registrar")):
                _grey_disable(b); continue
            if lacks["update"] and any(k in name or k in text for k in ("editar","modificar","actualizar")):
                _grey_disable(b); continue
            if lacks["delete"] and any(k in name or k in text for k in ("eliminar","borrar","quitar","suprimir")):
                _grey_disable(b); continue

    # -------------------- sidebar --------------------
    def _apply_sidebar_mode(self, collapsed: bool):
        if collapsed:
            for nombre, icon_key, _ in NAV_ITEMS:
                btn = self.menu_buttons[nombre]
                btn.setProperty("mini", True); btn.setToolTip(nombre)
                ic, fb = themed_qicon(icon_key, self._current_dark)
                if not ic.isNull(): btn.setText(""); btn.setIcon(ic); btn.setIconSize(ICON_SIZE)
                else: btn.setText(fb)
            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth()); self.animation_sidebar.setEndValue(COLLAPSED_WIDTH)

            che_right, fb_r = themed_qicon("chevron_right", self._current_dark)
            self.botonOcultarMenu.setIcon(che_right if not che_right.isNull() else QIcon())
            self.botonOcultarMenu.setText(fb_r if che_right.isNull() else ""); self.botonOcultarMenu.setToolTip("Expandir menú")

            lg_icon, lg_fb = themed_qicon("logout", self._current_dark)
            if not lg_icon.isNull(): self.logoutBtn.setText(""); self.logoutBtn.setIcon(lg_icon); self.logoutBtn.setIconSize(ICON_SIZE)
            else: self.logoutBtn.setText(lg_fb or "⎋"); self.logoutBtn.setToolTip("Cerrar sesión")
        else:
            for nombre, icon_key, _ in NAV_ITEMS:
                btn = self.menu_buttons[nombre]
                btn.setProperty("mini", False); btn.setToolTip("")
                ic, fb = themed_qicon(icon_key, self._current_dark)
                if not ic.isNull(): btn.setIcon(ic); btn.setIconSize(ICON_SIZE); btn.setText(nombre)
                else: btn.setText(f"{fb}  {nombre}" if fb else nombre)

            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth()); self.animation_sidebar.setEndValue(EXPANDED_WIDTH)

            che_left, fb_l = themed_qicon("chevron_left", self._current_dark)
            self.botonOcultarMenu.setIcon(che_left if not che_left.isNull() else QIcon())
            self.botonOcultarMenu.setText(fb_l if che_left.isNull() else ""); self.botonOcultarMenu.setToolTip("Colapsar menú")

            lg_icon, lg_fb = themed_qicon("logout", self._current_dark)
            if not lg_icon.isNull(): self.logoutBtn.setIcon(lg_icon); self.logoutBtn.setIconSize(ICON_SIZE); self.logoutBtn.setText("Logout")
            else: self.logoutBtn.setText(f"{lg_fb}  Logout" if lg_fb else "Logout"); self.logoutBtn.setToolTip("Cerrar sesión")

        self.animation_sidebar.start()
        self._refresh_all_icons()

    def toggleMenuLateral(self):
        self._sidebar_collapsed = not self._sidebar_collapsed
        self._apply_sidebar_mode(self._sidebar_collapsed)

    # -------------------- navegación módulos --------------------
    def abrir_modulo(self, nombre_modulo: str):
        roles, perms = _session_roles_perms(self.session)

        if nombre_modulo == "Inicio":
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)
            if self._user_can_dashboard():
                self._ensure_inicio_visible_widgets()
                self._render_dashboard_charts()
            else:
                self._blank_inicio()

            QTimer.singleShot(0, self._refresh_inicio_data_async)
            
            return
        
        

        view_code = PERM_VIEW_BY_MODULE.get(nombre_modulo)
        if view_code and not _can(roles, perms, view_code):
            return

        attr = f"pagina_{nombre_modulo}"
        if hasattr(self, attr):
            self.stackedWidget.setCurrentWidget(getattr(self, attr)); return

        clase_modulo = self.modulos[nombre_modulo]
        instancia_modulo = clase_modulo() if clase_modulo is not None else None
        pagina = self.paginaPrincipal if instancia_modulo is None else (QWidget() if hasattr(instancia_modulo, "setupUi") else instancia_modulo)
        if instancia_modulo and hasattr(instancia_modulo, "setupUi"):
            instancia_modulo.setupUi(pagina)
        try: pagina.menuPrincipalRef = self
        except Exception: pass
        self.stackedWidget.addWidget(pagina)
        setattr(self, attr, pagina)
        self._apply_permissions_to_module_page(nombre_modulo, pagina)
        self.stackedWidget.setCurrentWidget(pagina)

    # -------------------- datos/gráficos --------------------
    def _fmt_currency(self, x: float) -> str:
        return f"Gs. {x:,.0f}".replace(",", ".")

    def _query_month_bounds(self):
        with _get_engine_cached().connect() as con:
            row = con.execute(_SQL_MONTH_BOUNDS).mappings().first()
            return row['ini'], row['fin']

    def _start_thread_job(self, name: str, fn, on_done):
        """Arranca un job en QThread. on_done(result, error, job_id)."""
        jid = self._job_seq.get(name, 0) + 1
        self._job_seq[name] = jid

        th = QThread(self)
        worker = _FuncWorker(fn)
        worker.moveToThread(th)

        def _finished(res, err):
            try:
                if (jid == self._job_seq.get(name, 0)) and not getattr(self, "_shutting_down", False):
                    on_done(res, err, jid)
            finally:
                try:
                    th.quit()
                except Exception:
                    pass

        self._threads[name] = {"thread": th, "worker": worker, "jid": jid}

        worker.finished.connect(_finished)
        worker.finished.connect(worker.deleteLater)
        th.finished.connect(lambda: self._threads.pop(name, None))
        th.finished.connect(th.deleteLater)

        th.started.connect(worker.run)
        th.start()

    def _refresh_inicio_data_async(self):
        """Carga KPIs de forma síncrona y actualiza las cards (sin dejar 'Cargando…')."""
        if getattr(self, "_shutting_down", False):
            return

        try:
            data = self._compute_kpis()  # no debe lanzar; ya maneja errores internos
        except Exception as e:
            print("[Dashboard] KPI sync error:", e)
            data = {"ventas": 0, "compras": 0, "top": None, "crit": 0}

        # Actualizar SIEMPRE la UI; nunca dejar 'Cargando…'
        try:
            self._on_kpis_ready(data)
        except Exception as e:
            print("[Dashboard] KPI render error:", e)
            # Fallback duro si algo raro pasó al renderizar
            try:
                self.kpi_ventas.set_value(self._fmt_currency(0.0), "Total vendido")
                self.kpi_compras.set_value(self._fmt_currency(0.0), "Total comprado")
                self.kpi_topprod.set_value("—", "Sin ventas en el mes")
                self.kpi_stock.set_value("0", "productos en nivel crítico")
            except Exception:
                pass

        # Clima (como antes)
        QTimer.singleShot(200, lambda: self.weather.refresh_default_city())

    def _compute_kpis(self):
        eng = _get_engine_cached()
        ventas = compras = crit = 0
        top_row = None
        try:
            with eng.connect() as con:
                row = con.execute(_SQL_MONTH_BOUNDS).mappings().first()
                ini, fin = row['ini'], row['fin']

                try:
                    ventas = con.execute(_SQL_KPI_VENTAS, {'ini': ini, 'fin': fin}).scalar() or 0
                except Exception:
                    ventas = 0
                try:
                    compras = con.execute(_SQL_KPI_COMPRAS, {'ini': ini, 'fin': fin}).scalar() or 0
                except Exception:
                    compras = 0
                try:
                    top_row = con.execute(_SQL_KPI_TOP_PROD, {'ini': ini, 'fin': fin}).mappings().first()
                except Exception:
                    top_row = None
                try:
                    crit = con.execute(_SQL_KPI_CRITICOS).scalar() or 0
                except Exception:
                    crit = 0
        except Exception as e:
            print("[Dashboard] KPI error:", e)

        # Salida SIEMPRE válida
        return {
            "ventas": float(ventas or 0),
            "compras": float(compras or 0),
            "top": ( (top_row.get('nombre'), int(top_row.get('u', 0))) if (top_row and top_row.get('nombre')) else None ),
            "crit": int(crit or 0)
        }

    def _on_kpis_ready(self, data: dict):
        # NO retornamos si la ventana no está visible: actualizamos igual
        try:
            ventas  = float(data.get("ventas", 0) or 0)
            compras = float(data.get("compras", 0) or 0)
            top     = data.get("top")
            crit    = int(data.get("crit", 0) or 0)

            self.kpi_ventas.set_value(self._fmt_currency(ventas), "Total vendido")
            self.kpi_compras.set_value(self._fmt_currency(compras), "Total comprado")

            if top and isinstance(top, (tuple, list)) and top[0]:
                nombre, u = top[0], int(top[1] or 0)
                self.kpi_topprod.set_value(f"{nombre}", f"{u} u. vendidas")
            else:
                self.kpi_topprod.set_value("—", "Sin ventas en el mes")

            self.kpi_stock.set_value(str(crit), "productos en nivel crítico")
        except Exception as e:
            print("[Dashboard] KPI render error:", e)
            # Fallback duro para no dejar 'Cargando…'
            self.kpi_ventas.set_value(self._fmt_currency(0.0), "Total vendido")
            self.kpi_compras.set_value(self._fmt_currency(0.0), "Total comprado")
            self.kpi_topprod.set_value("—", "Sin ventas en el mes")
            self.kpi_stock.set_value("0", "productos en nivel crítico")

    # ======= Helpers de gráficos (mínimos y estables) =======
    def _clear_layout(self, layout):
        try:
            while layout.count():
                it = layout.takeAt(0)
                w = it.widget()
                if w:
                    w.setParent(None)
                    w.deleteLater()
        except Exception:
            pass

    def _normalize_card_figure(self, fig):
        try:
            # 0) apagar layout engine (matplotlib >=3.8)
            try:
                if getattr(fig, "get_layout_engine", None) and fig.get_layout_engine() != "none":
                    fig.set_layout_engine("none")
            except Exception:
                # fallback: desactivar constrained/tight si estuvieran activos
                try: fig.set_constrained_layout(False)
                except Exception: pass
    
            # 1) sin títulos internos
            for ax in fig.get_axes():
                try: ax.set_title("")
                except Exception: pass
    
                # 2) limpiar textos en coords de ejes salvo que el eje pida preservarlos
                preserve = bool(getattr(ax, "_rodler_preserve_axes_text", False))
                if not preserve:
                    to_remove = []
                    for t in list(ax.texts):
                        try:
                            if t.get_transform() == ax.transAxes:
                                to_remove.append(t)
                        except Exception:
                            pass
                    for t in to_remove:
                        try: t.remove()
                        except Exception: pass
    
            # 3) márgenes: solo si la figura no trae márgenes propios
            if not getattr(fig, "_rodler_custom_margins", False):
                try:
                    fig.subplots_adjust(left=0.08, right=0.985, top=0.90, bottom=0.26)
                except Exception:
                    pass
        except Exception:
            pass
        


    def _make_canvas(self, fig):
        # DPI fijo para evitar “agrandamientos”
        try:
            if getattr(fig, "get_dpi", None):
                base_dpi = getattr(gs, "BASE_DPI", 96)
                if fig.get_dpi() != base_dpi:
                    fig.set_dpi(base_dpi)
        except Exception:
            pass
        
        # Normalizar (no cortar nada y sin títulos internos; respeta donuts “preservados”)
        try:
            self._normalize_card_figure(fig)
        except Exception:
            pass
        
        # Restaurar pulgadas originales y embutir
        _reset_figure_geometry(fig)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setMinimumHeight(240)  # un pelín más alto para el número arriba del donut
        canvas.setMaximumHeight(_CHART_MAX_H - _CHART_CANVAS_MARGIN)
        return canvas


    def _render_dashboard_charts(self):
        """Crea y monta gráficos de forma directa (sin hilos), con DPI estable."""
        if getattr(self, "_shutting_down", False):
            return
        if getattr(self, "chartGrid", None) is None:
            return
        try:
            self._clear_layout(self.chartGrid)

            figs = [
                ("Ventas vs Compras", create_ventas_vs_compras_mensuales(meses=12)),
                ("Gastos mensuales",  create_gastos_mensuales(meses=12)),
                ("Presupuesto vs Gasto por obra", create_presupuesto_vs_gasto_por_obra(top_n=10)),
                ("Gastos por tipo",   create_distribucion_gastos_por_tipo()),
            ]
            positions = [(0,0), (0,1), (1,0), (1,1)]
            for (title, fig), (r, c) in zip(figs, positions):
                card = QFrame(self.paginaPrincipal)
                card.setObjectName("tarjetaDashboard")
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                card.setMinimumHeight(_CHART_WRAPPER_MIN_H); card.setMaximumHeight(_CHART_MAX_H)
                lay = QVBoxLayout(card); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)
                lbl = QLabel(title, card); lbl.setProperty("role", "cardtitle"); lbl.setStyleSheet("background: transparent;")
                lay.addWidget(lbl)
                canvas = self._make_canvas(fig)
                lay.addWidget(canvas, 1)
                try:
                    gs.restyle_figure(canvas.figure)
                except Exception:
                    pass
                self.chartGrid.addWidget(card, r, c)
        except Exception as e:
            print("[Dashboard] Error al crear/montar gráficos:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuPrincipal()
    window.show()
    sys.exit(app.exec())
