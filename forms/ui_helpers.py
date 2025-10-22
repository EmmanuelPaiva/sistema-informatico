# rodler_ui_helpers.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPlainTextEdit, QTextEdit,
    QTableWidget, QTableView, QHeaderView, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt

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
