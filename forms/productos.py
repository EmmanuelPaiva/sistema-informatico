# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'productos.ui'
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
    QImage, QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform, QStandardItem, QStandardItemModel)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QTableView,QStyledItemDelegate,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1000, 600)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(80, 32)
        self.pushButton.setMaximumWidth(190)

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout.addWidget(self.frame)

        self.tableView = QTableView(Form)
        self.tableView.setObjectName(u"tableView")

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(Form)
        
        self.configurar_tabla()

        QMetaObject.connectSlotsByName(Form)

        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

        self.frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.frame.setMinimumHeight(0)
        self.frame.setStyleSheet("QFrame { border: none; padding: 0px; margin: 0px; background-color: #f0f0f0; }")
        self.horizontalLayout.setContentsMargins(100, 30, 50, 50)
        self.horizontalLayout.setSpacing(0)
        

        self.label.setStyleSheet("""
            QLabel { 
            margin: 0px;
            padding: 0px;
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold; 
           
            }
                                 """)
        self.pushButton.setStyleSheet("""
            QPushButton { 
            margin-right: 10px;
            padding: 4px 10px;
            border: none;
            background-color: #3498db;
            border-radius: 5px;
            
            
            }
                                      """)
        
        Form.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }            
                           """)
        self.tableView.setStyleSheet("""
            QTableView {
                background-color: #f0f0f0;
                border: none;
                gridline-color: #d0d0d0;
                color : #2c3e50;    
                gridline-color: transparent;
            }
            QTableView::item {
            border-bottom: 1px solid #d0d0d0;
            }                         """)
        self.tableView.horizontalHeader().setStyleSheet("""
             background-color: #f0f0f0;
             border: none;
             color: #2c3e50;
             font-weight: bold;                                           
                                                        """)

        
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Productos", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Agregar Producto", None))
    # retranslateUi

    def configurar_tabla(self):
        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels(["Nombre", "Precio", "Stock", "Proveedor", "opciones"])

        self.fila = [
            QStandardItem("Cemento"),
            QStandardItem("65.000"),
            QStandardItem("90"),
            QStandardItem("Acemar")
        ]
        for item in self.fila:
            item.setTextAlignment(Qt.AlignCenter) 

        self.tableView.setModel(self.modelo)
        #self.tableView.setColumnHidden(0, True)
        self.modelo.appendRow(self.fila)

        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.tableView.setEditTriggers(QTableView.NoEditTriggers)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(50)
        self.tableView.setItemDelegateForColumn(4, botonDelegate())
        
class botonDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        contenedor = QWidget(parent)
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0) 
        
        boton = QPushButton("Editar", contenedor)
        layout.addWidget(boton)
    
        boton.setStyleSheet("background-color: #000; color: black; border-radius: 5px; padding: 4px;")
        boton.clicked.connect(lambda: print(f"Botón clickeado en fila {index.row()}"))
        return contenedor
    
    def paint(self, painter, option, index):
       pass
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())

