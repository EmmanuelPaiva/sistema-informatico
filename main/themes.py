import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget, QApplication

# =========================================================
#  FUNCIONES PÚBLICAS
# =========================================================
def apply_theme(widget: QWidget, dark: bool) -> None:
    """Apply Rodler theme (light/dark) to the given widget or app."""
    qss = QSS_RODLER_DARK if dark else QSS_RODLER_LIGHT
    if isinstance(widget, QApplication):
        widget.setStyleSheet(qss)
    else:
        widget.setStyleSheet(qss)
    try:
        app = QApplication.instance()
        if app:
            app.setProperty("appTheme", "dark" if dark else "light")
    except Exception:
        pass


def is_dark_mode() -> bool:
    """Return True if the app is currently in dark mode."""
    app = QApplication.instance()
    if not app:
        return False
    prop = app.property("appTheme")
    if isinstance(prop, str):
        return prop.lower() == "dark"
    try:
        return (app.styleSheet() == QSS_RODLER_DARK)
    except Exception:
        return False


# Icons helpers (light/dark)
_SVG_TINT_CACHE = {}

def _svg_icon_tinted(svg_path: str, color: QColor, size: QSize) -> QIcon:
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

    p = QPainter(pm)
    r.render(p, QRect(0, 0, size.width(), size.height()))
    p.end()

    p = QPainter(pm)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(pm.rect(), color)
    p.end()

    ic = QIcon(pm)
    if not ic.isNull():
        _SVG_TINT_CACHE[key] = ic
    return ic


def _icons_base_dir() -> Path:
    # 1) relative to this file
    this_dir = Path(__file__).resolve().parent
    rel = (this_dir / ".." / "rodlerIcons").resolve()
    if rel.is_dir():
        return rel
    # 2) absolute fallback (project desktop path)
    abs_fallback = Path(r"C:\Users\mauri\OneDrive\Desktop\sistema-informatico\rodlerIcons")
    if abs_fallback.is_dir():
        return abs_fallback
    # 3) cwd fallback
    return Path.cwd()


def themed_icon(name: str, dark: bool | None = None, size: QSize | None = None) -> QIcon:
    """Return QIcon by name from 'rodlerIcons', tinted white in dark mode."""
    if dark is None:
        dark = is_dark_mode()
    size = size or QSize(18, 18)
    base = _icons_base_dir()
    svg = (base / f"{name}.svg")
    if svg.is_file():
        if dark:
            ic = _svg_icon_tinted(str(svg), QColor("#FFFFFF"), size)
            if not ic.isNull():
                return ic
        return QIcon(str(svg))
    png = (base / f"{name}.png")
    return QIcon(str(png)) if png.is_file() else QIcon()


    
# =========================
#  RODLER THEME DEFINITIONS
# =========================

