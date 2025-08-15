# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QSize, QRect, QCoreApplication, QMetaObject
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(841, 607)
        MainWindow.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                color: #333;
            }
            QLabel#labelHead {
                font-size: 36px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel {
                font-size: 16px;
                color: #555;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                box-shadow: 0 0 5px rgba(52, 152, 219, 0.5);
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.centralwidget = QWidget(MainWindow)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        self.labelHead = QLabel("RODLER E.A.S", self.centralwidget)
        self.labelHead.setObjectName("labelHead")
        self.labelHead.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout.addWidget(self.labelHead)

        # Usuario
        self.LabelUsuario = QLabel("Usuario", self.centralwidget)
        self.LabelUsuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout.addWidget(self.LabelUsuario)

        self.LineEditUsuario = QLineEdit(self.centralwidget)
        self.LineEditUsuario.setMaximumWidth(400)
        self.verticalLayout.addWidget(self.LineEditUsuario, 0, Qt.AlignmentFlag.AlignHCenter)

        # Contraseña
        self.LabelContrasena = QLabel("Contraseña", self.centralwidget)
        self.LabelContrasena.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout.addWidget(self.LabelContrasena)

        self.lineEditContrasena = QLineEdit(self.centralwidget)
        self.lineEditContrasena.setMaximumWidth(400)
        self.lineEditContrasena.setEchoMode(QLineEdit.Password)
        self.verticalLayout.addWidget(self.lineEditContrasena, 0, Qt.AlignmentFlag.AlignHCenter)

        # Botón iniciar
        self.BotonIniciarSesion = QPushButton("INICIAR", self.centralwidget)
        self.BotonIniciarSesion.setMaximumWidth(200)
        self.verticalLayout.addWidget(self.BotonIniciarSesion, 0, Qt.AlignmentFlag.AlignHCenter)

        MainWindow.setCentralWidget(self.centralwidget)

        # Menú y barra de estado
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 841, 30))
        self.menurodler = QMenu("rodler", self.menubar)
        self.menubar.addAction(self.menurodler.menuAction())
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(MainWindow)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
