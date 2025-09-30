# MenuPrincipal.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QPropertyAnimation, Signal, QTimer, QSize, QFile
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QPen, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton,
    QStackedWidget, QButtonGroup, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect
)

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

# ================= Tema (estilo del mock) =================
QSS_RODLER = """
/* Paleta/Tipografía base */
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background: #F5F7FB; }
QLabel { background: transparent; }
:disabled { color: #9AA4B2; }

/* -------------------- Sidebar -------------------- */
#sidebar { background:#FFFFFF; border-right:1px solid #E8EEF6; }
#sidebarHeader { background: transparent; border: none; }

QPushButton[nav="true"] {
  text-align: left; padding: 10px 12px; border-radius: 10px;
  background: transparent; border: 1px solid transparent; color: #0F172A;
}
QPushButton[nav="true"]::menu-indicator { image: none; }
QPushButton[nav="true"]:hover { background: rgba(41,121,255,.08); }
QPushButton[nav="true"]:checked {
  background: rgba(41,121,255,.15); border: 1px solid #90CAF9; color: #0F172A;
}

/* Botón Logout (pegado abajo) */
#logoutBtn {
  background: #EEF2FF; border:1px solid #E8EEF6; color:#1E293B;
  border-radius: 10px; padding: 8px 10px;
}
#logoutBtn:hover { background:#E0E7FF; border-color:#C7D2FE; }

/* Toggle Sidebar */
#toggleSidebarBtn {
  background: transparent; border:1px solid transparent; border-radius:10px;
  padding:6px 8px; font-size:16px;
}
#toggleSidebarBtn:hover { background: rgba(41,121,255,.08); }

/* -------------------- TopBar -------------------- */
#topBar { background:#FFFFFF; border-bottom:1px solid #E8EEF6; }
#brand QLabel#appTitle { font-size:28px; font-weight:800; color:#0F172A; background: transparent; }
#brand QLabel#appSub { color:#94A3B8; font-size:11px; background: transparent; }

#userChip {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:14px; padding:6px 10px;
}
#userChip QLabel[role="name"] { font-weight:600; }
#userChip QLabel[role="role"] { color:#94A3B8; font-size:11px; }

/* -------------------- Cards del dashboard -------------------- */
#tarjetaDashboard { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px; }
#tarjetaDashboard:hover { border:1px solid #90CAF9; }
#tarjetaDashboard QLabel[role="cardtitle"] { font-size:14px; font-weight:700; color:#0F172A; }

/* KPI tiles */
.kpiTile { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px; }
.kpiTile[accent="blue"] { background: linear-gradient(135deg,#2979FF 0%, #5EA8FF 100%); }
.kpiTile[accent="blue"] QLabel, .kpiTile[accent="blue"] QFrame { color:#FFFFFF; }
.kpiTile QLabel[role="subtitle"] { color:#94A3B8; }

/* Botones prev/next del carrusel */
#carouselBtn {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:8px; padding:4px 8px;
}
#carouselBtn:hover { border-color:#90CAF9; background:#F8FAFF; }

/* -------------------- Weather (chips/días) -------------------- */
#hourChip { border:1px solid #E8EEF6; border-radius:10px; padding:6px 8px; }
"""

# ---------------- Iconos ----------------
ICONS_BASE = r"C:\Users\mauri\OneDrive\Desktop\sistema-informatico\rodlerIcons"

ICONS = {
    "inicio":        os.path.join(ICONS_BASE, "home.svg"),
    "productos":     os.path.join(ICONS_BASE, "box.svg"),
    "ventas":        os.path.join(ICONS_BASE, "receipt.svg"),
    "compras":       os.path.join(ICONS_BASE, "cart.svg"),
    "obras":         os.path.join(ICONS_BASE, "crane.svg"),
    "clientes":      os.path.join(ICONS_BASE, "users.svg"),
    "proveedores":   os.path.join(ICONS_BASE, "store.svg"),
    "logout":        os.path.join(ICONS_BASE, "logout.svg"),
    "chevron_left":  os.path.join(ICONS_BASE, "chevron-left.svg"),
    "chevron_right": os.path.join(ICONS_BASE, "chevron-right.svg"),
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
    }.get(key, "")
    return QIcon(), fallback_txt


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
    if first or last: display = f"{first} {last}".strip()
    elif username:    display = username
    else:             display = "Usuario"
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
        self.icon = QLabel(icon); self.icon.setStyleSheet("font-size:18px;")
        self.title = QLabel(title); self.title.setProperty("role","subtitle")
        row.addWidget(self.icon); row.addWidget(self.title); row.addStretch(1)
        lay.addLayout(row)

        self.value = QLabel("—"); self.value.setStyleSheet("font-size:22px; font-weight:800;")
        lay.addWidget(self.value)

        self.note = QLabel(""); self.note.setProperty("role","subtitle")
        lay.addWidget(self.note)

        eff = QGraphicsDropShadowEffect(self); eff.setBlurRadius(18); eff.setOffset(0,2); eff.setColor(QColor("#E6EDF9"))
        self.setGraphicsEffect(eff)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, text:str, note:str=""): self.value.setText(text); self.note.setText(note)

