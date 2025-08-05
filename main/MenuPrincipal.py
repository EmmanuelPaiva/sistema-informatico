import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Signal, QPropertyAnimation, QTimer)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget, QStackedWidget,QPushButton)
from forms.productos_ui import Ui_Form as Ui_Form
from forms.compras_ui import Ui_Form as ComprasUiForm
from forms.Obras_ui import Ui_Form as ObrasUiForm
from forms.ventas_ui import Ui_Form as ventasForm

class senal(QLabel):
        clicked = Signal()
        
        
        def mousePressEvent(self, event):
            self.clicked.emit()
            super().mousePressEvent(event)
            
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(793, 531)
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.gridLayout_2 = QGridLayout(self.widget)
        self.stackedWidget = QStackedWidget(self.widget)
        self.stackedWidget.setObjectName("stackedWidget")
        
        self.PaginaPincipal = QWidget()
        self.PaginaPrinciplaLayout = QGridLayout(self.PaginaPincipal)
        
       
        self.stackedWidget.addWidget(self.PaginaPincipal)
        
        self.gridLayout_2.addWidget(self.stackedWidget, 1, 1, 2, 2)
        
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.contenedorGrafico1 = QWidget(self.widget)
        self.contenedorGrafico1.setObjectName(u"contenedorGrafico1")
        self.horizontalLayout = QHBoxLayout(self.contenedorGrafico1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.grafico1 = QFrame(self.contenedorGrafico1)
        self.grafico1.setObjectName(u"grafico1")
        self.grafico1.setFrameShape(QFrame.Shape.StyledPanel)
        self.grafico1.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.grafico1)


        self.PaginaPrinciplaLayout.addWidget(self.contenedorGrafico1, 1, 2, 1, 1)
    
        #self.gridLayout_2.addWidget(self.contenedorGrafico1, 1, 2, 1, 1)

        self.contenedorExcel = QWidget(self.widget)
        self.contenedorExcel.setObjectName(u"contenedorExcel")
        self.horizontalLayout_2 = QHBoxLayout(self.contenedorExcel)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.formularioExcel = QFrame(self.contenedorExcel)
        self.formularioExcel.setObjectName(u"formularioExcel")
        self.formularioExcel.setFrameShape(QFrame.Shape.StyledPanel)
        self.formularioExcel.setFrameShadow(QFrame.Shadow.Raised)

        self.PaginaPrinciplaLayout.addWidget(self.contenedorExcel, 2, 1, 1, 2)
        
        self.horizontalLayout_2.addWidget(self.formularioExcel)


        #self.gridLayout_2.addWidget(self.contenedorExcel, 2, 1, 1, 2)

        self.conetenedorEstadisticas1 = QWidget(self.widget)
        self.conetenedorEstadisticas1.setObjectName(u"conetenedorEstadisticas1")
        self.gridLayout_3 = QGridLayout(self.conetenedorEstadisticas1)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.estadisticas1 = QFrame(self.conetenedorEstadisticas1)
        self.estadisticas1.setObjectName(u"estadisticas1")
        self.estadisticas1.setFrameShape(QFrame.Shape.StyledPanel)
        self.estadisticas1.setFrameShadow(QFrame.Shadow.Raised)
        
        self.PaginaPrinciplaLayout.addWidget(self.conetenedorEstadisticas1, 1, 1, 1, 1)

        self.gridLayout_3.addWidget(self.estadisticas1, 0, 0, 1, 1)

        self.estadisticas2 = QFrame(self.conetenedorEstadisticas1)
        self.estadisticas2.setObjectName(u"estadisticas2")
        self.estadisticas2.setFrameShape(QFrame.Shape.StyledPanel)
        self.estadisticas2.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_3.addWidget(self.estadisticas2, 1, 0, 1, 1)

        self.estadisticas3 = QFrame(self.conetenedorEstadisticas1)
        self.estadisticas3.setObjectName(u"estadisticas3")
        self.estadisticas3.setFrameShape(QFrame.Shape.StyledPanel)
        self.estadisticas3.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_3.addWidget(self.estadisticas3, 1, 1, 1, 1)

        self.estadisticas4 = QFrame(self.conetenedorEstadisticas1)
        self.estadisticas4.setObjectName(u"estadisticas4")
        self.estadisticas4.setFrameShape(QFrame.Shape.StyledPanel)
        self.estadisticas4.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_3.addWidget(self.estadisticas4, 0, 1, 1, 1)


        #self.gridLayout_2.addWidget(self.conetenedorEstadisticas1, 1, 1, 1, 1)

        self.contenedorMenuAlto = QWidget(self.widget)
        self.contenedorMenuAlto.setObjectName(u"contenedorMenuAlto")
        self.contenedorMenuAlto.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_3 = QHBoxLayout(self.contenedorMenuAlto)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.menualto = QFrame(self.contenedorMenuAlto)
        self.menualto.setObjectName(u"menualto")
        self.menualto.setFrameShape(QFrame.Shape.StyledPanel)
        self.menualto.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.menualto)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_7 = QLabel(self.menualto)
        self.label_7.setObjectName(u"label_7")
        self.botonOcultarMenu = QPushButton(self.menualto)
        self.botonOcultarMenu.setText("Ocultar Menu")

        self.horizontalLayout_4.addWidget(self.label_7)
        self.horizontalLayout_4.addWidget(self.botonOcultarMenu)

        self.label_8 = QLabel(self.menualto)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_4.addWidget(self.label_8)


        self.horizontalLayout_3.addWidget(self.menualto)
        

        self.gridLayout_2.addWidget(self.contenedorMenuAlto, 0, 0, 1, 3)
        self.menuLateral = QFrame(self.widget)
        self.menuLateral.setObjectName(u"menuLateral")
        self.menuLateral.setMaximumSize(QSize(180, 16777215))
        
        self.menuLateral.setMinimumWidth(0)
        self.menuLateral.setMaximumWidth(200)

        self.animation_sidebar = QPropertyAnimation(self.menuLateral, b"maximumWidth")
        self.animation_sidebar.setDuration(200)
        self.botonOcultarMenu.clicked.connect(self.hideMenuLateral)

        
        self.verticalLayout = QVBoxLayout(self.menuLateral)
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        self.menualto.setStyleSheet("""
        QFrame{
            background-color: #f0f0f0;
            border: 1px solid rgb(200, 200, 200);
        }                  
        """)
        self.menuLateral.setStyleSheet("""
        QLabel{
           color: #2c3e50;
           font-family: 'Segoe UI';
           font-size: 14px;
           border-radius: 5px;
        }
        QFrame{
            background-color: #f0f0f0;
            border: 1px solid rgb(200, 200, 200);
            
        }  
        """)
        self.label_7.setStyleSheet("""
        QLabel {
           color: #2c3e50;
           font-family: 'segoe UI';
           font-size: 20px;
           border: none;
           }
        """)
        self.label_8.setStyleSheet("""
        QLabel {
           color: #2c3e50;
           font-family: 'Segoe UI';
           font-size: 14px;
           border-radius: 5px;
           }
        """)
        self.label_2 = senal(self.menuLateral)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setCursor(Qt.PointingHandCursor)
        self.label_2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_2.setAttribute(Qt.WA_Hover)
        self.label_2.setMouseTracking(True)
        self.label_2.setEnabled(True)
        self.label_2.setStyleSheet("""
        QLabel {
            padding: 10px;
            height; 30px;
            width: 180px;
                                 
                                   """)
        

        self.verticalLayout.addWidget(self.label_2)

        self.label_3 = senal(self.menuLateral)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.label_4 = senal(self.menuLateral)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.label_5 = senal(self.menuLateral)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)

        self.label = senal(self.menuLateral)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)


        self.gridLayout_2.addWidget(self.menuLateral, 1, 0, 2, 1)


        self.gridLayout.addWidget(self.widget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 793, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.label_2.clicked.connect(self.abrir_productos)
        self.label_3.clicked.connect(self.abrir_ventas)
        self.label_4.clicked.connect(self.abrir_compras)
        self.label_5.clicked.connect(self.abrir_Obras) 
        self.label.clicked.connect(self.abrir_Empleados)

    
        labels_menu = [self.label_2, self.label_3, self.label_4, self.label_5, self.label]
        
        estilo_labels = """
        QLabel {
            padding: 0px;
            margin: 0px;
            height: 30px;
            width: 180px;
            font-size: 14px;
          }
             """

        for label in labels_menu:
            label.setStyleSheet(estilo_labels)
            label.setFixedHeight(30)

        
        QMetaObject.connectSlotsByName(MainWindow)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'formulario_nueva_venta'):
            ancho_formulario = self.formulario_nueva_venta.width()
            alto_formulario = self.height()
            self.formulario_nueva_venta.setGeometry(
                self.width() - ancho_formulario, 0,
                ancho_formulario, alto_formulario
            )

    
   # setupUi
    def hideMenuLateral(self):
        if self.menuLateral.maximumWidth() == 0:
            self.animation_sidebar.setStartValue(0)
            self.animation_sidebar.setEndValue(200)
            self.animation_sidebar.start()
        else:
            self.animation_sidebar.setStartValue(self.menuLateral.maximumWidth())
            self.animation_sidebar.setEndValue(0)
            self.animation_sidebar.start()

        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Productos", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Ventas", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Compras", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Obras", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"RODLER ", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"usuario", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Empleados", None))
    # retranslateUi

    def abrir_productos(self):
        if hasattr(self, "paginaProductos") and self.stackedWidget.currentWidget() == self.paginaProductos:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaProductos'):
                self.paginaProductos = QWidget()
                self.productos_ui = Ui_Form()
                self.productos_ui.setupUi(self.paginaProductos)
                self.stackedWidget.addWidget(self.paginaProductos)


            self.stackedWidget.setCurrentWidget(self.paginaProductos)
        
    def abrir_ventas(self):
        if hasattr(self,'paginaVentas') and self.stackedWidget.currentWidget() == self.paginaVentas:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaVentas'): 
                self.paginaVentas = QWidget()
                self.ventasUi = ventasForm()
                self.ventasUi.setupUi(self.paginaVentas)
                self.stackedWidget.addWidget(self.paginaVentas)

            self.stackedWidget.setCurrentWidget(self.paginaVentas)
    
    def abrir_compras(self):
        if hasattr(self, 'paginaCompras') and self.stackedWidget.currentWidget() == self.paginaCompras:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaCompras'):
                self.paginaCompras = QWidget()
                self.compras_ui = ComprasUiForm()
                self.compras_ui.setupUi(self.paginaCompras)
        
                self.stackedWidget.addWidget(self.paginaCompras)
            self.stackedWidget.setCurrentWidget(self.paginaCompras)
    
    def abrir_Obras(self):
        if hasattr (self, 'paginaObras') and self.stackedWidget.currentWidget() == self.paginaObras:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaObras'):
                self.paginaObras = QWidget()
                self.compras_ui = ObrasUiForm()
                self.compras_ui.setupUi(self.paginaObras)

                self.stackedWidget.addWidget(self.paginaObras)
            self.stackedWidget.setCurrentWidget(self.paginaObras)
    
    def abrir_Empleados(self):
        if hasattr(self, 'paginaCompras') and self.stackedWidget.currentWidget() == self.paginaCompras:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaCompras'):
                self.paginaCompras = QWidget()
                self.compras_ui = ComprasUiForm()
                self.compras_ui.setupUi(self.paginaCompras)

                self.stackedWidget.addWidget(self.paginaCompras)
            self.stackedWidget.setCurrentWidget(self.paginaCompras)
            
            
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
    


