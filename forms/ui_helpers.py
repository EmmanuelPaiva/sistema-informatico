# rodler_ui_helpers.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPlainTextEdit, QTextEdit,
    QTableWidget, QTableView, QHeaderView, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt

QSS_RODLER_LIGHT = """
* { color: #0d1b2a; font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #ffffff; }
#topBar { background: #ffffff; border-bottom: 1px solid #dfe7f5; }
QLabel#labelTitulo { font-size: 22px; font-weight: 800; letter-spacing: .4px; }
QLabel[role="subtitle"] { color: #5b6b8a; font-size: 12px; }

#sidebar { background: #ffffff; border-right: 1px solid #dfe7f5; }
#sidebarHeader { background: transparent; border: none; }
#toggleSidebarBtn {
  background: transparent; border: 1px solid transparent; border-radius: 10px; padding: 6px 10px; font-size: 16px;
}
#toggleSidebarBtn:hover { background: rgba(79,195,247,.12); border-color: rgba(79,195,247,.25); }

QPushButton[nav="true"] {
  text-align: left; padding: 10px 12px; border-radius: 12px; background: transparent; border: 1px solid transparent; min-height: 36px; color: #0d1b2a;
}
QPushButton[nav="true"]:hover { background: rgba(79,195,247,.12); border-color: rgba(79,195,247,.25); }
QPushButton[nav="true"]:checked { background: rgba(144,202,249,.20); border-color: #90caf9; }
QPushButton[nav="true"][mini="true"] { text-align: center; padding: 8px 6px; }

#tarjetaDashboard { background: #f7f9fc; border: 1px solid #dfe7f5; border-radius: 12px; }
#tarjetaDashboard:hover { border: 1px solid #90caf9; }
#tarjetaDashboard QLabel { font-size: 14px; font-weight: 600; color: #0d1b2a; }

QTableWidget, QTableView { gridline-color: #dfe7f5; background: #ffffff; border: 1px solid #dfe7f5; border-radius: 12px; }
QHeaderView::section { background: #f7f9fc; color: #0d1b2a; padding: 8px; border: none; border-right: 1px solid #dfe7f5; }
QTableWidget::item, QTableView::item { selection-background-color: rgba(144,202,249,.25); selection-color: #0d1b2a; }

QLineEdit, QPlainTextEdit, QTextEdit {
  background: #ffffff; border: 1px solid #dfe7f5; border-radius: 10px; padding: 6px 10px;
  selection-background-color: #90caf9; selection-color: #0d1b2a;
}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #90caf9; }

QPushButton[type="primary"] {
  background: #4fc3f7; border: 1px solid #4fc3f7; color: #0d1b2a; border-radius: 10px; padding: 8px 12px;
}
QPushButton[type="primary"]:hover { background: #6fd0fa; }
QPushButton[type="danger"] {
  background: #ef5350; border: 1px solid #ef5350; color: white; border-radius: 10px; padding: 8px 12px;
}
QGroupBox { border: 1px solid #dfe7f5; border-radius: 12px; margin-top: 10px; background: #ffffff; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #5b6b8a; }
"""

def apply_global_styles(root: QWidget):
    """Aplica el QSS claro al widget raíz del módulo (no a toda la app)."""
    root.setStyleSheet(QSS_RODLER_LIGHT)

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