class ChartCard(QFrame):
    def __init__(self, title:str, parent=None):
        super().__init__(parent)
        self.setObjectName("tarjetaDashboard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout(self); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)
        self.lbl = QLabel(title); self.lbl.setProperty("role","cardtitle"); lay.addWidget(self.lbl)

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

        self.dots = QLabel("• • •"); self.dots.setAlignment(Qt.AlignCenter); self.dots.setStyleSheet("color:#94A3B8;")
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
        super().resizeEvent(ev)
        self._resize_timer.start()

    def _redraw_current(self):
        try:
            current = self.stack.currentWidget()
            if not current: return
            canvas = current.findChild(FigureCanvas)
            if canvas: canvas.draw_idle()
        except Exception:
            pass

# ============================ Main Widget ============================
class MenuPrincipal(QWidget):
    """Dashboard Rodler con estilo del mock (sin buscador, sin notificaciones)."""
    logoutRequested = Signal()

    def __init__(self, session: dict | None = None, parent=None):
        super().__init__(parent)
        self.session = session or {}
        self._sidebar_collapsed = False
        self._build_ui()
        self.setStyleSheet(QSS_RODLER)
        self._refresh_inicio_data()

    def update_user_info(self, session: dict | None = None):
        if session is not None:
            self.session = session
        display_name, role = _resolver_user_fields(self.session)
        self.nameLbl.setText(display_name)
        self.roleLbl.setText(role)
        initial = _initial_from_name(display_name)
        self.avatarLbl.setPixmap(
            _circle_pix("#2979FF", 28, initial).scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def _do_logout(self):
        try:
            self.logoutRequested.emit()
        finally:
            self.close()

    # -------------------- construcción UI --------------------
    def _build_ui(self):
        self.rootLayout = QGridLayout(self); self.rootLayout.setContentsMargins(0,0,0,0); self.rootLayout.setSpacing(0)

        mainContainer = QWidget(self)
        mainContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid = QGridLayout(mainContainer); grid.setContentsMargins(0,0,0,0); grid.setSpacing(0)

        # --- TOP BAR ---
        self.topBar = QWidget(mainContainer); self.topBar.setObjectName("topBar")
        self.topBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tb = QHBoxLayout(self.topBar); tb.setContentsMargins(16,10,16,10); tb.setSpacing(10)

        brandWrap = QFrame(self.topBar); brandWrap.setObjectName("brand")
        brandWrap.setStyleSheet("background: transparent; border: none;")
        brandWrap.setFrameShape(QFrame.NoFrame)
        brandWrap.setGraphicsEffect(None)

        brandL = QVBoxLayout(brandWrap); brandL.setContentsMargins(0,0,0,0)

        self.appTitle = QLabel("Rodler")
        self.appTitle.setObjectName("appTitle")
        self.appTitle.setStyleSheet("background: transparent;")
        brandL.addWidget(self.appTitle)

        tb.addWidget(brandWrap); tb.addStretch(1)

        # --- USER CHIP ---
        self.userChip = QFrame(self.topBar); self.userChip.setObjectName("userChip")
        self.userChip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        chipL = QHBoxLayout(self.userChip); chipL.setContentsMargins(8,4,8,4); chipL.setSpacing(8)

        self.avatarLbl = QLabel()
        self.nameLbl   = QLabel(); self.nameLbl.setProperty("role","name")
        self.roleLbl   = QLabel(); self.roleLbl.setProperty("role","role")

        txtBox = QVBoxLayout(); txtBox.setContentsMargins(0,0,0,0)
        txtBox.addWidget(self.nameLbl); txtBox.addWidget(self.roleLbl)

        chipL.addWidget(self.avatarLbl); chipL.addLayout(txtBox)
        self.update_user_info(self.session)

        tb.addWidget(self.userChip)
        grid.addWidget(self.topBar, 0, 0, 1, 2)

        # --- SIDEBAR ---
        self.menuLateral = QFrame(mainContainer); self.menuLateral.setObjectName("sidebar")
        self.menuLateral.setMaximumWidth(EXPANDED_WIDTH); self.menuLateral.setMinimumWidth(0)
        self.menuLateral.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.animation_sidebar = QPropertyAnimation(self.menuLateral, b"maximumWidth"); self.animation_sidebar.setDuration(220)

        sb = QVBoxLayout(self.menuLateral); sb.setContentsMargins(12,12,12,12); sb.setSpacing(10)

        header = QFrame(self.menuLateral); header.setObjectName("sidebarHeader")
        hLay = QHBoxLayout(header); hLay.setContentsMargins(0,0,0,0)
        hLay.addSpacerItem(QSpacerItem(1,1,QSizePolicy.Expanding,QSizePolicy.Minimum))

        che_left, fb_l = _load_icon("chevron_left")
        self.botonOcultarMenu = QPushButton(fb_l if che_left.isNull() else "")
        self.botonOcultarMenu.setIcon(che_left if not che_left.isNull() else QIcon())
        self.botonOcultarMenu.setIconSize(ICON_SIZE)
        self.botonOcultarMenu.setObjectName("toggleSidebarBtn")
        self.botonOcultarMenu.setCursor(Qt.PointingHandCursor); self.botonOcultarMenu.setToolTip("Colapsar menú")
        self.botonOcultarMenu.clicked.connect(self.toggleMenuLateral)
        hLay.addWidget(self.botonOcultarMenu)
        sb.addWidget(header)

        self.btn_group = QButtonGroup(self); self.btn_group.setExclusive(True)
        self.menu_buttons = {}; self.modulos = {}

        def _make_nav_button(nombre: str, icon_key: str):
            icon, fb = _load_icon(icon_key)
            btn = QPushButton(nombre if icon.isNull() else nombre)
            btn.setCheckable(True)
            btn.setProperty("nav", True); btn.setProperty("mini", False)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(36)
            if not icon.isNull():
                btn.setIcon(icon); btn.setIconSize(ICON_SIZE)
            else:
                btn.setText(f"{fb}  {nombre}" if fb else nombre)
            return btn

        for nombre, icon_key, clase in NAV_ITEMS:
            self.modulos[nombre] = clase
            btn = _make_nav_button(nombre, icon_key)
            btn.clicked.connect(lambda checked, m=nombre: self.abrir_modulo(m))
            sb.addWidget(btn); self.btn_group.addButton(btn); self.menu_buttons[nombre] = btn

        sb.addStretch(1)

        # Logout
        lg_icon, lg_fb = _load_icon("logout")
        self.logoutBtn = QPushButton("Logout" if lg_icon.isNull() else "Logout")
        self.logoutBtn.setObjectName("logoutBtn")
        self.logoutBtn.setCursor(Qt.PointingHandCursor)
        if not lg_icon.isNull():
            self.logoutBtn.setIcon(lg_icon); self.logoutBtn.setIconSize(ICON_SIZE)
        else:
            if lg_fb: self.logoutBtn.setText(f"{lg_fb}  Logout")
        self.logoutBtn.setToolTip("Cerrar sesión")
        self.logoutBtn.clicked.connect(self._do_logout)
        sb.addWidget(self.logoutBtn)

        grid.addWidget(self.menuLateral, 1, 0, 1, 1)

        # --- STACK CONTENIDO ---
        self.stackedWidget = QStackedWidget(mainContainer)
        self.stackedWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ======== Dashboard (Inicio) ========
        self.paginaPrincipal = QWidget()
        self.paginaPrincipal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        dashboard = QGridLayout(self.paginaPrincipal); dashboard.setContentsMargins(16,16,16,16)
        dashboard.setHorizontalSpacing(12); dashboard.setVerticalSpacing(12)

        self.kpi_ventas  = KpiTile("Ventas del mes", "💰", accent="blue")
        self.kpi_compras = KpiTile("Compras del mes", "🧾")
        self.kpi_topprod = KpiTile("Producto más vendido (mes)", "🏆")
        self.kpi_stock   = KpiTile("Stock crítico", "⚠️")

        kpis = QHBoxLayout()
        for w in (self.kpi_ventas, self.kpi_compras, self.kpi_topprod, self.kpi_stock):
            w.setMinimumHeight(90)
            kpis.addWidget(w)
        kpis_wrap = QFrame(); kpis_wrap.setLayout(kpis); kpis_wrap.setObjectName("transparent")
        kpis_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        dashboard.addWidget(kpis_wrap, 0, 0, 1, 3)

        self.carousel = ChartCarousel("Indicadores: Ventas/Compras/Gastos", autorotate_ms=7000)
        dashboard.addWidget(self.carousel, 1, 0, 1, 2)

        # ⬇️ TÍTULO ACTUALIZADO: ahora la tarjeta derecha muestra el gráfico de torta
        self.card_right = ChartCard("Distribución de gastos por tipo")
        dashboard.addWidget(self.card_right, 1, 2, 1, 1)

        self.weather = DashboardWeatherPanel()
        self.weather.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

    # -------------------- comportamiento --------------------
    def _apply_sidebar_mode(self, collapsed: bool):
        if collapsed:
            for nombre, icon_key, _ in NAV_ITEMS:
                btn = self.menu_buttons[nombre]
                btn.setProperty("mini", True)
                btn.setToolTip(nombre)
                icon, fb = _load_icon(icon_key)
                if not icon.isNull():
                    btn.setText(""); btn.setIcon(icon); btn.setIconSize(ICON_SIZE)
                else:
                    btn.setText(fb)
                btn.style().unpolish(btn); btn.style().polish(btn)

            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth()); self.animation_sidebar.setEndValue(COLLAPSED_WIDTH)

            che_right, fb_r = _load_icon("chevron_right")
            self.botonOcultarMenu.setIcon(che_right if not che_right.isNull() else QIcon())
            self.botonOcultarMenu.setText(fb_r if che_right.isNull() else "")
            self.botonOcultarMenu.setToolTip("Expandir menú")

            lg_icon, lg_fb = _load_icon("logout")
            if not lg_icon.isNull():
                self.logoutBtn.setText(""); self.logoutBtn.setIcon(lg_icon); self.logoutBtn.setIconSize(ICON_SIZE)
            else:
                self.logoutBtn.setText(lg_fb or "⎋")
            self.logoutBtn.setToolTip("Cerrar sesión")

        else:
            for nombre, icon_key, _ in NAV_ITEMS:
                btn = self.menu_buttons[nombre]
                btn.setProperty("mini", False)
                btn.setToolTip("")
                icon, fb = _load_icon(icon_key)
                if not icon.isNull():
                    btn.setIcon(icon); btn.setIconSize(ICON_SIZE); btn.setText(nombre)
                else:
                    btn.setText(f"{fb}  {nombre}" if fb else nombre)
                btn.style().unpolish(btn); btn.style().polish(btn)

            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth()); self.animation_sidebar.setEndValue(EXPANDED_WIDTH)

            che_left, fb_l = _load_icon("chevron_left")
            self.botonOcultarMenu.setIcon(che_left if not che_left.isNull() else QIcon())
            self.botonOcultarMenu.setText(fb_l if che_left.isNull() else "")
            self.botonOcultarMenu.setToolTip("Colapsar menú")

            lg_icon, lg_fb = _load_icon("logout")
            if not lg_icon.isNull():
                self.logoutBtn.setIcon(lg_icon); self.logoutBtn.setIconSize(ICON_SIZE); self.logoutBtn.setText("Logout")
            else:
                self.logoutBtn.setText(f"{lg_fb}  Logout" if lg_fb else "Logout")
            self.logoutBtn.setToolTip("Cerrar sesión")

        self.animation_sidebar.start()

    def toggleMenuLateral(self):
        self._sidebar_collapsed = not getattr(self, "_sidebar_collapsed", False)
        self._apply_sidebar_mode(self._sidebar_collapsed)

    def abrir_modulo(self, nombre_modulo: str):
        if nombre_modulo == "Inicio":
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)
            self._refresh_inicio_data()
            return
        if hasattr(self, f"pagina_{nombre_modulo}") and self.stackedWidget.currentWidget() == getattr(self, f"pagina_{nombre_modulo}"):
            return
        if not hasattr(self, f"pagina_{nombre_modulo}"):
            clase_modulo = self.modulos[nombre_modulo]; instancia_modulo = clase_modulo() if clase_modulo is not None else None
            if instancia_modulo is None: pagina = self.paginaPrincipal
            else:
                if hasattr(instancia_modulo, "setupUi"): pagina = QWidget(); instancia_modulo.setupUi(pagina)
                else: pagina = instancia_modulo
                self.stackedWidget.addWidget(pagina)
            setattr(self, f"pagina_{nombre_modulo}", pagina)
        self.stackedWidget.setCurrentWidget(getattr(self, f"pagina_{nombre_modulo}"))

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

        # ⬇️ Ahora el carrusel incluye 'Materiales más usados' y la tarjeta derecha el gráfico de torta
        figs = [
            create_ventas_vs_compras_mensuales(meses=12),
            create_gastos_mensuales(meses=12),
            create_presupuesto_vs_gasto_por_obra(top_n=10),
            create_top_materiales_mes(dias=30, limit=10),           # <— movido al carrusel
            create_stock_critico(limit=10),
        ]
        self.carousel.set_figures(figs)

        # Gráfico de torta en el widget derecho
        self.card_right.set_figure(create_distribucion_gastos_por_tipo())

        self.weather.refresh_default_city()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MenuPrincipal()
    window.show()
    sys.exit(app.exec())
