import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QCoreApplication, QPropertyAnimation, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QMenuBar, QStatusBar, QStackedWidget
)

# Importación de todos los módulos
from forms.productos_ui import Ui_Form as ProductosForm
from forms.compras_ui import Ui_Form as ComprasForm
from forms.Obras_ui import Ui_Form as ObrasForm
from forms.ventas_ui import Ui_Form as VentasForm
from forms.Clientes_ui import Ui_Form as ClientesForm
from forms.Proveedores_ui import Ui_Form as ProveedoresForm


# Señal personalizada para QLabel clickeable
class SenalLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)

        # === Central Widget ===
        self.centralwidget = QWidget(MainWindow)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)

        # === Contenedor principal ===
        self.mainContainer = QWidget(self.centralwidget)
        self.gridLayout_2 = QGridLayout(self.mainContainer)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)

        # === Menú Superior ===
        self.contenedorMenuAlto = QWidget(self.mainContainer)
        self.contenedorMenuAlto.setMaximumHeight(40)
        self.horizontalLayout_3 = QHBoxLayout(self.contenedorMenuAlto)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.menualto = QFrame(self.contenedorMenuAlto)
        self.menualto.setObjectName("menualto")
        self.horizontalLayout_4 = QHBoxLayout(self.menualto)

        self.label_7 = QLabel("RODLER")
        self.label_7.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.horizontalLayout_4.addWidget(self.label_7)

        self.botonOcultarMenu = QPushButton("☰")
        self.botonOcultarMenu.setMaximumWidth(40)
        self.botonOcultarMenu.setCursor(Qt.PointingHandCursor)
        self.horizontalLayout_4.addWidget(self.botonOcultarMenu)

        self.label_8 = QLabel("usuario")
        self.label_8.setStyleSheet("font-size: 14px; margin-left: auto;")
        self.horizontalLayout_4.addWidget(self.label_8)

        self.horizontalLayout_3.addWidget(self.menualto)
        self.gridLayout_2.addWidget(self.contenedorMenuAlto, 0, 0, 1, 2)

        # === Menú lateral ===
        self.menuLateral = QFrame(self.mainContainer)
        self.menuLateral.setObjectName("menuLateral")
        self.menuLateral.setMaximumWidth(200)
        self.animation_sidebar = QPropertyAnimation(self.menuLateral, b"maximumWidth")
        self.animation_sidebar.setDuration(200)

        self.verticalLayout = QVBoxLayout(self.menuLateral)

        # Diccionario para módulos
        self.modulos = {
            "Productos": ProductosForm,
            "Ventas": VentasForm,
            "Compras": ComprasForm,
            "Obras": ObrasForm,
            "Clientes": ClientesForm,
            "Proveedores": ProveedoresForm
        }

        # Crear labels del menú
        self.menu_labels = {}
        for nombre_modulo in self.modulos.keys():
            label = SenalLabel(nombre_modulo)
            label.setCursor(Qt.PointingHandCursor)
            label.setFixedHeight(35)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName("menuLabel")
            label.clicked.connect(lambda m=nombre_modulo: self.abrir_modulo(m))
            self.verticalLayout.addWidget(label)
            self.menu_labels[nombre_modulo] = label

        self.gridLayout_2.addWidget(self.menuLateral, 1, 0, 1, 1)

        # === Área central con QStackedWidget ===
        self.stackedWidget = QStackedWidget(self.mainContainer)

        # Página principal (Dashboard)
        self.paginaPrincipal = QWidget()
        self.paginaPrincipal.setObjectName("paginaPrincipal")
        dashboard_layout = QGridLayout(self.paginaPrincipal)

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

        # Barra de menú y estado
        self.menubar = QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        # Conexión del botón para ocultar menú
        self.botonOcultarMenu.clicked.connect(self.toggleMenuLateral)

        # === Estilos generales ===
        MainWindow.setStyleSheet("""
            QMainWindow {
                background-color: #f4f6f8;
            }
            #menualto {
                background-color: #ffffff;
                border-bottom: 1px solid #dcdde1;
            }
            #menualto {
                color: black;
                
            }
            #menuLateral {
                background-color: #ffffff;
                border-right: 1px solid #dcdde1;
            }
            #menuLabel {
                padding: 8px;
                font-size: 14px;
                background-color: black;
                border-radius: 6px;
            }
            #menuLabel:hover {
                background-color: #3498db;
                color: white;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 0.1);
                border-radius: 4px;
            }
        """)

        # === Estilos SOLO para el dashboard ===
        self.paginaPrincipal.setStyleSheet("""
            #tarjetaDashboard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
            #tarjetaDashboard:hover {
                border: 1px solid #3498db;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
            }
            #tarjetaDashboard QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        QCoreApplication.translate("MainWindow", None)

    def crear_tarjeta(self, titulo, object_name):
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout(frame)
        label = QLabel(titulo)
        layout.addWidget(label)
        return frame

    def toggleMenuLateral(self):
        if self.menuLateral.maximumWidth() == 0:
            self.animation_sidebar.setStartValue(0)
            self.animation_sidebar.setEndValue(200)
        else:
            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth())
            self.animation_sidebar.setEndValue(0)
        self.animation_sidebar.start()

    def abrir_modulo(self, nombre_modulo):
        if hasattr(self, f"pagina_{nombre_modulo}") and \
           self.stackedWidget.currentWidget() == getattr(self, f"pagina_{nombre_modulo}"):
            self.stackedWidget.setCurrentWidget(self.paginaPrincipal)
        else:
            if not hasattr(self, f"pagina_{nombre_modulo}"):
                pagina = QWidget()
                ui_modulo = self.modulos[nombre_modulo]()
                ui_modulo.setupUi(pagina)
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