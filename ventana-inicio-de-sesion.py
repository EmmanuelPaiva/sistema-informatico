# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ventana-inicio-de-sesion.ui'
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
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1080, 526)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalWidget_2 = QWidget(self.centralwidget)
        self.verticalWidget_2.setObjectName(u"verticalWidget_2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.verticalWidget_2)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 150))

        self.verticalLayout_2.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_usuario = QLabel(self.verticalWidget_2)
        self.label_usuario.setObjectName(u"label_usuario")
        self.label_usuario.setMaximumSize(QSize(16777215, 10))
        self.label_usuario.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_usuario.setLocale(QLocale(QLocale.Embu, QLocale.Kenya))

        self.verticalLayout_2.addWidget(self.label_usuario, 0, Qt.AlignmentFlag.AlignHCenter)

        self.widget = QWidget(self.verticalWidget_2)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit = QLineEdit(self.widget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMaximumSize(QSize(400, 16777215))

        self.horizontalLayout.addWidget(self.lineEdit)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addWidget(self.widget)

        self.label_contrasena = QLabel(self.verticalWidget_2)
        self.label_contrasena.setObjectName(u"label_contrasena")
        self.label_contrasena.setMaximumSize(QSize(16777215, 10))

        self.verticalLayout_2.addWidget(self.label_contrasena, 0, Qt.AlignmentFlag.AlignHCenter)

        self.widget_2 = QWidget(self.verticalWidget_2)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lineEdit_2 = QLineEdit(self.widget_2)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setMaximumSize(QSize(400, 16777215))

        self.horizontalLayout_3.addWidget(self.lineEdit_2)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addWidget(self.widget_2)


        self.verticalLayout_3.addWidget(self.verticalWidget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1080, 33))
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
        self.label.setText(QCoreApplication.translate("MainWindow", u"RODLER", None))
        self.label_usuario.setText(QCoreApplication.translate("MainWindow", u"usuario", None))
        self.label_contrasena.setText(QCoreApplication.translate("MainWindow", u"contrase\u00f1a", None))
        self.menurodler.setTitle(QCoreApplication.translate("MainWindow", u"rodler", None))
    # retranslateUi

import sys

app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec())  