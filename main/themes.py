from PySide6.QtWidgets import QWidget

# =========================================================
#  FUNCIONES PÚBLICAS
# =========================================================
def apply_theme(widget: QWidget, dark: bool) -> None:
    """Aplica el tema Rodler (light/dark) al widget principal."""
    widget.setStyleSheet(QSS_RODLER_DARK if dark else QSS_RODLER_LIGHT)


    
# =========================
#  RODLER THEME DEFINITIONS
# =========================

QSS_RODLER_LIGHT = """
/* ================== PALETA BASE (LIGHT) ================== */
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background: transparent; }
:disabled { color:#9AA4B2; }

/* ============== MENU PRINCIPAL / SIDEBAR ============== */
#sidebar { background:#FFFFFF; border-right:1px solid #E8EEF6; }
#sidebarHeader { background: transparent; border: none; }

QPushButton[nav="true"] {
  text-align:left; padding:10px 12px; border-radius:10px;
  background:transparent; border:1px solid transparent; color:#0F172A;
}
QPushButton[nav="true"]::menu-indicator { image:none; }
QPushButton[nav="true"]:hover { background:rgba(41,121,255,.08); }
QPushButton[nav="true"]:checked {
  background:rgba(41,121,255,.15);
  border:1px solid #90CAF9;
}

#logoutBtn {
  background:#EEF2FF; border:1px solid #E8EEF6; color:#1E293B;
  border-radius:10px; padding:8px 10px;
}
#logoutBtn:hover { background:#E0E7FF; border-color:#C7D2FE; }

#toggleSidebarBtn {
  background:transparent; border:1px solid transparent; border-radius:10px;
  padding:6px 8px; font-size:16px;
}
#toggleSidebarBtn:hover { background:rgba(41,121,255,.08); }

/* =================== TOPBAR & CHIP =================== */
#topBar { background:#FFFFFF; border-bottom:1px solid #E8EEF6; }
#brand QLabel#appTitle { font-size:28px; font-weight:800; color:#0F172A; background:transparent; }
#brand QLabel#appSub { color:#94A3B8; font-size:11px; background:transparent; }

#userChip {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:14px; padding:8px 12px;
}
#userChip QLabel[role="name"] { font-weight:600; }
#userChip QLabel[role="role"] { color:#94A3B8; font-size:11px; }
#userChipArrow { border:none; padding:2px 4px; background:transparent; }
#userChipArrow:hover { background:transparent; }

/* ======= POPUP DEL CHIP (botón nuevo usuario / switch / borrar) ======= */
#userMenuPopup {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:12px;
}
#userMenuPopup QPushButton {
  text-align:left; padding:10px 12px; margin:6px 0; border-radius:8px;
  background:transparent; color:#0F172A; border:1px solid transparent; min-height:36px;
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
#tarjetaDashboard QLabel[role="cardtitle"] { font-size:14px; font-weight:700; color:#0F172A; }

QFrame#tarjetaDashboard[class="kpiTile"] { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px; }
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] {
  background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2979FF, stop:1 #5EA8FF);
}
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QLabel,
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QFrame { color:#FFFFFF; }
QFrame#tarjetaDashboard[class="kpiTile"] QLabel[role="subtitle"] { color:#94A3B8; }

#carouselBtn { background:#FFFFFF; border:1px solid #E8EEF6; border-radius:8px; padding:4px 8px; }
#carouselBtn:hover { border-color:#90CAF9; background:#F8FAFF; }

/* Weather chips */
#hourChip { border:1px solid #E8EEF6; border-radius:10px; padding:6px 8px; }

/* =================== CARDS GENERALES (módulos) =================== */
#card, #headerCard, #tableCard, .card, QTableWidget, QTreeWidget {
  background:#FFFFFF; border:1px solid #E8EEF6; border-radius:16px;
}
.card:hover { border-color:#90CAF9; }

/* Títulos */
QLabel[role="pageTitle"] { font-size:18px; font-weight:800; color:#0F172A; }

/* Pills & muted */
QLabel[pill="true"] {
  background:#F1F5F9; border:1px solid #E8EEF6; border-radius:9px;
  padding:3px 8px; font-weight:600; color:#334155;
}
QLabel[muted="true"] { color:#64748B; }

/* Etiquetas de campos / hints */
QLabel[role="fieldLabel"] { font-weight:600; color:#0F172A; margin-bottom:4px; }
QLabel[role="hint"] { color:#64748B; font-size:12px; }

/* =================== INPUTS =================== */
QLineEdit, QComboBox, QDateEdit, QDateTimeEdit, QDoubleSpinBox, QTextEdit {
  background:#F1F5F9; border:1px solid #E8EEF6; border-radius:10px; padding:6px 10px; min-height:28px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
  border:1px solid #90CAF9; background:#FFFFFF;
}

/* Buscador */
QLineEdit#searchBox {
  background:#F1F5F9; border:1px solid #E8EEF6; border-radius:10px; padding:8px 12px;
}
QLineEdit#searchBox:focus { border-color:#90CAF9; }

/* =================== BOTONES =================== */
QPushButton[type="primary"] {
  background:#2979FF; border:1px solid #2979FF; color:#FFFFFF;
  border-radius:10px; padding:8px 12px; qproperty-iconSize: 18px 18px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

QPushButton[type="secondary"] {
  background:#FFFFFF; border:1px solid #E8EEF6; color:#0F172A;
  border-radius:10px; padding:6px 14px; min-height:28px;
}
QPushButton[type="secondary"]:hover { border-color:#CFE0F5; }

QPushButton[type="danger"] {
  background:#EF5350; border:1px solid #EF5350; color:#FFFFFF;
  border-radius:8px; padding:6px 12px; min-height:28px; font-size:12px;
}
QPushButton[type="danger"]:hover { background:#f26461; }

QPushButton[role="iconSmall"] {
  min-width:28px; max-width:34px; min-height:28px; padding:0; font-size:16px; font-weight:700;
}

/* Icon-only (editar/eliminar en cards, toolbuttons) */
QToolButton[type="icon"], QPushButton[type="icon"] {
  background:transparent; border:none; color:#64748B; padding:6px; border-radius:8px; qproperty-iconSize: 18px 18px;
}
QToolButton[type="icon"]:hover, QPushButton[type="icon"]:hover {
  background:rgba(41,121,255,.10); color:#0F172A;
}
QPushButton[type="icon"][variant="edit"], QToolButton[type="icon"][variant="edit"] {
  background:#EAF2FF; color:#1D4ED8;
}
QPushButton[type="icon"][variant="edit"]:hover, QToolButton[type="icon"][variant="edit"]:hover {
  background:#DCEBFF; color:#1E40AF;
}
QPushButton[type="icon"][variant="delete"], QToolButton[type="icon"][variant="delete"] {
  background:#FEECEC; color:#DC2626;
}
QPushButton[type="icon"][variant="delete"]:hover, QToolButton[type="icon"][variant="delete"]:hover {
  background:#FDDDDD; color:#B91C1C;
}

/* =================== TABLAS / LISTAS =================== */
QHeaderView::section {
  background:#F8FAFF; color:#0F172A; padding:10px; border:none; border-right:1px solid #E8EEF6;
}
QTableWidget {
  gridline-color:#E8EEF6; selection-background-color:rgba(41,121,255,.15); selection-color:#0F172A; border:none;
}
QTableWidget::item { padding:6px; }
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
"""

