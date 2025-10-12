# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QPropertyAnimation, Signal, QTimer, QSize, QPoint, QRect, QObject, QEvent
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QPen, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton,
    QStackedWidget, QButtonGroup, QSizePolicy, QSpacerItem,
    QCheckBox, QApplication
)
from PySide6.QtSvg import QSvgRenderer  # <- para tintar SVG preservando alpha

# === Temas (themes.py) ===
# Debe exponer: QSS_RODLER_LIGHT y QSS_RODLER_DARK (ambos str)
from main.themes  import QSS_RODLER_LIGHT, QSS_RODLER_DARK

# === Módulos de tu app ===
from forms.productos_ui import Ui_Form as ProductosForm
from forms.compras_ui import Ui_Form as ComprasForm
from forms.Obras_ui import ObrasWidget
from forms.Ventas_ui import Ui_Form as VentasForm
from forms.Clientes_ui import Ui_Form as ClientesForm
from forms.Proveedores_ui import Ui_Form as ProveedoresForm

# === Gráficos ===
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from sqlalchemy import text
from graficos.graficos_dashboard import (
    get_engine,
    create_ventas_vs_compras_mensuales,
    create_gastos_mensuales,
    create_presupuesto_vs_gasto_por_obra,
    create_distribucion_gastos_por_tipo,
    create_stock_critico,
    create_top_materiales_mes,
)

# === Clima (panel separado) ===
from forms.weather_panel import DashboardWeatherPanel

# ---------------- Iconos ----------------
_THIS_DIR = os.path.dirname(__file__)
_REL_ICONS = os.path.normpath(os.path.join(_THIS_DIR, "..", "rodelrIcons"))  # path original del proyecto
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
    "user_add":       os.path.join(ICONS_BASE, "user-plus.svg"),
    "moon":           os.path.join(ICONS_BASE, "moon.svg"),
    "trash":          os.path.join(ICONS_BASE, "trash.svg"),
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
        "user_add": "➕", "moon": "🌙", "trash": "🗑️",
    }.get(key, "")
    return QIcon(), fallback_txt

# --- Tintado SVG runtime (preserva huecos/alpha) ---
_SVG_TINT_CACHE: dict[tuple[str, int, int, int, int, int, int], QIcon] = {}

def svg_icon_tinted(svg_path: str, color: QColor, size: QSize) -> QIcon:
    """
    Renderiza el SVG y aplica un tinte usando CompositionMode_SourceIn, preservando el alpha (huecos/espacios).
    Cachea el resultado por (path, size, color).
    """
    if not svg_path or not os.path.exists(svg_path):
        return QIcon()

    key = (
        svg_path,
        size.width(), size.height(),
        color.red(), color.green(), color.blue(), color.alpha()
    )
    cached = _SVG_TINT_CACHE.get(key)
    if cached is not None and not cached.isNull():
        return cached

    pm = QPixmap(size)
    pm.fill(Qt.transparent)

    try:
        r = QSvgRenderer(svg_path)
    except Exception:
        return QIcon()

    # Render del SVG respetando su alpha
    p = QPainter(pm)
    r.render(p, QRect(0, 0, size.width(), size.height()))
    p.end()

    # Tinte manteniendo alpha
    p = QPainter(pm)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(pm.rect(), color)
    p.end()

    ic = QIcon(pm)
    if not ic.isNull():
        _SVG_TINT_CACHE[key] = ic
    return ic

def themed_qicon(key: str, dark: bool, size: QSize | None = None) -> tuple[QIcon, str]:
    """
    Devuelve un QIcon tematizado. En modo oscuro, si es SVG, lo tiñe de blanco preservando transparencia.
    En modo claro, devuelve el SVG original.
    """
    path = ICONS.get(key, "")
    if path and os.path.exists(path):
        if dark and path.lower().endswith(".svg"):
            sz = size or ICON_SIZE
            try:
                ic = svg_icon_tinted(path, QColor("#FFFFFF"), sz)
                if not ic.isNull():
                    return ic, ""
            except Exception:
                pass  # fallback al ícono normal
        ic = QIcon(path)
        if not ic.isNull():
            return ic, ""
    return _load_icon(key)  # emoji/text fallback

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
POPUP_RIGHT_FIX = 1   # evita “sangrado” a la derecha

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
    "Productos": {
        "create": ["btnProductoNuevo", "btnAceptarProducto"],
        "update": ["btnProductoEditar"],
        "delete": ["btnProductoEliminar"],
    },
    "Ventas": {
        "create": ["btnVentaNueva", "btnAceptarVenta"],
        "update": ["btnVentaEditar"],
        "delete": ["btnVentaEliminar"],
    },
    "Compras": {
        "create": ["btnCompraNueva", "btnAceptarCompra"],
        "update": ["btnCompraEditar"],
        "delete": ["btnCompraEliminar"],
    },
    "Obras": {
        "create": ["btnObraNueva", "btnAceptarObra"],
        "update": ["btnObraEditar"],
        "delete": ["btnObraEliminar"],
    },
    "Clientes": {
        "create": ["btnClienteNuevo", "btnAceptarCliente"],
        "update": ["btnClienteEditar"],
        "delete": ["btnClienteEliminar"],
    },
    "Proveedores": {
        "create": ["btnProveedorNuevo", "btnAceptarProveedor"],
        "update": ["btnProveedorEditar"],
        "delete": ["btnProveedorEliminar"],
    },
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

