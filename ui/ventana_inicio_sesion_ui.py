# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ventana_inicio_sesion.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(841, 607)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalWidget_2 = QWidget(self.centralwidget)
        self.verticalWidget_2.setObjectName(u"verticalWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalWidget_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.verticalWidget_2)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(16777215, 200))
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.labelHead = QLabel(self.widget)
        self.labelHead.setObjectName(u"labelHead")
        self.labelHead.setStyleSheet(u"font: 68pt \"Script\";\n"
"font: 72pt \"Rockwell\";")

        self.horizontalLayout_3.addWidget(self.labelHead, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_2.addWidget(self.widget)

        self.LabelUsuario = QLabel(self.verticalWidget_2)
        self.LabelUsuario.setObjectName(u"LabelUsuario")
        self.LabelUsuario.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.LabelUsuario, 0, Qt.AlignmentFlag.AlignHCenter)

        self.widget1 = QWidget(self.verticalWidget_2)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_2 = QHBoxLayout(self.widget1)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.LineEditUsuario = QLineEdit(self.widget1)
        self.LineEditUsuario.setObjectName(u"LineEditUsuario")
        self.LineEditUsuario.setMaximumSize(QSize(400, 16777215))

        self.horizontalLayout_2.addWidget(self.LineEditUsuario)


        self.verticalLayout_2.addWidget(self.widget1)

        self.LabelContrasena = QLabel(self.verticalWidget_2)
        self.LabelContrasena.setObjectName(u"LabelContrasena")
        self.LabelContrasena.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.LabelContrasena, 0, Qt.AlignmentFlag.AlignHCenter)

        self.widget_3 = QWidget(self.verticalWidget_2)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_6 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.lineEditContrasena = QLineEdit(self.widget_3)
        self.lineEditContrasena.setObjectName(u"lineEditContrasena")
        self.lineEditContrasena.setMaximumSize(QSize(400, 16777215))

        self.horizontalLayout_6.addWidget(self.lineEditContrasena)


        self.verticalLayout_2.addWidget(self.widget_3)

        self.widget2 = QWidget(self.verticalWidget_2)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout = QHBoxLayout(self.widget2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.BotonIniciarSesion = QPushButton(self.widget2)
        self.BotonIniciarSesion.setObjectName(u"BotonIniciarSesion")
        self.BotonIniciarSesion.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout.addWidget(self.BotonIniciarSesion)


        self.verticalLayout_2.addWidget(self.widget2)

        self.widget3 = QWidget(self.verticalWidget_2)
        self.widget3.setObjectName(u"widget3")
        self.widget3.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout_2.addWidget(self.widget3)


        self.verticalLayout_3.addWidget(self.verticalWidget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 841, 33))
        self.menurodler = QMenu(self.menubar)
        self.menurodler.setObjectName(u"menurodler")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menurodler.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.labelHead.setText(QCoreApplication.translate("MainWindow", u"RODLER E.A.S", None))
        self.LabelUsuario.setText(QCoreApplication.translate("MainWindow", u"Usuario", None))
        self.LabelContrasena.setText(QCoreApplication.translate("MainWindow", u"Contrase\u00f1a", None))
        self.BotonIniciarSesion.setText(QCoreApplication.translate("MainWindow", u"INICIAR", None))
        self.menurodler.setTitle(QCoreApplication.translate("MainWindow", u"rodler", None))
    # retranslateUi

