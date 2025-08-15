import sys  
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QPropertyAnimation)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget, QTreeWidget, QHeaderView, QHBoxLayout)
from forms.formularioVentas import Ui_Form as nuevaCompraUi
from db.conexion import conexion
from db.compras_queries import agrega_prodcuto_a_fila, reiniciar_tabla_productos, obtener_productos_por_proveedor, SaveSellIntoDb, setRowsTreeWidget, on_proveedor_selected, validar_filas_por_proveedor
from utils.utilsCompras import borrar_fila
class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(868, 646)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_4 = QFrame(Form)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMaximumSize(QSize(16777215, 16777215))
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_4)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.gridLayout.addWidget(self.frame_4, 2, 0, 2, 1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)  # quita márgenes laterales


        self.frame_3 = QFrame(Form)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMaximumSize(QSize(16777215, 80))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        
                                         

        # Cambiamos de GridLayout a HorizontalLayout
        self.horizontalLayout = QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(16, 16, 16, 16)
        self.labelCompras = QLabel(self.frame_3)
        self.labelCompras.setObjectName(u"labelCompras")
        self.labelCompras.setStyleSheet("font-size: 24px; font-weight: bold; color: #003366;")

        # Botones
        self.pushButtonNuevaCompra = QPushButton(self.frame_3)
        self.pushButtonNuevaCompra.setObjectName(u"pushButtonNuevaCompra")
        self.pushButtonNuevaCompra.setText("Agregar Compra")
        self.pushButtonNuevaCompra.setStyleSheet("background-color: #0066cc; color: white; padding: 8px 16px; border-radius: 8px;")
        self.pushButtonNuevaCompra.clicked.connect(lambda: self.abrir_formulario_nueva_compra(Form))

        self.pushButtonExportar = QPushButton(self.frame_3)
        self.pushButtonExportar.setObjectName(u"pushButtonExportar")
        self.pushButtonExportar.setText("Exportar")
        self.pushButtonExportar.setStyleSheet("background-color: #00b3b3; color: white; padding: 8px 16px; border-radius: 8px;")

        # Añadir al layout con stretch
        self.horizontalLayout.addWidget(self.labelCompras)
        self.horizontalLayout.addStretch()  # empuja los botones a la derecha
        self.horizontalLayout.addWidget(self.pushButtonNuevaCompra)
        self.horizontalLayout.addWidget(self.pushButtonExportar)

        # Añadir a la grilla principal
        self.gridLayout.addWidget(self.frame_3, 1, 0, 1, 1)


        self.retranslateUi(Form)
        
        self.treeWidget = QTreeWidget(Form)
        self.treeWidget.setObjectName(u"treeWidget")

        self.gridLayout.addWidget(self.treeWidget, 3, 0, 1, 4)
        
        self.treeWidget.setColumnCount(7)
        self.treeWidget.setHeaderLabels(["ID","Fecha", "Proveedor", "Total","Medio","Factura","Opciones"])
        self.treeWidget.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.treeWidget.setColumnHidden(0, True)
        header = self.treeWidget.header()
        header.setSectionResizeMode(QHeaderView.Stretch) 
        self.treeWidget.setColumnWidth(5, 50)  # achicamos Factura
        
        

        QMetaObject.connectSlotsByName(Form)
        
        setRowsTreeWidget(self, Form)
        
        
        Form.setStyleSheet("""
            QWidget {
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
                background-color: #f9fbfd;
            }

            /* Controles */
            QLineEdit, QDateTimeEdit, QComboBox {
                padding: 8px;
                border: 1px solid #b0c4de;
                border-radius: 8px;
                background-color: #ffffff;
            }

            QLineEdit:focus, QDateTimeEdit:focus, QComboBox:focus {
                border: 1px solid #5dade2;
                background-color: #eef7ff;
            }

            /* Botones */
            QPushButton {
                padding: 10px 18px;
                background-color: #5dade2;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }

            QPushButton:hover {
                background-color: #3498db;
            }

            QPushButton:pressed {
                background-color: #2e86c1;
            }

            /* Labels */
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }

            /* Tabla */
            QTreeWidget {
                border: 1px solid #d6eaf8;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #d0d0d0;
            }

            QTreeWidget::item {
                padding: 6px;
                font-size: 12px;
                color: #333333;
                height: 40px;
            }

            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-size: 13px;
            }

            QTreeWidget QTableCornerButton::section {
                background-color: #3498db;
            }

            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #a0c4ff;
                min-height: 20px;
                border-radius: 4px;
            }

            """)
             
    # setupUi
    def cancelar(self, Form):
        if hasattr(self, 'formulario_nueva_venta'):
            self.formulario_nueva_compra.close()
        
        ancho_formulario = 300
        alto_formulario = Form.height()

        self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.start()
    

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButtonNuevaCompra.setText(QCoreApplication.translate("Form", u"Nueva compra", None))
        self.pushButtonExportar.setText(QCoreApplication.translate("Form", u"Exportar", None))
        self.labelCompras.setText(QCoreApplication.translate("Form", u"Compras", None))
    # retranslateUi

    
    def abrir_formulario_nueva_compra(self, Form, edicion = False):
        if hasattr(self, 'formulario_nueva_compra') and self.formulario_nueva_compra.isVisible():
          return  # ya está abierto
        
        self.ui_nueva_compra = nuevaCompraUi()
        self.formulario_nueva_compra = QWidget(Form)  # o el contenedor principal
        self.ui_nueva_compra.setupUi(self.formulario_nueva_compra)
        
        self.ui_nueva_compra.labelCliente.setText("Proveedor")
        
        agrega_prodcuto_a_fila
        (self.ui_nueva_compra)
      
        
        ancho_formulario = 450 
        alto_formulario = Form.height()


        # Posición inicial fuera de pantalla (izquierda)
        self.formulario_nueva_compra.setGeometry(Form.width(), 0, ancho_formulario, alto_formulario)
        self.formulario_nueva_compra.show()

        # Animación para deslizar
        self.anim = QPropertyAnimation(self.formulario_nueva_compra, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(Form.width(), 0, ancho_formulario, alto_formulario))
        self.anim.setEndValue(QRect(Form.width() - ancho_formulario, 0, ancho_formulario, alto_formulario))
        self.anim.start()
        
        if not edicion:
            conexion_db = conexion() 
            cursor = conexion_db.cursor()
            cursor.execute("SELECT id_proveedor, nombre FROM proveedores;")
            proveedores = cursor.fetchall()

            for idP, nombreP in proveedores:
                self.ui_nueva_compra.comboBox.addItem(nombreP, idP)
            if self.ui_nueva_compra.comboBox.count() > 0:
                self.ui_nueva_compra.comboBox.setCurrentIndex(0)
            self.ui_nueva_compra.comboBox.currentIndexChanged.connect(lambda: reiniciar_tabla_productos(self.ui_nueva_compra))
            proveedor_id = self.ui_nueva_compra.comboBox.currentData()
            self.ui_nueva_compra.comboBox.currentIndexChanged.connect(lambda: on_proveedor_selected(self.ui_nueva_compra))

            cursor.close()
            conexion_db.close()
            
            
        self.ui_nueva_compra.pushButtonCancelar.clicked.connect(lambda: self.cancelar(Form))
        self.ui_nueva_compra.pushButtonAgregarProducto.clicked.connect(lambda: agrega_prodcuto_a_fila(self.ui_nueva_compra))
        self.ui_nueva_compra.pushButtonQuitarProducto.clicked.connect(lambda: borrar_fila(self.ui_nueva_compra))
        self.ui_nueva_compra.pushButtonAceptar.clicked.connect(lambda: SaveSellIntoDb(self.ui_nueva_compra, ui ,Form))




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())