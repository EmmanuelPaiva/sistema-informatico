
import pandas as pd
import psycopg2
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt5.QtWidgets import QFileDialog, QMessageBox


def exportar_desde_postgresql(tipo, conexion, consulta_sql, parent=None):
    try:
        conn = psycopg2.connect(**conexion)
        cursor = conn.cursor()
        cursor.execute(consulta_sql)
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
        productos = [dict(zip(columnas, fila)) for fila in datos]
        cursor.close()
        conn.close()
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"No se pudo conectar a la base de datos:\n{e}")
        return

    if tipo == "excel":
        archivo, _ = QFileDialog.getSaveFileName(parent, "Guardar Excel", "", "Excel Files (*.xlsx)")
        if archivo:
            if not archivo.endswith(".xlsx"):
                archivo += ".xlsx"
            pd.DataFrame(productos).to_excel(archivo, index=False)
            QMessageBox.information(parent, "Éxito", "Exportado a Excel correctamente ✅")

    elif tipo == "pdf":
        archivo, _ = QFileDialog.getSaveFileName(parent, "Guardar PDF", "", "PDF Files (*.pdf)")
        if archivo:
            if not archivo.endswith(".pdf"):
                archivo += ".pdf"
            c = canvas.Canvas(archivo, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, height - 50, "Listado de Productos")
            c.setFont("Helvetica", 12)
            y = height - 100
            for producto in productos:
                texto = " - ".join([f"{k}: {v}" for k, v in producto.items()])
                c.drawString(50, y, texto)
                y -= 20
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 50
            c.save()
            QMessageBox.information(parent, "Éxito", "Exportado a PDF correctamente ✅")
