import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QCoreApplication, QPropertyAnimation, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QMenuBar, QStatusBar, QStackedWidget,
    QButtonGroup, QSizePolicy, QSpacerItem
)

from forms.productos_ui import Ui_Form as ProductosForm
from forms.compras_ui import Ui_Form as ComprasForm
from forms.Obras_ui import ObrasWidget
from forms.Ventas_ui import Ui_Form as VentasForm
from forms.Clientes_ui import Ui_Form as ClientesForm
from forms.Proveedores_ui import Ui_Form as ProveedoresForm


# =============== Paleta clara (predomina blanco + celestes) ===============
QSS_RODLER_LIGHT = """
/* -------- Paleta --------
Base    : #ffffff
Superf. : #f7f9fc
Borde   : #dfe7f5
Texto   : #0d1b2a
Suave   : #5b6b8a
Acento  : #4fc3f7  (celeste)
Acento2 : #90caf9  (azul claro)
Hover   : rgba(79,195,247,.12)
Active  : rgba(144,202,249,.20)
---------------------------------- */

* { color: #0d1b2a; font-family: "Segoe UI", Arial, sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: #ffffff; }

/* Top bar */
#topBar {
  background: #ffffff;
  border-bottom: 1px solid #dfe7f5;
}
QLabel#labelTitulo { font-size: 22px; font-weight: 800; letter-spacing: .4px; } /* RODLER más grande */
QLabel[role="subtitle"] { color: #5b6b8a; font-size: 12px; }

/* Sidebar */
#sidebar {
  background: #ffffff;
  border-right: 1px solid #dfe7f5;
}
#sidebarHeader {
  background: transparent;
  border: none;
}

/* Botón de toggle (arriba derecha del sidebar) */
#toggleSidebarBtn {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  padding: 6px 10px;
  font-size: 16px;
}
#toggleSidebarBtn:hover {
  background: rgba(79,195,247,.12);
  border-color: rgba(79,195,247,.25);
}

/* Botones de navegación */
QPushButton[nav="true"] {
  text-align: left;
  padding: 10px 12px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  min-height: 36px;
  color: #0d1b2a;
}
QPushButton[nav="true"]:hover {
  background: rgba(79,195,247,.12);           /* Hover celeste suave */
  border-color: rgba(79,195,247,.25);
}
QPushButton[nav="true"]:checked {
  background: rgba(144,202,249,.20);          /* Activo azul claro */
  border-color: #90caf9;
}

/* Estado colapsado: alineación centrada para iconos */
QPushButton[nav="true"][mini="true"] {
  text-align: center;
  padding: 8px 6px;
}

/* Cards del dashboard */
#tarjetaDashboard {
  background: #f7f9fc;
  border: 1px solid #dfe7f5;
  border-radius: 12px;
}
#tarjetaDashboard:hover { border: 1px solid #90caf9; }
#tarjetaDashboard QLabel { font-size: 14px; font-weight: 600; color: #0d1b2a; }

/* Tablas (si algún módulo las usa) */
QTableWidget, QTableView {
  gridline-color: #dfe7f5;
  background: #ffffff;
  border: 1px solid #dfe7f5;
  border-radius: 12px;
}
QHeaderView::section {
  background: #f7f9fc;
  color: #0d1b2a;
  padding: 8px;
  border: none;
  border-right: 1px solid #dfe7f5;
}
QTableWidget::item, QTableView::item {
  selection-background-color: rgba(144,202,249,.25);
  selection-color: #0d1b2a;
}

/* StatusBar / MenuBar */
QMenuBar { background: #ffffff; border-bottom: 1px solid #dfe7f5; }
QStatusBar { background: #ffffff; color: #5b6b8a; }
"""

# Datos de navegación: etiqueta + icono (unicode/emoji)
NAV_ITEMS = [
    ("Inicio",       "🏠", None),          # dashboard
    ("Productos",    "📦", ProductosForm),
    ("Ventas",       "🧾", VentasForm),
    ("Compras",      "🛒", ComprasForm),
    ("Obras",        "🏗️", ObrasWidget),
    ("Clientes",     "👥", ClientesForm),
    ("Proveedores",  "🏪", ProveedoresForm),
]

EXPANDED_WIDTH = 224
COLLAPSED_WIDTH = 64


class SenalLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1160, 740)

        # === Raíz ===
        self.centralwidget = QWidget(MainWindow)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)

        self.mainContainer = QWidget(self.centralwidget)
        self.gridLayout_2 = QGridLayout(self.mainContainer)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)

        # === TOP BAR ===
        self.contenedorMenuAlto = QWidget(self.mainContainer)
        self.contenedorMenuAlto.setMaximumHeight(56)
        self.contenedorMenuAlto.setObjectName("topBar")
        self.horizontalLayout_3 = QHBoxLayout(self.contenedorMenuAlto)
        self.horizontalLayout_3.setContentsMargins(16, 8, 16, 8)

        self.menualto = QFrame(self.contenedorMenuAlto)
        self.menualto.setObjectName("menualto")
        self.horizontalLayout_4 = QHBoxLayout(self.menualto)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)

        self.labelTitulo = QLabel("RODLER")
        self.labelTitulo.setObjectName("labelTitulo")  # más grande en QSS
        self.horizontalLayout_4.addWidget(self.labelTitulo)

        self.horizontalLayout_4.addStretch(1)

        self.labelUsuario = QLabel("usuario")
        self.labelUsuario.setProperty("role", "subtitle")
        self.horizontalLayout_4.addWidget(self.labelUsuario)

        self.horizontalLayout_3.addWidget(self.menualto)
        self.gridLayout_2.addWidget(self.contenedorMenuAlto, 0, 0, 1, 2)

        # === SIDEBAR ===
        self.menuLateral = QFrame(self.mainContainer)
        self.menuLateral.setObjectName("sidebar")
        self.menuLateral.setMaximumWidth(EXPANDED_WIDTH)
        self.menuLateral.setMinimumWidth(0)
        self.animation_sidebar = QPropertyAnimation(self.menuLateral, b"maximumWidth")
        self.animation_sidebar.setDuration(220)

        self.sidebarLayout = QVBoxLayout(self.menuLateral)
        self.sidebarLayout.setContentsMargins(10, 10, 10, 10)
        self.sidebarLayout.setSpacing(8)

        # Header del sidebar (solo contiene el botón de toggle a la derecha)
        self.sidebarHeader = QFrame(self.menuLateral)
        self.sidebarHeader.setObjectName("sidebarHeader")
        headerLayout = QHBoxLayout(self.sidebarHeader)
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.botonOcultarMenu = QPushButton("❮")  # dentro del menú, arriba derecha
        self.botonOcultarMenu.setObjectName("toggleSidebarBtn")
        self.botonOcultarMenu.setCursor(Qt.PointingHandCursor)
        self.botonOcultarMenu.setToolTip("Colapsar menú")
        headerLayout.addWidget(self.botonOcultarMenu)
        self.sidebarLayout.addWidget(self.sidebarHeader)

        # Botones de navegación
        self.btn_group = QButtonGroup()
        self.btn_group.setExclusive(True)
        self.menu_buttons = {}
        self.modulos = {}
        for nombre, icono, clase in NAV_ITEMS:
            self.modulos[nombre] = clase
            btn = QPushButton(f"{icono}  {nombre}")
            btn.setCheckable(True)
            btn.setProperty("nav", True)
            btn.setProperty("mini", False)  # cambia a True en modo colapsado
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda checked, m=nombre: self.abrir_modulo(m))
            self.sidebarLayout.addWidget(btn)
            self.btn_group.addButton(btn)
            self.menu_buttons[nombre] = btn

        self.sidebarLayout.addStretch(1)
        self.gridLayout_2.addWidget(self.menuLateral, 1, 0, 1, 1)

        # === STACKED (contenido) ===
        self.stackedWidget = QStackedWidget(self.mainContainer)

        # Dashboard (Inicio)
        self.paginaPrincipal = QWidget()
        self.paginaPrincipal.setObjectName("paginaPrincipal")
        dashboard_layout = QGridLayout(self.paginaPrincipal)
        dashboard_layout.setContentsMargins(16, 16, 16, 16)
        dashboard_layout.setSpacing(12)

        self.tarjeta1 = self.crear_tarjeta("Estadística 1", "tarjetaDashboard")
        self.tarjeta2 = self.crear_tarjeta("Estadística 2", "tarjetaDashboard")
        self.tarjeta3 = self.crear_tarjeta("Estadística 3", "tarjetaDashboard")
        self.tarjeta4 = self.crear_tarjeta("Estadística 4", "tarjetaDashboard")

        dashboard_layout.addWidget(self.tarjeta1, 0, 0)
        dashboard_layout.addWidget(self.tarjeta2, 0, 1)
        dashboard_layout.addWidget(self.tarjeta3, 1, 0)
        dashboard_layout.addWidget(self.tarjeta4, 1, 1)

        self.stackedWidget.addWidget(self.paginaPrincipal)
        self.gridLayout_2.addWidget(self.stackedWidget, 1, 1, 1, 1)

        self.gridLayout.addWidget(self.mainContainer, 0, 0)
        MainWindow.setCentralWidget(self.centralwidget)

        # Menú y status
        self.menubar = QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        # Conexiones
        self.botonOcultarMenu.clicked.connect(self.toggleMenuLateral)

        # Estilos globales (paleta clara)
        MainWindow.setStyleSheet(QSS_RODLER_LIGHT)

        # Estado inicial
        self.menu_buttons["Inicio"].setChecked(True)
        self.stackedWidget.setCurrentWidget(self.paginaPrincipal)
        self._sidebar_collapsed = False  # expandido al inicio

        QCoreApplication.translate("MainWindow", None)

    # ---------- Helpers UI ----------
    def crear_tarjeta(self, titulo, object_name):
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        label = QLabel(titulo)
        layout.addWidget(label)
        return frame

    def _apply_sidebar_mode(self, collapsed: bool):
        """Actualiza textos/props de botones y ancho según modo."""
        if collapsed:
            # Achicar: solo iconos, centrados
            for nombre, icono, _ in NAV_ITEMS:
                btn = self.menu_buttons[nombre]
                btn.setText(icono)               # icono solamente
                btn.setProperty("mini", True)    # para QSS (centrado)
                btn.setToolTip(nombre)           # tooltip con nombre
                btn.style().unpolish(btn); btn.style().polish(btn)
            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth())
            self.animation_sidebar.setEndValue(COLLAPSED_WIDTH)
            self.botonOcultarMenu.setText("❯")
            self.botonOcultarMenu.setToolTip("Expandir menú")
        else:
            # Expandir: icono + texto
            for nombre, icono, _ in NAV_ITEMS:
                btn = self.menu_buttons[nombre]
                btn.setText(f"{icono}  {nombre}")
                btn.setProperty("mini", False)
                btn.setToolTip("")               # no hace falta en expandido
                btn.style().unpolish(btn); btn.style().polish(btn)
            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth())
            self.animation_sidebar.setEndValue(EXPANDED_WIDTH)
            self.botonOcultarMenu.setText("❮")
            self.botonOcultarMenu.setToolTip("Colapsar menú")

        self.animation_sidebar.start()

    def toggleMenuLateral(self):
        self._sidebar_collapsed = not getattr(self, "_sidebar_collapsed", False)
        self._apply_sidebar_mode(self._sidebar_collapsed)

    def abrir_modulo(self, nombre_modulo):
        # Inicio → dashboard
        if nombre_modulo == "Inicio":
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)
            # Si está colapsado, el botón de toggle queda arriba del listado (ya lo está)
            return

        # Evitar recarga si ya está
        if hasattr(self, f"pagina_{nombre_modulo}") and \
           self.stackedWidget.currentWidget() == getattr(self, f"pagina_{nombre_modulo}"):
            return

        # Cargar el módulo si no existe aún
        if not hasattr(self, f"pagina_{nombre_modulo}"):
            clase_modulo = self.modulos[nombre_modulo]
            instancia_modulo = clase_modulo() if clase_modulo is not None else None
            if instancia_modulo is None:
                pagina = self.paginaPrincipal
            else:
                if hasattr(instancia_modulo, "setupUi"):
                    pagina = QWidget()
                    instancia_modulo.setupUi(pagina)
                else:
                    pagina = instancia_modulo  # QWidget puro como ObrasWidget
                self.stackedWidget.addWidget(pagina)
            setattr(self, f"pagina_{nombre_modulo}", pagina)

        self.stackedWidget.setCurrentWidget(getattr(self, f"pagina_{nombre_modulo}"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