# ======================= Widgets =======================
class KpiTile(QFrame):
    def __init__(self, title:str, icon:str="📊", accent=None, parent=None):
        super().__init__(parent)
        self.setObjectName("tarjetaDashboard"); self.setProperty("class", "kpiTile")
        if accent == "blue": self.setProperty("accent", "blue")
        lay = QVBoxLayout(self); lay.setContentsMargins(16,14,16,14); lay.setSpacing(6)

        row = QHBoxLayout(); row.setSpacing(10)
        self.icon = QLabel(icon); self.icon.setStyleSheet("font-size:18px; background: transparent;")
        self.title = QLabel(title); self.title.setProperty("role","subtitle")
        self.title.setStyleSheet("background: transparent;")
        row.addWidget(self.icon); row.addWidget(self.title); row.addStretch(1)
        lay.addLayout(row)

        self.value = QLabel("—")
        self.value.setProperty("role", "value")
        self.value.setStyleSheet("font-size:22px; font-weight:800; background: transparent;")
        lay.addWidget(self.value)

        self.note = QLabel(""); self.note.setProperty("role","subtitle")
        self.note.setStyleSheet("background: transparent;")
        lay.addWidget(self.note)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, text:str, note:str=""): self.value.setText(text); self.note.setText(note)

class ChartCard(QFrame):
    def __init__(self, title:str, parent=None):
        super().__init__(parent); self.setObjectName("tarjetaDashboard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout(self); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)
        self.lbl = QLabel(title); self.lbl.setProperty("role","cardtitle")
        self.lbl.setStyleSheet("background: transparent;")
        lay.addWidget(self.lbl)

        self.container = QWidget(self)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cl = QVBoxLayout(self.container); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
        lay.addWidget(self.container, 1)
        self.canvas = None

        self._resize_timer = QTimer(self); self._resize_timer.setSingleShot(True); self._resize_timer.setInterval(50)
        self._resize_timer.timeout.connect(self._redraw)

    def set_figure(self, fig):
        lc = self.container.layout()
        while lc.count():
            item = lc.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lc.addWidget(self.canvas)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if self.canvas:
            self._resize_timer.start()

    def _redraw(self):
        try:
            self.canvas.draw_idle()
        except Exception:
            pass

class ChartCarousel(QFrame):
    def __init__(self, title:str, parent=None, autorotate_ms=7000):
        super().__init__(parent); self.setObjectName("tarjetaDashboard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(8)

        header = QHBoxLayout()
        self.lbl = QLabel(title); self.lbl.setProperty("role","cardtitle")
        self.lbl.setStyleSheet("background: transparent;")
        header.addWidget(self.lbl); header.addStretch(1)
        self.btn_prev = QPushButton("◀"); self.btn_prev.setObjectName("carouselBtn")
        self.btn_next = QPushButton("▶"); self.btn_next.setObjectName("carouselBtn")
        for b in (self.btn_prev, self.btn_next):
            b.setCursor(Qt.PointingHandCursor)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header.addWidget(self.btn_prev); header.addWidget(self.btn_next)
        root.addLayout(header)

        self.stack = QStackedWidget(self); self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.stack, 1)

        self.dots = QLabel("• • •"); self.dots.setAlignment(Qt.AlignCenter); self.dots.setStyleSheet("color:#94A3B8; background: transparent;")
        root.addWidget(self.dots)

        self.btn_prev.clicked.connect(self.prev); self.btn_next.clicked.connect(self.next)
        self.timer = QTimer(self)
        if autorotate_ms:
            self.timer.setInterval(autorotate_ms); self.timer.timeout.connect(self.next); self.timer.start()

        self._resize_timer = QTimer(self); self._resize_timer.setSingleShot(True); self._resize_timer.setInterval(50)
        self._resize_timer.timeout.connect(self._redraw_current)

    def set_figures(self, figures):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w); w.deleteLater()

        for fig in figures:
            w = QWidget()
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            l = QVBoxLayout(w); l.setContentsMargins(0,0,0,0); l.setSpacing(0)
            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            l.addWidget(canvas)
            self.stack.addWidget(w)

        self._update_dots()
        self._redraw_current()

    def _update_dots(self):
        total = self.stack.count(); i = self.stack.currentIndex()
        self.dots.setText(" ".join("●" if k==i else "•" for k in range(total)))

    def next(self):
        if self.stack.count()==0: return
        self.stack.setCurrentIndex((self.stack.currentIndex()+1)%self.stack.count()); self._update_dots(); self._redraw_current()

    def prev(self):
        if self.stack.count()==0: return
        self.stack.setCurrentIndex((self.stack.currentIndex()-1)%self.stack.count()); self._update_dots(); self._redraw_current()

    def resizeEvent(self, ev):
        super().resizeEvent(ev); self._resize_timer.start()

    def _redraw_current(self):
        try:
            current = self.stack.currentWidget()
            if not current: return
            canvas = current.findChild(FigureCanvas)
            if canvas: canvas.draw_idle()
        except Exception:
            pass