QSS_RODLER_LIGHT = """
/* ================== PALETA BASE (LIGHT) ================== */
* { font-family: "Poppins", "Inter", "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:14px; }
QWidget { background:#F5F7FB; }
QLabel { background: transparent; }
:disabled { color:#9AA4B2; }

/* ============== MENU PRINCIPAL / SIDEBAR ============== */
#sidebar { background:#FFFFFF; border-right:1px solid #E8EEF6; }
#sidebarHeader { background: transparent; border: none; }

QPushButton[nav="true"] {
  text-align:left; padding:10px 12px; border-radius:10px;
  background:transparent; border:1px solid transparent; color:#0F172A;
  font-size:14px;
}
QPushButton[nav="true"]::menu-indicator { image:none; }
QPushButton[nav="true"]:hover { background:rgba(41,121,255,.08); }
QPushButton[nav="true"]:checked {
  background:rgba(41,121,255,.15);
  border:1px solid #90CAF9;
}

#logoutBtn {
  background:#EEF2FF; border:1px solid #E8EEF6; color:#1E293B;
  border-radius:10px; padding:8px 10px; font-size:14px;
}
#logoutBtn:hover { background:#E0E7FF; border-color:#C7D2FE; }

#toggleSidebarBtn {
  background:transparent; border:1px solid transparent; border-radius:10px;
  padding:6px 8px; font-size:18px;
}
#toggleSidebarBtn:hover { background:rgba(41,121,255,.08); }

/* =================== TOPBAR & CHIP =================== */
#topBar { background:#FFFFFF; border-bottom:1px solid #E8EEF6; }
#brand QLabel#appTitle {
  font-size:32px; font-weight:900; color:#0F172A; background:transparent;
  letter-spacing:1px; qproperty-text: "RODLER";
}
#brand QLabel#appSub { color:#94A3B8; font-size:12px; background:transparent; }

#userChip {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:14px; padding:8px 12px;
}
#userChip QLabel[role="name"] { font-weight:600; font-size:14px; }
#userChip QLabel[role="role"] { color:#94A3B8; font-size:12px; }
#userChipArrow { border:none; padding:2px 4px; background:transparent; }
#userChipArrow:hover { background:transparent; }

/* ======= POPUP DEL CHIP (botón nuevo usuario / switch / borrar) ======= */
#userMenuPopup {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:12px;
}
#userMenuPopup QPushButton {
  text-align:left; padding:10px 12px; margin:6px 0; border-radius:8px;
  background:transparent; color:#0F172A; border:1px solid transparent; min-height:36px; font-size:14px;
}
#userMenuPopup QPushButton:hover { background:rgba(41,121,255,.06); }

/* Switch de tema (unchecked gris - checked azul) */
QCheckBox#themeSwitch { background:transparent; }
QCheckBox#themeSwitch::indicator {
  width:40px; height:20px; border-radius:10px;
  background:#E2E8F0; border:1px solid #CBD5E1;
}
QCheckBox#themeSwitch::indicator:checked {
  background:#2979FF; border-color:#2979FF;
}

/* =================== DASHBOARD / CARDS =================== */
#tarjetaDashboard { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px; }
#tarjetaDashboard:hover { border:1px solid #90CAF9; }
#tarjetaDashboard QLabel[role="cardtitle"] { font-size:16px; font-weight:700; color:#0F172A; }
QLabel[role="pageTitle"] { font-size:20px; font-weight:800; color:#0F172A; }

/* KPI tiles */
QFrame#tarjetaDashboard[class="kpiTile"] { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px; }
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] {
  background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2979FF, stop:1 #5EA8FF);
}
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QLabel,
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QFrame { color:#FFFFFF; }
QFrame#tarjetaDashboard[class="kpiTile"] QLabel[role="subtitle"] { color:#94A3B8; font-size:13px; }
QFrame#tarjetaDashboard[class="kpiTile"] QLabel[role="value"] { font-size:24px; font-weight:800; }

/* Carousel */
#carouselBtn { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:8px; padding:4px 8px; font-size:14px; }
#carouselBtn:hover { border-color:#90CAF9; background:#F8FAFF; }

/* Weather chips */
#hourChip { border:1px solid #E8EEF6; border-radius:10px; padding:6px 8px; }

/* =================== CARDS GENERALES (módulos) =================== */
#card, #headerCard, #tableCard, .card, QTableWidget, QTreeWidget {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px;
}
.card:hover { border-color:#90CAF9; }

/* Pills & muted */
QLabel[pill="true"] {
  background:#F1F5F9; border:1px solid #E8EEF6; border-radius:9px;
  padding:4px 10px; font-weight:600; color:#334155; font-size:13px;
}
QLabel[muted="true"] { color:#64748B; font-size:13px; }

/* Etiquetas de campos / hints */
QLabel[role="fieldLabel"] { font-weight:600; color:#0F172A; margin-bottom:4px; font-size:14px; }
QLabel[role="hint"] { color:#64748B; font-size:13px; }

/* =================== INPUTS =================== */
QLineEdit, QComboBox, QDateEdit, QDateTimeEdit, QDoubleSpinBox, QTextEdit {
  background:#F1F5F9; border:1px solid #E8EEF6; border-radius:10px; padding:8px 12px; min-height:30px; font-size:14px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
  border:1px solid #90CAF9; background:#FFFFFF;
}

/* Buscador */
QLineEdit#searchBox {
  background:#F1F5F9; border:1px solid #E8EEF6; border-radius:10px; padding:10px 14px; font-size:14px;
}
QLineEdit#searchBox:focus { border-color:#90CAF9; }

/* =================== BOTONES =================== */
QPushButton[type="primary"] {
  background:#2979FF; border:1px solid #2979FF; color:#FFFFFF;
  border-radius:10px; padding:9px 14px; qproperty-iconSize: 20px 20px; font-size:14px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

QPushButton[type="secondary"] {
  background:#FFFFFF; border:1px solid #E8EEF6; color:#0F172A;
  border-radius:10px; padding:8px 16px; min-height:30px; font-size:14px;
}
QPushButton[type="secondary"]:hover { border-color:#CFE0F5; }

QPushButton[type="danger"] {
  background:#EF5350; border:1px solid #EF5350; color:#FFFFFF;
  border-radius:8px; padding:7px 12px; min-height:30px; font-size:13px;
}
QPushButton[type="danger"]:hover { background:#f26461; }

QPushButton[role="iconSmall"] {
  min-width:28px; max-width:34px; min-height:28px; padding:0; font-size:18px; font-weight:700;
}

/* Icon-only (editar/eliminar en cards, toolbuttons) */
QToolButton[type="icon"], QPushButton[type="icon"] {
  background:transparent; border:none; color:#64748B; padding:6px; border-radius:8px; qproperty-iconSize: 20px 20px; font-size:16px;
}
QToolButton[type="icon"]:hover, QPushButton[type="icon"]:hover {
  background:rgba(41,121,255,.10); color:#0F172A;
}
QPushButton[type="icon"][variant="edit"], QToolButton[type="icon"][variant="edit"] {
  background:#D6E4FF; color:#0B63F6;
}
QPushButton[type="icon"][variant="edit"]:hover, QToolButton[type="icon"][variant="edit"]:hover {
  background:#C7DAFF; color:#0847C5;
}
QPushButton[type="icon"][variant="delete"], QToolButton[type="icon"][variant="delete"] {
  background:#FFE4E6; color:#E11D48;
}
QPushButton[type="icon"][variant="delete"]:hover, QToolButton[type="icon"][variant="delete"]:hover {
  background:#FFD5D9; color:#B91C1C;
}

/* =================== TABLAS / LISTAS =================== */
QHeaderView::section {
  background:#F8FAFF; color:#0F172A; padding:12px; border:none; border-right:1px solid #E8EEF6; font-size:14px;
}
QTableWidget {
  gridline-color:#E8EEF6; selection-background-color:rgba(41,121,255,.15); selection-color:#0F172A; border:none;
}
QTableWidget::item { padding:8px; font-size:14px; }
QTreeWidget {
  selection-background-color:rgba(41,121,255,.15); selection-color:#0F172A;
  border:1px solid #E8EEF6; border-radius:16px;
}
/* hijos transparentes dentro de celdas */
QTableWidget QWidget, QTreeWidget QWidget { background:transparent; border:none; }

/* ======== Form específico: GastoForm (borde azul suave) ======== */
#GastoFormFrame {
  background:#FFFFFF; border:1px solid #0097e6; border-radius:10px;
}
/* Contenedores marcados como 'transparent' para remover cualquier fondo/sombra */
QFrame#transparent, QWidget#transparent { background: transparent; border: none; }
"""

