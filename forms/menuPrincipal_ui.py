# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menuPrincipal.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

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

        self.contenedorExcel = QWidget(self.widget)
        self.contenedorExcel.setObjectName(u"contenedorExcel")
        self.horizontalLayout_2 = QHBoxLayout(self.contenedorExcel)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.formularioExcel = QFrame(self.contenedorExcel)
        self.formularioExcel.setObjectName(u"formularioExcel")
        self.formularioExcel.setFrameShape(QFrame.Shape.StyledPanel)
        self.formularioExcel.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_2.addWidget(self.formularioExcel)


        self.gridLayout_2.addWidget(self.contenedorExcel, 2, 1, 1, 2)

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


        self.gridLayout_2.addWidget(self.conetenedorEstadisticas1, 1, 1, 1, 1)

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

        self.horizontalLayout_4.addWidget(self.label_7)

        self.label_8 = QLabel(self.menualto)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_4.addWidget(self.label_8)


        self.horizontalLayout_3.addWidget(self.menualto)


        self.gridLayout_2.addWidget(self.contenedorMenuAlto, 0, 0, 1, 3)

        self.menuLateral = QWidget(self.widget)
        self.menuLateral.setObjectName(u"menuLateral")
        self.menuLateral.setMaximumSize(QSize(140, 16777215))
        self.verticalLayout = QVBoxLayout(self.menuLateral)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(self.menuLateral)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.label_3 = QLabel(self.menuLateral)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.label_4 = QLabel(self.menuLateral)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.label_5 = QLabel(self.menuLateral)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)

        self.label = QLabel(self.menuLateral)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.label_6 = QLabel(self.menuLateral)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout.addWidget(self.label_6)


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

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"RODLER ", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"usuario", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Productos", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Ventas", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Compras", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Obras", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Proveedores", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Empleados", None))
    # retranslateUi

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())