# ============================ Popup flotante del chip ============================
class UserMenuPopup(QFrame):
    newUserRequested = Signal()
    themeToggled = Signal(bool)
    deleteAccountRequested = Signal()
    hidden = Signal()  # se emite al ocultarse

    def __init__(self, parent=None, is_admin=False, dark_mode=False):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("userMenuPopup")
        self.setWindowFlag(Qt.NoDropShadowWindowHint, True)
        self._is_admin = is_admin
        self._dark = bool(dark_mode)

        self._rebuild_styles()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 12)
        lay.setSpacing(10)

        # === Nuevo usuario (solo admin) ===
        self.btnNuevo = QPushButton(self)
        ic_plus, _ = themed_qicon("user_add", self._dark)
        if not ic_plus.isNull():
            self.btnNuevo.setIcon(ic_plus)
        self.btnNuevo.setText("  Nuevo usuario")
        self.btnNuevo.clicked.connect(lambda: (self.newUserRequested.emit(), self.close()))
        self.btnNuevo.setVisible(self._is_admin)
        lay.addWidget(self.btnNuevo)

        # === Modo oscuro ===
        row = QHBoxLayout()
        row.setContentsMargins(10, 0, 10, 0)
        row.setSpacing(8)
        row.setAlignment(Qt.AlignVCenter)
        lbl = QLabel("Modo oscuro")
        lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        lbl.setStyleSheet("background: transparent;")
        self.themeSwitch = QCheckBox()
        self.themeSwitch.setObjectName("themeSwitch")
        self.themeSwitch.setChecked(self._dark)
        self.themeSwitch.toggled.connect(self._on_toggle)
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(self.themeSwitch)
        lay.addLayout(row)

        # === Borrar cuenta ===
        self.btnBorrar = QPushButton(self)
        ic_trash, _ = themed_qicon("trash", self._dark)
        if not ic_trash.isNull():
            self.btnBorrar.setIcon(ic_trash)
        self.btnBorrar.setText("  Borrar cuenta")
        self.btnBorrar.clicked.connect(lambda: (self.deleteAccountRequested.emit(), self.close()))
        lay.addWidget(self.btnBorrar)

    # estilos del popup por tema
    def _rebuild_styles(self):
        if self._dark:
            self._closed_stylesheet = """
            #userMenuPopup {
                background:#0B1220; border:1px solid #243147;
                border-radius:12px; padding:8px 0;
            }
            #userMenuPopup QPushButton {
                text-align:left; padding:10px 14px; margin:6px 0; border-radius:8px;
                color:#E5EDFF; background:transparent; border:1px solid transparent; min-height:36px;
            }
            #userMenuPopup QPushButton:hover { background: rgba(56,189,248,.12); }
            QCheckBox#themeSwitch { background:transparent; }
            QCheckBox#themeSwitch::indicator {
                width:40px; height:20px; border-radius:10px; background:#162036; border:1px solid #243147;
            }
            QCheckBox#themeSwitch::indicator:checked { background:#60A5FA; border-color:#60A5FA; }
            """
            self._open_stylesheet = self._closed_stylesheet.replace(
                "border-radius:12px;", "border-bottom-left-radius:12px; border-bottom-right-radius:12px;"
            )
        else:
            self._closed_stylesheet = """
            #userMenuPopup {
                background:#FFFFFF; border:1px solid #E8EEF6;
                border-radius:12px; padding:8px 0;
            }
            #userMenuPopup QPushButton {
                text-align:left; padding:10px 14px; margin:6px 0; border-radius:8px;
                color:#0F172A; background:transparent; border:1px solid transparent; min-height:36px;
            }
            #userMenuPopup QPushButton:hover { background: rgba(41,121,255,.08); }
            QCheckBox#themeSwitch { background:transparent; }
            QCheckBox#themeSwitch::indicator {
                width:40px; height:20px; border-radius:10px; background:#E2E8F0; border:1px solid #CBD5E1;
            }
            QCheckBox#themeSwitch::indicator:checked { background:#2979FF; border-color:#2979FF; }
            """
            self._open_stylesheet = self._closed_stylesheet.replace(
                "border-radius:12px;", "border-bottom-left-radius:12px; border-bottom-right-radius:12px;"
            )
        self.setStyleSheet(self._closed_stylesheet)

    def set_is_admin(self, is_admin: bool):
        self._is_admin = is_admin
        if hasattr(self, "btnNuevo"):
            self.btnNuevo.setVisible(is_admin)

    def set_dark_mode(self, dark: bool):
        if self._dark != bool(dark):
            self._dark = bool(dark)
            self._rebuild_styles()
            if hasattr(self, "themeSwitch"):
                self.themeSwitch.blockSignals(True)
                self.themeSwitch.setChecked(self._dark)
                self.themeSwitch.blockSignals(False)
            # refrescar iconos
            ic_plus, _ = themed_qicon("user_add", self._dark)
            self.btnNuevo.setIcon(ic_plus if not ic_plus.isNull() else QIcon())
            ic_trash, _ = themed_qicon("trash", self._dark)
            self.btnBorrar.setIcon(ic_trash if not ic_trash.isNull() else QIcon())

    def _on_toggle(self, checked: bool):
        self.themeToggled.emit(bool(checked))

    def hideEvent(self, e):
        super().hideEvent(e)
        try:
            self.hidden.emit()
        except Exception:
            pass