QSS_RODLER_DARK = """
/* ================== PALETA BASE (DARK) ================== */
* { font-family:"Poppins", "Inter", "Segoe UI", Arial, sans-serif; color:#E5E7EB; font-size:14px; }
QWidget { background:#0B1220; }
QLabel { background:transparent; }
:disabled { color:#6B7280; }

/* ============== MENU PRINCIPAL / SIDEBAR ============== */
#sidebar { background:#0F172A; border-right:1px solid #1F2A44; }
#sidebarHeader { background:transparent; border:none; }

QPushButton[nav="true"] {
  text-align:left; padding:10px 12px; border-radius:10px;
  background:transparent; border:1px solid transparent; color:#E5E7EB; font-size:14px;
}
QPushButton[nav="true"]::menu-indicator { image:none; }
QPushButton[nav="true"]:hover { background:rgba(41,121,255,.12); }
QPushButton[nav="true"]:checked {
  background:rgba(41,121,255,.18);
  border:1px solid #60A5FA;
}

#logoutBtn {
  background:#111B2E; border:1px solid #1F2A44; color:#D1D5DB;
  border-radius:10px; padding:8px 10px; font-size:14px;
}
#logoutBtn:hover { background:#12203A; border-color:#27456F; }

#toggleSidebarBtn {
  background:transparent; border:1px solid transparent; border-radius:10px;
  padding:6px 8px; font-size:18px; color:#E5E7EB;
}
#toggleSidebarBtn:hover { background:rgba(41,121,255,.12); }

/* =================== TOPBAR & CHIP =================== */
#topBar { background:#0F172A; border-bottom:1px solid #1F2A44; }
#brand QLabel#appTitle {
  font-size:32px; font-weight:900; color:#E5E7EB; background:transparent;
  letter-spacing:1px; qproperty-text: "RODLER";
}
#brand QLabel#appSub { color:#9CA3AF; font-size:12px; background:transparent; }

#userChip {
  background:#0F172A; border:1px solid #1F2A44; border-radius:14px; padding:8px 12px;
}
#userChip QLabel[role="name"] { font-weight:600; color:#E5E7EB; font-size:14px; }
#userChip QLabel[role="role"] { color:#9CA3AF; font-size:12px; }
#userChipArrow { border:none; padding:2px 4px; background:transparent; color:#E5E7EB; }
#userChipArrow:hover { background:transparent; }

/* ======= POPUP DEL CHIP ======= */
#userMenuPopup {
  background:#0F172A; border:1px solid #1F2A44; border-radius:12px;
}
#userMenuPopup QPushButton {
  text-align:left; padding:10px 12px; margin:6px 0; border-radius:8px;
  background:transparent; color:#E5E7EB; border:1px solid transparent; min-height:36px; font-size:14px;
}
#userMenuPopup QPushButton:hover { background:rgba(41,121,255,.12); }

/* Switch de tema en dark */
QCheckBox#themeSwitch { background:transparent; }
QCheckBox#themeSwitch::indicator {
  width:40px; height:20px; border-radius:10px;
  background:#1E293B; border:1px solid #334155;
}
QCheckBox#themeSwitch::indicator:checked {
  background:#2979FF; border-color:#2979FF;
}

/* =================== DASHBOARD / CARDS =================== */
#tarjetaDashboard { background:#0F172A; border:1px solid #1F2A44; border-radius:16px; }
#tarjetaDashboard:hover { border:1px solid #27456F; }
#tarjetaDashboard QLabel[role="cardtitle"] { font-size:16px; font-weight:700; color:#E5E7EB; }
QLabel[role="pageTitle"] { font-size:20px; font-weight:800; color:#E5E7EB; }

/* KPI tiles */
QFrame#tarjetaDashboard[class="kpiTile"] { background:#0F172A; border:1px solid #1F2A44; border-radius:16px; }
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] {
  background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1F6BFF, stop:1 #5EA8FF);
}
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QLabel,
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QFrame { color:#FFFFFF; }
QFrame#tarjetaDashboard[class="kpiTile"] QLabel[role="subtitle"] { color:#9CA3AF; font-size:13px; }
QFrame#tarjetaDashboard[class="kpiTile"] QLabel[role="value"] { font-size:24px; font-weight:800; }

#carouselBtn { background:#0F172A; border:1px solid #1F2A44; border-radius:8px; padding:4px 8px; color:#E5E7EB; font-size:14px; }
#carouselBtn:hover { border-color:#27456F; background:#0D1526; }

/* Weather chips */
#hourChip { border:1px solid #1F2A44; border-radius:10px; padding:6px 8px; color:#E5E7EB; }

/* =================== CARDS GENERALES (módulos) =================== */
#card, #headerCard, #tableCard, .card, QTableWidget, QTreeWidget {
  background:#0F172A; border:1px solid #1F2A44; border-radius:16px;
}
.card:hover { border-color:#27456F; }

/* Pills & muted */
QLabel[pill="true"] {
  background:#0D1526; border:1px solid #1F2A44; border-radius:9px;
  padding:4px 10px; font-weight:600; color:#D1D5DB; font-size:13px;
}
QLabel[muted="true"] { color:#94A3B8; font-size:13px; }

/* Etiquetas / hints */
QLabel[role="fieldLabel"] { font-weight:600; color:#E5E7EB; margin-bottom:4px; font-size:14px; }
QLabel[role="hint"] { color:#94A3B8; font-size:13px; }

/* =================== INPUTS =================== */
QLineEdit, QComboBox, QDateEdit, QDateTimeEdit, QDoubleSpinBox, QTextEdit {
  background:#0D1526; border:1px solid #1F2A44; border-radius:10px; padding:8px 12px; min-height:30px; color:#E5E7EB; font-size:14px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
  border:1px solid #60A5FA; background:#101C30;
}

/* Buscador */
QLineEdit#searchBox {
  background:#0D1526; border:1px solid #1F2A44; border-radius:10px; padding:10px 14px; color:#E5E7EB; font-size:14px;
}
QLineEdit#searchBox:focus { border-color:#60A5FA; }

/* =================== BOTONES =================== */
QPushButton[type="primary"] {
  background:#2979FF; border:1px solid #2979FF; color:#FFFFFF;
  border-radius:10px; padding:9px 14px; qproperty-iconSize: 20px 20px; font-size:14px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

QPushButton[type="secondary"] {
  background:#0F172A; border:1px solid #1F2A44; color:#E5E7EB;
  border-radius:10px; padding:8px 16px; min-height:30px; font-size:14px;
}
QPushButton[type="secondary"]:hover { border-color:#27456F; }

QPushButton[type="danger"] {
  background:#EF5350; border:1px solid #EF5350; color:#FFFFFF;
  border-radius:8px; padding:7px 12px; min-height:30px; font-size:13px;
}
QPushButton[type="danger"]:hover { background:#f26461; }

QPushButton[role="iconSmall"] {
  min-width:28px; max-width:34px; min-height:28px; padding:0; font-size:18px; font-weight:700; color:#E5E7EB;
}

/* Icon-only */
QToolButton[type="icon"], QPushButton[type="icon"] {
  background:transparent; border:none; color:#A1AEC5; padding:6px; border-radius:8px; qproperty-iconSize: 20px 20px; font-size:16px;
}
QToolButton[type="icon"]:hover, QPushButton[type="icon"]:hover {
  background:rgba(41,121,255,.16); color:#FFFFFF;
}
QPushButton[type="icon"][variant="edit"], QToolButton[type="icon"][variant="edit"] {
  background:#153E75; color:#CFE1FF;
}
QPushButton[type="icon"][variant="edit"]:hover, QToolButton[type="icon"][variant="edit"]:hover {
  background:#1B4C91; color:#E5F0FF;
}
QPushButton[type="icon"][variant="delete"], QToolButton[type="icon"][variant="delete"] {
  background:#5A1020; color:#FFD1D9;
}
QPushButton[type="icon"][variant="delete"]:hover, QToolButton[type="icon"][variant="delete"]:hover {
  background:#701A2C; color:#FFE4E8;
}

/* =================== TABLAS / LISTAS =================== */
QHeaderView::section {
  background:#0D1526; color:#E5E7EB; padding:12px; border:none; border-right:1px solid #1F2A44; font-size:14px;
}
QTableWidget {
  gridline-color:#1F2A44; selection-background-color:rgba(41,121,255,.25); selection-color:#FFFFFF; border:none;
}
QTableWidget::item { padding:8px; font-size:14px; }
QTreeWidget {
  selection-background-color:rgba(41,121,255,.25); selection-color:#FFFFFF;
  border:1px solid #1F2A44; border-radius:16px;
}
QTableWidget QWidget, QTreeWidget QWidget { background:transparent; border:none; }

/* ======== Form específico: GastoForm ======== */
#GastoFormFrame {
  background:#0F172A; border:1px solid #27456F; border-radius:10px;
}
/* Contenedores marcados como 'transparent' para remover cualquier fondo/sombra */
QFrame#transparent, QWidget#transparent { background: transparent; border: none; }
"""
