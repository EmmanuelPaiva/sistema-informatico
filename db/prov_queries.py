from PySide6.QtWidgets import QMessageBox, QTableWidgetItem
from db.conexion import conexion


def guardar_registro(ui_nuevo_proveedor, parent_widget):
    nombre = ui_nuevo_proveedor.lineEditNombre.text().strip()
    direccion = ui_nuevo_proveedor.lineEditDireccion.text().strip()
    telefono = ui_nuevo_proveedor.lineEditTelefono.text().strip()
    correo = ui_nuevo_proveedor.lineEditCorreo.text().strip()

    if not nombre or not correo or not telefono:
        QMessageBox.warning(parent_widget, "Campos obligatorios", "Todos los campos excepto dirección son obligatorios.")
        return

    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        # Validar duplicado
        query = """SELECT 1 FROM proveedores
                   WHERE LOWER(nombre) = %s OR LOWER(correo) = %s"""
        cursor.execute(query, (nombre.lower(), correo.lower()))
        if cursor.fetchone():
            QMessageBox.warning(parent_widget, "Proveedor duplicado", "Ya existe un proveedor con ese nombre o correo.")
            return

        # Insertar nuevo proveedor
        query_insert = """INSERT INTO proveedores (nombre, telefono, direccion, correo)
                          VALUES (%s, %s, %s, %s)"""
        cursor.execute(query_insert, (nombre, telefono, direccion, correo))
        conexion_db.commit()

        QMessageBox.information(parent_widget, "Éxito", "Proveedor guardado correctamente.")
        parent_widget.close()
        cargar_proveedores(ui_nuevo_proveedor)

    except Exception as e:
        conexion_db.rollback()
        QMessageBox.critical(parent_widget, "Error", f"No se pudo guardar el proveedor.\n{str(e)}")

    finally:
        cursor.close()
        conexion_db.close()
    
def cargar_proveedores(ui):
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        ui.tableWidget.setRowCount(0)
        cursor.execute("SELECT nombre, correo, telefono, direccion FROM proveedores ORDER BY nombre")
        proveedores = cursor.fetchall()

        for row_data in proveedores:
            row_number = ui.tableWidget.rowCount()
            ui.tableWidget.insertRow(row_number)
            for col, data in enumerate(row_data):
                ui.tableWidget.setItem(row_number, col, QTableWidgetItem(str(data)))

    except Exception as e:
        print(f"Error al cargar proveedores: {e}")

    finally:
        cursor.close()
        conexion_db.close()

    