# ============================ Main Widget ============================
class MenuPrincipal(QWidget):
    logoutRequested = Signal()
    newUserRequested = Signal()
    themeToggled = Signal(bool)
    deleteAccountRequested = Signal()

    def __init__(self, session: dict | None = None, parent=None):
        super().__init__(parent)
        self.session = session or {}
        self._sidebar_collapsed = False
        self._userMenuPopup = None
        self._current_dark = bool(((self.session or {}).get("user") or {}).get("dark_mode", False))

        self._build_ui()

        # Tema inicial desde session
        self._apply_theme(self._current_dark)

        # Recolocar popup y permitir click en TODO el chip
        self.installEventFilter(self); self.topBar.installEventFilter(self); self.userChip.installEventFilter(self)
        for w in (self.avatarLbl, self.nameLbl, self.roleLbl, self.userChipArrow):
            w.installEventFilter(self)

        self._ensure_perms_loaded()
        self._apply_permissions_global()

        # Hooks
        self.newUserRequested.connect(self._on_new_user_requested)
        self.themeToggled.connect(self._on_theme_toggled)
        self.deleteAccountRequested.connect(self._on_delete_account_requested)

        if self._user_can_dashboard(): self._refresh_inicio_data()
        else: self._blank_inicio()

    # --- Event filter
    def eventFilter(self, obj: QObject, ev: QEvent) -> bool:
        if obj in (getattr(self, "userChip", None), self.avatarLbl, self.nameLbl, self.roleLbl, self.userChipArrow):
            if ev.type() == QEvent.MouseButtonPress and ev.button() == Qt.LeftButton:
                self._toggle_user_menu_popup()
                return True
        if obj in (self, getattr(self, "topBar", None), getattr(self, "userChip", None)):
            if ev.type() in (QEvent.Resize, QEvent.Move, QEvent.Show, QEvent.LayoutRequest):
                self._reposition_user_menu_popup()
        return super().eventFilter(obj, ev)

    def resizeEvent(self, ev):
        super().resizeEvent(ev); self._reposition_user_menu_popup()

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
        tb.addWidget(brandWrap); tb.addStretch(1)

        # Chip
        self.userChip = QFrame(self.topBar)
        self.userChip.setObjectName("userChip")
        self.userChip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.userChip.setMinimumWidth(CHIP_MIN_WIDTH)
        chipL = QHBoxLayout(self.userChip)
        chipL.setContentsMargins(12, 6, 12, 6)
        chipL.setSpacing(8)
        chipL.setAlignment(Qt.AlignCenter)

        self.avatarLbl = QLabel()
        self.avatarLbl.setFixedSize(28, 28)

        self.nameLbl = QLabel(); self.nameLbl.setProperty("role", "name")
        self.roleLbl = QLabel(); self.roleLbl.setProperty("role", "role")

        txtBox = QVBoxLayout()
        txtBox.setContentsMargins(0, 0, 0, 0)
        txtBox.setSpacing(0)
        txtBox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.nameLbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.roleLbl.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        txtBox.addWidget(self.nameLbl); txtBox.addWidget(self.roleLbl)

        self.userChipArrow = QPushButton()
        self.userChipArrow.setObjectName("userChipArrow")
        self.userChipArrow.setCursor(Qt.PointingHandCursor)
        self.userChipArrow.setToolTip("Abrir menú")
        ic_down, fb_down = themed_qicon("chevron_down", False)  # se refresca luego por tema
        if not ic_down.isNull(): self.userChipArrow.setIcon(ic_down)
        else: self.userChipArrow.setText(fb_down or "▾")

        chipL.addWidget(self.avatarLbl, 0, Qt.AlignVCenter)
        chipL.addLayout(txtBox)
        chipL.addWidget(self.userChipArrow, 0, Qt.AlignVCenter)
        tb.addWidget(self.userChip, 0, Qt.AlignRight)

        # Datos del usuario
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

        self.kpi_ventas  = KpiTile("Ventas del mes", "💰", accent="blue")
        self.kpi_compras = KpiTile("Compras del mes", "🧾")
        self.kpi_topprod = KpiTile("Producto más vendido (mes)", "🏆")
        self.kpi_stock   = KpiTile("Stock crítico", "⚠️")

        kpis = QHBoxLayout()
        for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock):
            w.setMinimumHeight(90); kpis.addWidget(w)
        kpis_wrap = QFrame(); kpis_wrap.setLayout(kpis); kpis_wrap.setObjectName("transparent")
        kpis_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dashboard.addWidget(kpis_wrap, 0, 0, 1, 3)

        self.carousel = ChartCarousel("Indicadores: Ventas/Compras/Gastos", autorotate_ms=7000)
        dashboard.addWidget(self.carousel, 1, 0, 1, 2)

        self.card_right = ChartCard("Distribución de gastos por tipo")
        dashboard.addWidget(self.card_right, 1, 2, 1, 1)

        self.weather = DashboardWeatherPanel(); self.weather.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dashboard.addWidget(self.weather, 2, 0, 1, 3)

        dashboard.setColumnStretch(0, 2); dashboard.setColumnStretch(1, 2); dashboard.setColumnStretch(2, 1)
        dashboard.setRowStretch(0, 0); dashboard.setRowStretch(1, 1); dashboard.setRowStretch(2, 0)

        self.stackedWidget.addWidget(self.paginaPrincipal)
        grid.addWidget(self.stackedWidget, 1, 1, 1, 1)

        grid.setRowStretch(0, 0); grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 0); grid.setColumnStretch(1, 1)

        self.rootLayout.addWidget(mainContainer, 0, 0)

        self.menu_buttons["Inicio"].setChecked(True)
        self.stackedWidget.setCurrentWidget(self.paginaPrincipal)

    # -------------------- Tema --------------------
    def _refresh_all_icons(self):
        # Botones de navegación
        for nombre, icon_key, _ in NAV_ITEMS:
            btn = self.menu_buttons.get(nombre)
            if not btn:
                continue
            ic, fb = themed_qicon(icon_key, self._current_dark)
            if not ic.isNull():
                btn.setIcon(ic); btn.setIconSize(ICON_SIZE)
                btn.setText("" if self._sidebar_collapsed else nombre)
            else:
                btn.setIcon(QIcon())
                btn.setText((fb if self._sidebar_collapsed else (f"{fb}  {nombre}" if fb else nombre)) if fb else ("" if self._sidebar_collapsed else nombre))

        # Chevron colapsar/expandir
        che_key = "chevron_right" if self._sidebar_collapsed else "chevron_left"
        ic, fb = themed_qicon(che_key, self._current_dark)
        if not ic.isNull():
            self.botonOcultarMenu.setIcon(ic); self.botonOcultarMenu.setIconSize(ICON_SIZE); self.botonOcultarMenu.setText("")
        else:
            self.botonOcultarMenu.setIcon(QIcon()); self.botonOcultarMenu.setText(fb or "")

        # Icono Logout
        ic, fb = themed_qicon("logout", self._current_dark)
        if not ic.isNull():
            self.logoutBtn.setIcon(ic); self.logoutBtn.setIconSize(ICON_SIZE)
            self.logoutBtn.setText("" if self._sidebar_collapsed else "Logout")
        else:
            self.logoutBtn.setIcon(QIcon())
            self.logoutBtn.setText((fb or "Logout") if not self._sidebar_collapsed else (fb or ""))

        # Flecha del chip (arriba/abajo)
        arrow_key = "chevron_up" if (self._userMenuPopup and self._userMenuPopup.isVisible()) else "chevron_down"
        ic, fb = themed_qicon(arrow_key, self._current_dark)
        if not ic.isNull():
            self.userChipArrow.setIcon(ic); self.userChipArrow.setIconSize(ICON_SIZE); self.userChipArrow.setText("")
        else:
            self.userChipArrow.setIcon(QIcon()); self.userChipArrow.setText(fb or ("▴" if arrow_key=="chevron_up" else "▾"))

        # Íconos del popup (plus/trash)
        if self._userMenuPopup:
            for btn, key in ((getattr(self._userMenuPopup, "btnNuevo", None), "user_add"),
                             (getattr(self._userMenuPopup, "btnBorrar", None), "trash")):
                if btn:
                    ic, _ = themed_qicon(key, self._current_dark)
                    btn.setIcon(ic if not ic.isNull() else QIcon())

    def _apply_theme(self, dark: bool):
        qss = QSS_RODLER_DARK if dark else QSS_RODLER_LIGHT
        QApplication.instance().setStyleSheet(qss)
        self._current_dark = bool(dark)

        # Avatar (azul fijo)
        try:
            display_name, _ = _resolver_user_fields(self.session)
            initial = _initial_from_name(display_name)
            self.avatarLbl.setPixmap(_circle_pix("#2979FF", 28, initial).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception:
            pass

        # Popup: tema y skin
        if self._userMenuPopup is not None:
            try:
                self._userMenuPopup.set_dark_mode(self._current_dark)
                if self._userMenuPopup.isVisible():
                    self._userMenuPopup.setStyleSheet(self._userMenuPopup._open_stylesheet)
                else:
                    self._userMenuPopup.setStyleSheet(self._userMenuPopup._closed_stylesheet)
            except Exception:
                pass

        # Actualizar todos los iconos según el tema
        self._refresh_all_icons()

    # -------------------- Información de usuario --------------------
    def update_user_info(self, session: dict | None = None):
        if session is not None:
            self.session = session
        display_name, role = _resolver_user_fields(self.session)
        self.nameLbl.setText(display_name); self.roleLbl.setText(role)
        initial = _initial_from_name(display_name)
        avatar_pm = _circle_pix("#2979FF", 28, initial)
        self.avatarLbl.setPixmap(avatar_pm.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if self._userMenuPopup is not None:
            roles, _ = _session_roles_perms(self.session)
            self._userMenuPopup.set_is_admin('admin' in roles)
            try:
                self._userMenuPopup.set_dark_mode(self._current_dark)
            except Exception:
                pass

    # -------------------- Popup del chip (overlay) --------------------
    def _ensure_user_menu_popup(self):
        if self._userMenuPopup is None:
            roles, _ = _session_roles_perms(self.session)
            is_admin = ('admin' in roles)
            self._userMenuPopup = UserMenuPopup(parent=self, is_admin=is_admin, dark_mode=self._current_dark)
            self._userMenuPopup.newUserRequested.connect(self.newUserRequested)
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
            popup.close()
            # refrescar estado del ícono flecha
            self._refresh_all_icons()
            return

        # Chip sin esquinas inferiores (se funde con el popup)
        self.userChip.setStyleSheet("#userChip{border-bottom-left-radius:0px;border-bottom-right-radius:0px;}")
        popup.setStyleSheet(popup._open_stylesheet)

        popup.show(); popup.raise_()
        QTimer.singleShot(0, self._finalize_popup_open)
        QTimer.singleShot(1, self._finalize_popup_open)

        # refrescar flecha a "up"
        self._refresh_all_icons()

    def _finalize_popup_open(self):
        self._reposition_user_menu_popup()

    def _on_user_menu_hidden(self):
        try:
            self.userChip.setStyleSheet("")
            if self._userMenuPopup:
                self._userMenuPopup.setStyleSheet(self._userMenuPopup._closed_stylesheet)
        except Exception:
            pass
        # refrescar flecha a "down"
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

        popup.setMinimumWidth(fixed_w)
        popup.setMaximumWidth(fixed_w)

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
        # Guarda preferencia y reemite a listeners externos
        try:
            self.session.setdefault("user", {}); self.session["user"]["dark_mode"] = bool(dark)
        except Exception:
            pass
        self.themeToggled.emit(dark)

    # Señal pública: aplicar el tema realmente
    def _on_theme_toggled(self, dark: bool):
        self._apply_theme(bool(dark))

    # -------------------- Logout --------------------
    def _do_logout(self):
        try:
            self.logoutRequested.emit()
        finally:
            self.close()

    # -------------------- permisos / dashboard --------------------
    def _ensure_perms_loaded(self):
        if (self.session or {}).get("perms"): return
        user = (self.session or {}).get("user") or {}
        username = (user.get("username") or "").strip().lower()
        if not username: return
        try:
            eng = get_engine()
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
            eng = get_engine()
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

        for nombre, btn in self.menu_buttons.items():
            code = PERM_VIEW_BY_MODULE.get(nombre)
            if code: btn.setVisible(_can(roles, perms, code))

        if self.stackedWidget.currentWidget() is None:
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)

    def _blank_inicio(self):
        if getattr(self, "_inicio_blank", False): return
        self._inicio_blank = True
        try:
            for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock, self.carousel, self.card_right, self.weather):
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
        for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock, self.carousel, self.card_right, self.weather):
            try:
                if w: w.setVisible(True)
            except Exception:
                pass
        if hasattr(self, "_lblInicioVacio"): self._lblInicioVacio.setVisible(False)

    # -------------------- permisos por módulo --------------------
    def _apply_permissions_to_module_page(self, nombre_modulo: str, pagina: QWidget):
        roles, perms = _session_roles_perms(self.session)
        actions = PERM_ACTIONS_BY_MODULE.get(nombre_modulo) or {}
        def _grey_disable(widget):
            try: widget.setEnabled(False); widget.setStyleSheet(widget.styleSheet() + "; opacity: 0.6;")
            except Exception: pass

        lacks = {
            "create": not _can(roles, perms, actions.get("create", "")),
            "update": not _can(roles, perms, actions.get("update", "")),
            "delete": not _can(roles, perms, actions.get("delete", "")),
        }

        names_map = ACTION_BUTTONS_BY_MODULE.get(nombre_modulo, {})
        for kind, need in lacks.items():
            if need:
                for obj_name in names_map.get(kind, []):
                    btn = pagina.findChild(QPushButton, obj_name)
                    if btn: _grey_disable(btn)

        for b in pagina.findChildren(QPushButton):
            if not b.isEnabled(): continue
            perm_code = (b.property("perm_code") or "").strip()
            if perm_code and not _can(roles, perms, perm_code): _grey_disable(b)

        for b in pagina.findChildren(QPushButton):
            if not b.isEnabled(): continue
            name = (b.objectName() or "").lower(); text = (b.text() or "").lower()
            if lacks["create"] and (any(k in name for k in ("nuevo","crear","guardar","registrar")) or any(k in text for k in ("nuevo","crear","guardar","registrar"))):
                _grey_disable(b); continue
            if lacks["update"] and (any(k in name for k in ("editar","modificar","actualizar")) or any(k in text for k in ("editar","modificar","actualizar"))):
                _grey_disable(b); continue
            if lacks["delete"] and (any(k in name for k in ("eliminar","borrar","quitar","suprimir")) or any(k in text for k in ("eliminar","borrar","quitar","suprimir"))):
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
        self._refresh_all_icons()   # mantener iconos/textos coherentes

    def toggleMenuLateral(self):
        self._sidebar_collapsed = not self._sidebar_collapsed
        self._apply_sidebar_mode(self._sidebar_collapsed)

    # -------------------- navegación módulos --------------------
    def abrir_modulo(self, nombre_modulo: str):
        roles, perms = _session_roles_perms(self.session)

        if nombre_modulo == "Inicio":
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)
            if self._user_can_dashboard():
                self._ensure_inicio_visible_widgets(); self._refresh_inicio_data()
            else:
                self._blank_inicio()
            return

        view_code = PERM_VIEW_BY_MODULE.get(nombre_modulo)
        if view_code and not _can(roles, perms, view_code):
            return  # sin acceso

        attr = f"pagina_{nombre_modulo}"
        if hasattr(self, attr):
            self.stackedWidget.setCurrentWidget(getattr(self, attr)); return

        clase_modulo = self.modulos[nombre_modulo]
        instancia_modulo = clase_modulo() if clase_modulo is not None else None
        pagina = self.paginaPrincipal if instancia_modulo is None else (QWidget() if hasattr(instancia_modulo, "setupUi") else instancia_modulo)
        if instancia_modulo and hasattr(instancia_modulo, "setupUi"):
            instancia_modulo.setupUi(pagina)
        try:
            pagina.menuPrincipalRef = self
        except Exception:
            pass
        self.stackedWidget.addWidget(pagina)
        setattr(self, attr, pagina)
        self._apply_permissions_to_module_page(nombre_modulo, pagina)
        self.stackedWidget.setCurrentWidget(pagina)

    # -------------------- datos/gráficos --------------------
    def _fmt_currency(self, x: float) -> str:
        return f"Gs. {x:,.0f}".replace(",", ".")

    def _query_month_bounds(self):
        with get_engine().connect() as con:
            row = con.execute(text("""
                SELECT date_trunc('month', CURRENT_DATE)::date AS ini,
                       (date_trunc('month', CURRENT_DATE) + interval '1 month')::date AS fin
            """)).mappings().first()
            return row['ini'], row['fin']

    def _refresh_inicio_data(self):
        ini, fin = self._query_month_bounds()
        eng = get_engine()
        with eng.connect() as con:
            ventas = con.execute(text("""
                SELECT COALESCE(SUM(total_venta),0)
                FROM ventas WHERE fecha_venta >= :ini AND fecha_venta < :fin
            """), {'ini': ini, 'fin': fin}).scalar() or 0

            compras = con.execute(text("""
                SELECT COALESCE(SUM(total_compra),0)
                FROM compras WHERE fecha >= :ini AND fecha < :fin
            """), {'ini': ini, 'fin': fin}).scalar() or 0

            top_row = con.execute(text("""
                SELECT p.nombre, COALESCE(SUM(vd.cantidad),0) AS u
                FROM ventas_detalle vd
                JOIN ventas v  ON v.id_venta = vd.id_venta
                JOIN productos p ON p.id_producto = vd.id_producto
                WHERE v.fecha_venta >= :ini AND v.fecha_venta < :fin
                GROUP BY p.nombre
                ORDER BY u DESC
                LIMIT 1
            """), {'ini': ini, 'fin': fin}).mappings().first()

            crit = con.execute(text("SELECT COUNT(*) FROM productos WHERE stock_actual <= stock_minimo")).scalar() or 0

        self.kpi_ventas.set_value(self._fmt_currency(ventas), "Total vendido")
        self.kpi_compras.set_value(self._fmt_currency(compras), "Total comprado")
        if top_row:
            self.kpi_topprod.set_value(f"{top_row['nombre']}", f"{int(top_row['u'])} u. vendidas")
        else:
            self.kpi_topprod.set_value("—", "Sin ventas en el mes")
        self.kpi_stock.set_value(str(crit), "productos en nivel crítico")

        figs = [
            create_ventas_vs_compras_mensuales(meses=12),
            create_gastos_mensuales(meses=12),
            create_presupuesto_vs_gasto_por_obra(top_n=10),
            create_top_materiales_mes(dias=30, limit=10),
            create_stock_critico(limit=10),
        ]
        self.carousel.set_figures(figs)
        self.card_right.set_figure(create_distribucion_gastos_por_tipo())
        self.weather.refresh_default_city()

    # ===== Stubs =====
    def _on_new_user_requested(self): pass
    def _on_delete_account_requested(self): pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuPrincipal()
    window.show()
    sys.exit(app.exec())
