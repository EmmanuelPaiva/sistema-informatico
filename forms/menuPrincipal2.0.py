# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menuPrincipal2.0.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QWidget, QStackedWidget)
from productos import Ui_Form as ProductosUiForm
from Ventas import Ui_Form as VentasUiForm
from compras import Ui_Form as ComprasUiForm
from Obras import Ui_Form as ObrasUiForm

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(793, 500)
        self.centralwidget = QWidget(MainWindow)
        
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.gridLayout_2 = QGridLayout(self.widget)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
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
        self.label = QLabel(self.menualto)
        self.label.setObjectName(u"label")
        
        self.gridLayoutPaginaPrincipal = QGridLayout(self.centralwidget)
        self.PaginaPrincipal = QWidget()
        
        self.stackedWidget.addWidget(self.PaginaPrincipal)

        self.horizontalLayout_4.addWidget(self.label)
        
        
        self.paginaPrincipal = QWidget()
        self.stackedWidget = QStackedWidget(self.widget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.gridLayoutPaginaPrincipal = QGridLayout(self.centralwidget)
        self.PaginaPrincipal = QWidget()
        
        self.stackedWidget.addWidget(self.PaginaPrincipal)

        self.label_2 = QLabel(self.menualto)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.label_3 = QLabel(self.menualto)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.label_4 = QLabel(self.menualto)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.label_5 = QLabel(self.menualto)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_4.addWidget(self.label_5)


        self.horizontalLayout_3.addWidget(self.menualto)


        self.gridLayout_2.addWidget(self.contenedorMenuAlto, 0, 0, 1, 3)

        self.contenedorExcel = QWidget(self.widget)
        self.contenedorExcel.setObjectName(u"contenedorExcel")
        self.horizontalLayout_2 = QHBoxLayout(self.contenedorExcel)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.formularioExcel = QFrame(self.contenedorExcel)
        self.formularioExcel.setObjectName(u"formularioExcel")
        self.formularioExcel.setFrameShape(QFrame.Shape.StyledPanel)
        self.formularioExcel.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_2.addWidget(self.formularioExcel)


        self.gridLayout_2.addWidget(self.contenedorExcel, 2, 0, 1, 3)

        self.contenedorGrafico1 = QWidget(self.widget)
        self.contenedorGrafico1.setObjectName(u"contenedorGrafico1")
        self.horizontalLayout = QHBoxLayout(self.contenedorGrafico1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.grafico1 = QFrame(self.contenedorGrafico1)
        self.grafico1.setObjectName(u"grafico1")
        self.grafico1.setFrameShape(QFrame.Shape.StyledPanel)
        self.grafico1.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout.addWidget(self.grafico1)


        self.gridLayout_2.addWidget(self.contenedorGrafico1, 1, 2, 1, 1)

        self.conetenedorEstadisticas1 = QWidget(self.widget)
        self.conetenedorEstadisticas1.setObjectName(u"conetenedorEstadisticas1")
        self.gridLayout_3 = QGridLayout(self.conetenedorEstadisticas1)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.estadisticas1 = QFrame(self.conetenedorEstadisticas1)
        self.estadisticas1.setObjectName(u"estadisticas1")
        self.estadisticas1.setFrameShape(QFrame.Shape.StyledPanel)
        self.estadisticas1.setFrameShadow(QFrame.Shadow.Raised)

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


        self.gridLayout_2.addWidget(self.conetenedorEstadisticas1, 1, 0, 1, 1)


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

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Productos", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Ventas", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Compras", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Obras", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Empleados", None))
    # retranslateUi
    
    def abrir_productos(self):
        if hasattr(self, "paginaProductos") and self.stackedWidget.currentWidget() == self.paginaProductos:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaProductos'):
                self.paginaProductos = QWidget()
                self.productos_ui = ProductosUiForm()
                self.productos_ui.setupUi(self.paginaProductos)
                self.stackedWidget.addWidget(self.paginaProductos)


            self.stackedWidget.setCurrentWidget(self.paginaProductos)
        
    def abrir_ventas(self):
        if hasattr(self,'paginaVentas') and self.stackedWidget.currentWidget() == self.paginaVentas:
            self.stackedWidget.setCurrentWidget(self.PaginaPincipal)
        else:
            if not hasattr(self, 'paginaVentas'): 
                self.paginaVentas = QWidget()
                self.ventas_ui = VentasUiForm()
                self.ventas_ui.setupUi(self.paginaVentas)
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