QSS_RODLER_DARK = """
/* ================== PALETA BASE (DARK) ================== */
* { font-family:"Segoe UI", Arial, sans-serif; color:#E5E7EB; font-size:13px; }
QWidget { background:#0B1220; }               /* fondo general más profundo */
QLabel { background:transparent; }
:disabled { color:#6B7280; }

/* Variables (referenciales, por consistencia visual)
   surface: #0F172A | headers: #0D1526 | border: #1F2A44 | text: #E5E7EB
   muted: #94A3B8 | sub: #9CA3AF | primary: #2979FF (hover #3b86ff)
*/

/* ============== MENU PRINCIPAL / SIDEBAR ============== */
#sidebar { background:#0F172A; border-right:1px solid #1F2A44; }
#sidebarHeader { background:transparent; border:none; }

QPushButton[nav="true"] {
  text-align:left; padding:10px 12px; border-radius:10px;
  background:transparent; border:1px solid transparent; color:#E5E7EB;
}
QPushButton[nav="true"]::menu-indicator { image:none; }
QPushButton[nav="true"]:hover { background:rgba(41,121,255,.12); }
QPushButton[nav="true"]:checked {
  background:rgba(41,121,255,.18);
  border:1px solid #60A5FA;
}

#logoutBtn {
  background:#111B2E; border:1px solid #1F2A44; color:#D1D5DB;
  border-radius:10px; padding:8px 10px;
}
#logoutBtn:hover { background:#12203A; border-color:#27456F; }

#toggleSidebarBtn {
  background:transparent; border:1px solid transparent; border-radius:10px;
  padding:6px 8px; font-size:16px; color:#E5E7EB;
}
#toggleSidebarBtn:hover { background:rgba(41,121,255,.12); }

/* =================== TOPBAR & CHIP =================== */
#topBar { background:#0F172A; border-bottom:1px solid #1F2A44; }
#brand QLabel#appTitle { font-size:28px; font-weight:800; color:#E5E7EB; background:transparent; }
#brand QLabel#appSub { color:#9CA3AF; font-size:11px; background:transparent; }

#userChip {
  background:#0F172A; border:1px solid #1F2A44; border-radius:14px; padding:8px 12px;
}
#userChip QLabel[role="name"] { font-weight:600; color:#E5E7EB; }
#userChip QLabel[role="role"] { color:#9CA3AF; font-size:11px; }
#userChipArrow { border:none; padding:2px 4px; background:transparent; color:#E5E7EB; }
#userChipArrow:hover { background:transparent; }

/* ======= POPUP DEL CHIP ======= */
#userMenuPopup {
  background:#0F172A; border:1px solid #1F2A44; border-radius:12px;
}
#userMenuPopup QPushButton {
  text-align:left; padding:10px 12px; margin:6px 0; border-radius:8px;
  background:transparent; color:#E5E7EB; border:1px solid transparent; min-height:36px;
}
#userMenuPopup QPushButton:hover { background:rgba(41,121,255,.12); }

/* Switch de tema en dark (unchecked gris azulado / checked azul vivo) */
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
#tarjetaDashboard QLabel[role="cardtitle"] { font-size:14px; font-weight:700; color:#E5E7EB; }

QFrame#tarjetaDashboard[class="kpiTile"] { background:#0F172A; border:1px solid #1F2A44; border-radius:16px; }
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] {
  background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1F6BFF, stop:1 #5EA8FF);
}
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QLabel,
QFrame#tarjetaDashboard[class="kpiTile"][accent="blue"] QFrame { color:#FFFFFF; }
QFrame#tarjetaDashboard[class="kpiTile"] QLabel[role="subtitle"] { color:#9CA3AF; }

#carouselBtn { background:#0F172A; border:1px solid #1F2A44; border-radius:8px; padding:4px 8px; color:#E5E7EB; }
#carouselBtn:hover { border-color:#27456F; background:#0D1526; }

/* Weather chips */
#hourChip { border:1px solid #1F2A44; border-radius:10px; padding:6px 8px; color:#E5E7EB; }

/* =================== CARDS GENERALES (módulos) =================== */
#card, #headerCard, #tableCard, .card, QTableWidget, QTreeWidget {
  background:#0F172A; border:1px solid #1F2A44; border-radius:16px;
}
.card:hover { border-color:#27456F; }

/* Títulos */
QLabel[role="pageTitle"] { font-size:18px; font-weight:800; color:#E5E7EB; }

/* Pills & muted */
QLabel[pill="true"] {
  background:#0D1526; border:1px solid #1F2A44; border-radius:9px;
  padding:3px 8px; font-weight:600; color:#D1D5DB;
}
QLabel[muted="true"] { color:#94A3B8; }

/* Etiquetas / hints */
QLabel[role="fieldLabel"] { font-weight:600; color:#E5E7EB; margin-bottom:4px; }
QLabel[role="hint"] { color:#94A3B8; font-size:12px; }

/* =================== INPUTS =================== */
QLineEdit, QComboBox, QDateEdit, QDateTimeEdit, QDoubleSpinBox, QTextEdit {
  background:#0D1526; border:1px solid #1F2A44; border-radius:10px; padding:6px 10px; min-height:28px; color:#E5E7EB;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
  border:1px solid #60A5FA; background:#101C30;
}

/* Buscador */
QLineEdit#searchBox {
  background:#0D1526; border:1px solid #1F2A44; border-radius:10px; padding:8px 12px; color:#E5E7EB;
}
QLineEdit#searchBox:focus { border-color:#60A5FA; }

/* =================== BOTONES =================== */
QPushButton[type="primary"] {
  background:#2979FF; border:1px solid #2979FF; color:#FFFFFF;
  border-radius:10px; padding:8px 12px; qproperty-iconSize: 18px 18px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

QPushButton[type="secondary"] {
  background:#0F172A; border:1px solid #1F2A44; color:#E5E7EB;
  border-radius:10px; padding:6px 14px; min-height:28px;
}
QPushButton[type="secondary"]:hover { border-color:#27456F; }

QPushButton[type="danger"] {
  background:#EF5350; border:1px solid #EF5350; color:#FFFFFF;
  border-radius:8px; padding:6px 12px; min-height:28px; font-size:12px;
}
QPushButton[type="danger"]:hover { background:#f26461; }

QPushButton[role="iconSmall"] {
  min-width:28px; max-width:34px; min-height:28px; padding:0; font-size:16px; font-weight:700; color:#E5E7EB;
}

/* Icon-only */
QToolButton[type="icon"], QPushButton[type="icon"] {
  background:transparent; border:none; color:#A1AEC5; padding:6px; border-radius:8px; qproperty-iconSize: 18px 18px;
}
QToolButton[type="icon"]:hover, QPushButton[type="icon"]:hover {
  background:rgba(41,121,255,.16); color:#FFFFFF;
}
QPushButton[type="icon"][variant="edit"], QToolButton[type="icon"][variant="edit"] {
  background:#0D1C34; color:#93C5FD;
}
QPushButton[type="icon"][variant="edit"]:hover, QToolButton[type="icon"][variant="edit"]:hover] {
  background:#0E2345; color:#BFDBFE;
}
QPushButton[type="icon"][variant="delete"], QToolButton[type="icon"][variant="delete"] {
  background:#2A0F12; color:#FCA5A5;
}
QPushButton[type="icon"][variant="delete"]:hover, QToolButton[type="icon"][variant="delete"]:hover {
  background:#3A1519; color:#FEE2E2;
}

/* =================== TABLAS / LISTAS =================== */
QHeaderView::section {
  background:#0D1526; color:#E5E7EB; padding:10px; border:none; border-right:1px solid #1F2A44;
}
QTableWidget {
  gridline-color:#1F2A44; selection-background-color:rgba(41,121,255,.25); selection-color:#FFFFFF; border:none;
}
QTableWidget::item { padding:6px; }
QTreeWidget {
  selection-background-color:rgba(41,121,255,.25); selection-color:#FFFFFF;
  border:1px solid #1F2A44; border-radius:16px;
}
QTableWidget QWidget, QTreeWidget QWidget { background:transparent; border:none; }

/* ======== Form específico: GastoForm ======== */
#GastoFormFrame {
  background:#0F172A; border:1px solid #27456F; border-radius:10px;
}
"""
