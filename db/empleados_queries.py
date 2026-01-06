# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize
from functools import partial
from db.conexion import conexion
from forms.ui_helpers import style_edit_button, style_delete_button

def guardar_registro(ui_nuevo_cliente, form_widget, tableWidget, edit_callback, main_form_widget):
    """
    Guarda un nuevo cliente en la BD y recarga la tabla.
    Reglas:
     - nombre, ruc_ci y telefono obligatorios
     - no pueden existir dos clientes con el mismo ruc_ci (si ruc_ci no vacío)
    """
    nombre = ui_nuevo_cliente.lineEditNombre.text().strip()
    ruc_ci = ui_nuevo_cliente.lineEditRuc_Ci.text().strip()
    telefono = ui_nuevo_cliente.lineEditTelefono.text().strip()
    email = ui_nuevo_cliente.lineEditCorreo.text().strip()

    # Validaciones obligatorias
    if not nombre or not ruc_ci or not telefono:
        QMessageBox.warning(form_widget, "Campos obligatorios", "Nombre, RUC/CI y teléfono son obligatorios.")
        return

    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        # Validar duplicado por ruc_ci (case-insensitive)
        query = "SELECT 1 FROM clientes WHERE LOWER(ruc_ci) = %s"
        cursor.execute(query, (ruc_ci.lower(),))
        if cursor.fetchone():
            QMessageBox.warning(form_widget, "RUC/CI duplicado", "Ya existe un cliente con ese RUC/CI.")
            return

        # Insertar nuevo cliente
        query_insert = """INSERT INTO clientes (nombre, email, telefono, ruc_ci)
                          VALUES (%s, %s, %s, %s)"""
        cursor.execute(query_insert, (nombre, email, telefono, ruc_ci))
        conexion_db.commit()

        QMessageBox.information(form_widget, "Éxito", "Cliente guardado correctamente.")
        form_widget.close()

        # Recargar tabla
        cargar_clientes(tableWidget, edit_callback=edit_callback, main_form_widget=main_form_widget)

    except Exception as e:
        try:
            if conexion_db:
                conexion_db.rollback()
        except Exception:
            pass
        QMessageBox.critical(form_widget, "Error", f"No se pudo guardar el cliente.\n{str(e)}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def cargar_clientes(tableWidget, edit_callback=None, main_form_widget=None):
    """Carga todos los clientes en el tableWidget y conecta los botones de editar/eliminar."""
    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        tableWidget.setRowCount(0)

        cursor.execute("SELECT id, nombre, telefono, ruc_ci, email FROM clientes ORDER BY id")
        clientes = cursor.fetchall()

        for cliente in clientes:
            row_number = tableWidget.rowCount()
            tableWidget.insertRow(row_number)

            id_cli, nombre, telefono, ruc_ci, email = cliente
            tableWidget.setItem(row_number, 0, QTableWidgetItem(str(id_cli)))
            tableWidget.setItem(row_number, 1, QTableWidgetItem(nombre))
            tableWidget.setItem(row_number, 2, QTableWidgetItem(str(telefono) if telefono is not None else ""))
            tableWidget.setItem(row_number, 3, QTableWidgetItem(str(ruc_ci) if ruc_ci is not None else ""))
            tableWidget.setItem(row_number, 4, QTableWidgetItem(email if email is not None else ""))

            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            boton_editar = QPushButton()
            boton_editar.setObjectName("btnEmpleadoEditar")
            boton_editar.setProperty("perm_code", "empleados.update")
            boton_editar.setIconSize(QSize(18, 18))
            style_edit_button(boton_editar, "Editar empleado")

            boton_eliminar = QPushButton()
            boton_eliminar.setObjectName("btnEmpleadoEliminar")
            boton_eliminar.setProperty("perm_code", "empleados.delete")
            boton_eliminar.setIconSize(QSize(18, 18))
            style_delete_button(boton_eliminar, "Eliminar empleado")

            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
            tableWidget.setCellWidget(row_number, 5, contenedor)
            
            # Conectar botones por fila (bind de id_cli)
            if edit_callback and main_form_widget is not None:
                boton_editar.clicked.connect(partial(edit_callback, main_form_widget, id_cli))
            else:
                boton_editar.clicked.connect(lambda: None)

            boton_eliminar.clicked.connect(partial(eliminar_cliente, id_cli, tableWidget))

    except Exception as e:
        print(f"Error al cargar clientes: {e}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def buscar_clientes(texto, tableWidget, edit_callback=None, main_form_widget=None):
    """
    Busca por nombre (LIKE) o por ruc_ci exact/LIKE y actualiza el tableWidget.
    Se usa LOWER(...) para búsquedas case-insensitive.
    """
    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        tableWidget.setRowCount(0)

        texto = texto.strip()
        # Si la barra de búsqueda está vacía, cargamos todos
        if texto == "":
            cursor.execute("SELECT id, nombre, telefono, ruc_ci, email FROM clientes ORDER BY id")
            resultados = cursor.fetchall()
        else:
            # Buscamos por nombre (LIKE) o por ruc_ci (exacto o LIKE)
            pattern = f"%{texto.lower()}%"
            query = """
                SELECT id, nombre, telefono, ruc_ci, email
                FROM clientes
                WHERE LOWER(nombre) LIKE %s OR LOWER(ruc_ci) LIKE %s
                ORDER BY id
            """
            cursor.execute(query, (pattern, pattern))
            resultados = cursor.fetchall()

        for cliente in resultados:
            row_number = tableWidget.rowCount()
            tableWidget.insertRow(row_number)

            id_cli, nombre, telefono, ruc_ci, email = cliente
            tableWidget.setItem(row_number, 0, QTableWidgetItem(str(id_cli)))
            tableWidget.setItem(row_number, 1, QTableWidgetItem(nombre))
            tableWidget.setItem(row_number, 2, QTableWidgetItem(str(telefono) if telefono is not None else ""))
            tableWidget.setItem(row_number, 3, QTableWidgetItem(str(ruc_ci) if ruc_ci is not None else ""))
            tableWidget.setItem(row_number, 4, QTableWidgetItem(email if email is not None else ""))

            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            boton_editar = QPushButton()
            boton_editar.setObjectName("btnEmpleadoEditar")
            boton_editar.setProperty("perm_code", "empleados.update")
            boton_editar.setIconSize(QSize(18, 18))
            style_edit_button(boton_editar, "Editar empleado")

            boton_eliminar = QPushButton()
            boton_eliminar.setObjectName("btnEmpleadoEliminar")
            boton_eliminar.setProperty("perm_code", "empleados.delete")
            boton_eliminar.setIconSize(QSize(18, 18))
            style_delete_button(boton_eliminar, "Eliminar empleado")

            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
            tableWidget.setCellWidget(row_number, 5, contenedor)

            if edit_callback and main_form_widget is not None:
                boton_editar.clicked.connect(partial(edit_callback, main_form_widget, id_cli))
            else:
                boton_editar.clicked.connect(lambda: None)

            boton_eliminar.clicked.connect(partial(eliminar_cliente, id_cli, tableWidget))

    except Exception as e:
        print(f"Error al buscar clientes: {e}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def editar_cliente(ui_nuevo_cliente, tableWidget, id_cliente, form_widget, edit_callback, main_form_widget):
    """
    Actualiza un cliente y recarga la tabla.
    Respeta las mismas validaciones de campo obligatorio y evita duplicados de ruc_ci
    (excepto si el ruc_ci pertenece al mismo registro).
    """
    nombre = ui_nuevo_cliente.lineEditNombre.text().strip()
    ruc_ci = ui_nuevo_cliente.lineEditRuc_Ci.text().strip()
    telefono = ui_nuevo_cliente.lineEditTelefono.text().strip()
    email = ui_nuevo_cliente.lineEditCorreo.text().strip()
    
    if not nombre or not ruc_ci or not telefono:
        QMessageBox.warning(form_widget, "Campos obligatorios", "Nombre, RUC/CI y teléfono son obligatorios.")
        return

    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        # Verificar duplicado de ruc_ci en otro id distinto
        cursor.execute("SELECT id FROM clientes WHERE LOWER(ruc_ci) = %s AND id <> %s", (ruc_ci.lower(), id_cliente))
        if cursor.fetchone():
            QMessageBox.warning(form_widget, "RUC/CI duplicado", "Otro cliente ya tiene ese RUC/CI.")
            return

        cursor.execute(
            """
            UPDATE clientes
            SET nombre = %s, 
                email = %s,
                telefono = %s,
                ruc_ci = %s
            WHERE id = %s
            """,
            (nombre, email, telefono, ruc_ci, id_cliente)
        )
        conexion_db.commit()
        
        QMessageBox.information(form_widget, "Éxito", "Cliente actualizado correctamente.")
        form_widget.close()

        # Recargar tabla
        cargar_clientes(tableWidget, edit_callback=edit_callback, main_form_widget=main_form_widget)

    except Exception as e:
        try:
            if conexion_db:
                conexion_db.rollback()
        except Exception:
            pass
        QMessageBox.critical(form_widget, "Error", f"No se pudo actualizar el cliente.\n{str(e)}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def eliminar_cliente(id_cliente, tableWidget):
    confirm = QMessageBox.question(None, "Eliminar", "¿Estás seguro de eliminar este cliente?",
        QMessageBox.Yes | QMessageBox.No)
    if confirm == QMessageBox.Yes:
        conexion_db = None
        cursor = None
        try:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s;", (id_cliente,))
            conexion_db.commit()
        
            for fila in range(tableWidget.rowCount()):
                item = tableWidget.item(fila, 0)
                if item and int(item.text()) == id_cliente:
                    tableWidget.removeRow(fila)
                    break

        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo eliminar el cliente.\n{str(e)}")

        finally:
            try:
                if cursor:
                    cursor.close()
                if conexion_db:
                    conexion_db.close()
            except Exception:
                pass


def obtener_cliente_por_id(id_cliente):
    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("SELECT id, nombre, email, telefono, ruc_ci FROM clientes WHERE id = %s;", (id_cliente,))
        cliente = cursor.fetchone()
        return cliente
    except Exception as e:
        print(f"Error al obtener cliente: {e}")
        return None
    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass
