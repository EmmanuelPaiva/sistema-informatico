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
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QSizePolicy, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QGraphicsDropShadowEffect)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(970, 638)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        
        self.frame_2 = QFrame(Form)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        self.frame_barra_superior = QFrame(self.frame_2)
        self.frame_barra_superior.setMaximumSize(16777215, 50)
        self.frame_barra_superior.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_barra_superior.setFrameShadow(QFrame.Shadow.Raised)
        self.barra_superior_layout = QHBoxLayout(self.frame_barra_superior)
        
        self.label_ventas = QLabel(self.frame_barra_superior)
        self.label_ventas.setText("Ventas")
        self.label_ventas.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.barra_superior_layout.addWidget(self.label_ventas, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.boton_agregar_producto = QPushButton(self.frame_barra_superior)
        self.boton_agregar_producto.setText("Agregar Producto")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.boton_agregar_producto.setGraphicsEffect(shadow)
        self.barra_superior_layout.addWidget(self.boton_agregar_producto, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.verticalLayout.addWidget(self.frame_barra_superior)
        
        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame_4)
        

        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame_5)
        

        self.frame_6 = QFrame(self.frame_2)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame_6)


        self.gridLayout.addWidget(self.frame_2, 1, 1, 1, 2)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
    # retranslateUi
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())

