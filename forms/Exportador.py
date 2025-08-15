import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Simulación de base de datos (podés reemplazar por tu consulta real)
productos = [
    {"nombre": "Galletitas", "precio": 3500, "stock": 20},
    {"nombre": "Leche", "precio": 7200, "stock": 15},
    {"nombre": "Pan", "precio": 2000, "stock": 50},
    {"nombre": "Coca-Cola", "precio": 10000, "stock": 10}
]

# ---------- FUNCIONES DE EXPORTACIÓN ----------

def exportar_a_excel(productos, archivo):
    df = pd.DataFrame(productos)
    df.to_excel(archivo, index=False)
    print("📦 Exportado a Excel correctamente.")

def exportar_a_pdf(productos, archivo):
    c = canvas.Canvas(archivo, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Listado de Productos")

    c.setFont("Helvetica", 12)
    y = height - 100
    for producto in productos:
        texto = f"{producto['nombre']} - Gs. {producto['precio']} - Stock: {producto['stock']}"
        c.drawString(100, y, texto)
        y -= 20

    c.save()
    print("📄 Exportado a PDF correctamente.")

# ---------- INTERFAZ PYQT ----------

class Exportador(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exportar Productos")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        btn_excel = QPushButton("Exportar a Excel (.xlsx)")
        btn_excel.clicked.connect(self.guardar_excel)

        btn_pdf = QPushButton("Exportar a PDF (.pdf)")
        btn_pdf.clicked.connect(self.guardar_pdf)

        layout.addWidget(btn_excel)
        layout.addWidget(btn_pdf)

        self.setLayout(layout)

    def guardar_excel(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "", "Excel Files (*.xlsx)")
        if archivo:
            if not archivo.endswith(".xlsx"):
                archivo += ".xlsx"
            exportar_a_excel(productos, archivo)
            QMessageBox.information(self, "Éxito", "Exportado a Excel correctamente ✅")

    def guardar_pdf(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF Files (*.pdf)")
        if archivo:
            if not archivo.endswith(".pdf"):
                archivo += ".pdf"
            exportar_a_pdf(productos, archivo)
            QMessageBox.information(self, "Éxito", "Exportado a PDF correctamente ✅")

# ---------- MAIN ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Exportador()
    ventana.show()
    sys.exit(app.exec_())
