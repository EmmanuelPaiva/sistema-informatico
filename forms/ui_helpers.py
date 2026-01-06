# rodler_ui_helpers.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPlainTextEdit, QTextEdit,
    QTableWidget, QTableView, QHeaderView, QPushButton, QToolButton, QGroupBox
)
from PySide6.QtCore import Qt
from main.themes import themed_icon

def mark_title(label: QLabel):
    label.setProperty("role", "title")
    label.setTextFormat(Qt.RichText)
    label.style().unpolish(label); label.style().polish(label)

def mark_subtitle(label: QLabel):
    label.setProperty("role", "subtitle")
    label.style().unpolish(label); label.style().polish(label)

def make_primary(btn: QPushButton):
    btn.setProperty("type", "primary")
    btn.style().unpolish(btn); btn.style().polish(btn)

def make_danger(btn: QPushButton):
    btn.setProperty("type", "danger")
    btn.style().unpolish(btn); btn.style().polish(btn)


def style_icon_button(btn, variant: str, tooltip: str | None = None, icon_name: str | None = None):
    """
    Aplica los estilos globales de icon-button (editar/eliminar, etc.).
    Acepta QPushButton o QToolButton.
    """
    if tooltip:
        try:
            btn.setToolTip(tooltip)
        except Exception:
            pass
    try:
        btn.setText("")
    except Exception:
        pass
    try:
        btn.setProperty("type", "icon")
        btn.setProperty("variant", variant)
    except Exception:
        pass
    try:
        btn.setCursor(Qt.PointingHandCursor)
    except Exception:
        pass
    if icon_name:
        try:
            btn.setIcon(themed_icon(icon_name))
        except Exception:
            pass
    try:
        style = btn.style()
        style.unpolish(btn)
        style.polish(btn)
    except Exception:
        pass


def style_edit_button(btn, tooltip: str | None = None):
    tooltip = tooltip or "Editar"
    style_icon_button(btn, "edit", tooltip, "edit")


def style_delete_button(btn, tooltip: str | None = None):
    tooltip = tooltip or "Eliminar"
    style_icon_button(btn, "delete", tooltip, "trash")

def style_table(tbl):
    """Config básica para tablas."""
    if isinstance(tbl, (QTableWidget, QTableView)):
        if hasattr(tbl, "horizontalHeader"):
            hh: QHeaderView = tbl.horizontalHeader()
            hh.setStretchLastSection(True)
            hh.setHighlightSections(False)
        if hasattr(tbl, "verticalHeader"):
            vh: QHeaderView = tbl.verticalHeader()
            vh.setVisible(False)
        tbl.setAlternatingRowColors(False)
        tbl.setSortingEnabled(False)

def style_search(line: QLineEdit):
    line.setPlaceholderText(line.placeholderText() or "Buscar…")

def style_groupbox(gb: QGroupBox, title: str | None = None):
    if title:
        gb.setTitle(title)
        
# Override: do not set per-form QSS anymore; themes are global
def apply_global_styles(root: QWidget):
    """Styles are applied globally via main/themes; no-op here."""
    return
