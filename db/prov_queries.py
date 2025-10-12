# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
from functools import partial
from db.conexion import conexion


def guardar_registro(ui_nuevo_proveedor, form_widget, tableWidget, edit_callback, main_form_widget):
    """Guarda un nuevo proveedor en la BD y recarga la tabla.
    - ui_nuevo_proveedor: instancia del Ui del formulario (forms.agregarProveedor.Ui_Form)
    - form_widget: QWidget que contiene el formulario (se cerrará al guardar)
    - tableWidget: QTableWidget a recargar
    - edit_callback: función bound (por ejemplo ui.abrir_formulario_editar) para conectarla a los botones de editar
    - main_form_widget: el QWidget principal que será pasado a edit_callback cuando se haga click en editar
    """
    nombre = ui_nuevo_proveedor.lineEditNombre.text().strip()
    direccion = ui_nuevo_proveedor.lineEditDireccion.text().strip()
    telefono = ui_nuevo_proveedor.lineEditTelefono.text().strip()
    correo = ui_nuevo_proveedor.lineEditCorreo.text().strip()

    if not nombre or not correo or not telefono:
        QMessageBox.warning(form_widget, "Campos obligatorios", "Todos los campos excepto dirección son obligatorios.")
        return

    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        # Validar duplicado
        query = """SELECT 1 FROM proveedores
                   WHERE LOWER(nombre) = %s OR LOWER(correo) = %s"""
        cursor.execute(query, (nombre.lower(), correo.lower()))
        if cursor.fetchone():
            QMessageBox.warning(form_widget, "Proveedor duplicado", "Ya existe un proveedor con ese nombre o correo.")
            return

        # Insertar nuevo proveedor
        query_insert = """INSERT INTO proveedores (nombre, telefono, direccion, correo)
                          VALUES (%s, %s, %s, %s)"""
        cursor.execute(query_insert, (nombre, telefono, direccion, correo))
        conexion_db.commit()

        QMessageBox.information(form_widget, "Éxito", "Proveedor guardado correctamente.")
        form_widget.close()

        # Recargar tabla
        cargar_proveedores(tableWidget, edit_callback=edit_callback, main_form_widget=main_form_widget)

    except Exception as e:
        try:
            if conexion_db:
                conexion_db.rollback()
        except Exception:
            pass
        QMessageBox.critical(form_widget, "Error", f"No se pudo guardar el proveedor.{str(e)}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def cargar_proveedores(tableWidget, edit_callback=None, main_form_widget=None):
    """Carga todos los proveedores en el tableWidget y conecta los botones de editar/eliminar.
    - edit_callback: función (bound) que será llamada como edit_callback(FormWidget, id_proveedor)
    - main_form_widget: widget Form principal que se pasará como primer argumento al edit_callback
    """
    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        # Limpiar la tabla antes de cargar nuevos datos
        tableWidget.setRowCount(0)

        # Obtener datos de la base de datos
        cursor.execute("SELECT id_proveedor, nombre, telefono, direccion, correo FROM proveedores ORDER BY id_proveedor")
        proveedores = cursor.fetchall()
        
        for proveedor in proveedores:
            row_number = tableWidget.rowCount()
            tableWidget.insertRow(row_number)

            id_prov, nombre, telefono, direccion, correo = proveedor
            tableWidget.setItem(row_number, 0, QTableWidgetItem(str(id_prov)))
            tableWidget.setItem(row_number, 1, QTableWidgetItem(nombre))
            tableWidget.setItem(row_number, 2, QTableWidgetItem(telefono))
            tableWidget.setItem(row_number, 3, QTableWidgetItem(direccion))
            tableWidget.setItem(row_number, 4, QTableWidgetItem(correo))

            # Contenedor y botones por fila
            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            boton_editar = QPushButton("Editar")
            # Permission identifiers
            boton_editar.setObjectName("btnProveedorEditar")
            boton_editar.setProperty("perm_code", "proveedores.update")
            boton_editar.setStyleSheet("background-color: #3498db; color: white; border-radius: 5px; padding: 4px;")

            boton_eliminar = QPushButton("Eliminar")
            # Permission identifiers
            boton_eliminar.setObjectName("btnProveedorEliminar")
            boton_eliminar.setProperty("perm_code", "proveedores.delete")
            boton_eliminar.setStyleSheet("background-color: #e00000; color: white; border-radius: 5px; padding: 4px;")

            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
            tableWidget.setCellWidget(row_number, 5, contenedor)
            
            # Conectar botones por fila (bind de id_prov)
            if edit_callback and main_form_widget is not None:
                boton_editar.clicked.connect(partial(edit_callback, main_form_widget, id_prov))
            else:
                boton_editar.clicked.connect(lambda: None)

            boton_eliminar.clicked.connect(partial(eliminar_proveedor, id_prov, tableWidget))

        # Re-apply permissions if the page holds a reference to MenuPrincipal
        try:
            p = tableWidget
            page = None
            menu_ref = None
            # climb parents to find container with menuPrincipalRef
            while p is not None:
                if hasattr(p, 'menuPrincipalRef'):
                    page = p
                    menu_ref = getattr(p, 'menuPrincipalRef', None)
                    break
                p = p.parent() if hasattr(p, 'parent') else None
            if menu_ref and page:
                menu_ref._apply_permissions_to_module_page("Proveedores", page)
        except Exception:
            pass

    except Exception as e:
        print(f"Error al cargar proveedores: {e}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def buscar_proveedores(nombre, tableWidget, edit_callback=None, main_form_widget=None):
    """Busca proveedores por nombre (LIKE) y actualiza el tableWidget."""
    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()

        tableWidget.setRowCount(0)  # Limpiar tabla

        query = """
            SELECT id_proveedor, nombre, telefono, direccion, correo
            FROM proveedores
            WHERE LOWER(nombre) LIKE %s
            ORDER BY id_proveedor
        """
        cursor.execute(query, (f"%{nombre.lower()}%",))
        proveedores = cursor.fetchall()

        for proveedor in proveedores:
            row_number = tableWidget.rowCount()
            tableWidget.insertRow(row_number)

            id_prov, nombre, telefono, direccion, correo = proveedor
            tableWidget.setItem(row_number, 0, QTableWidgetItem(str(id_prov)))
            tableWidget.setItem(row_number, 1, QTableWidgetItem(nombre))
            tableWidget.setItem(row_number, 2, QTableWidgetItem(telefono))
            tableWidget.setItem(row_number, 3, QTableWidgetItem(direccion))
            tableWidget.setItem(row_number, 4, QTableWidgetItem(correo))

            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            boton_editar = QPushButton("Editar")
            boton_editar.setObjectName("btnProveedorEditar")                # PATCH permisos
            boton_editar.setProperty("perm_code", "proveedores.update")  
            boton_editar.setStyleSheet("background-color: #3498db; color: white; border-radius: 5px; padding: 4px;")

            boton_eliminar = QPushButton("Eliminar")
            boton_eliminar.setObjectName("btnProveedorEliminar")            # PATCH permisos
            boton_eliminar.setProperty("perm_code", "proveedores.delete")  
            boton_eliminar.setStyleSheet("background-color: #e00000; color: white; border-radius: 5px; padding: 4px;")

            layout.addWidget(boton_editar)
            layout.addWidget(boton_eliminar)
            tableWidget.setCellWidget(row_number, 5, contenedor)

            if edit_callback and main_form_widget is not None:
                boton_editar.clicked.connect(partial(edit_callback, main_form_widget, id_prov))
            else:
                boton_editar.clicked.connect(lambda: None)

            boton_eliminar.clicked.connect(partial(eliminar_proveedor, id_prov, tableWidget))

        # Re-apply permissions after search refresh
        try:
            p = tableWidget
            page = None
            menu_ref = None
            while p is not None:
                if hasattr(p, 'menuPrincipalRef'):
                    page = p
                    menu_ref = getattr(p, 'menuPrincipalRef', None)
                    break
                p = p.parent() if hasattr(p, 'parent') else None
            if menu_ref and page:
                menu_ref._apply_permissions_to_module_page("Proveedores", page)
        except Exception:
            pass

    except Exception as e:
        print(f"Error al buscar proveedores: {e}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def editar_proveedor(ui_nuevo_proveedor, tableWidget, id_proveedor, form_widget, edit_callback, main_form_widget):
    """Actualiza un proveedor y recarga la tabla."""
    nombre = ui_nuevo_proveedor.lineEditNombre.text().strip()
    direccion = ui_nuevo_proveedor.lineEditDireccion.text().strip()
    telefono = ui_nuevo_proveedor.lineEditTelefono.text().strip()
    correo = ui_nuevo_proveedor.lineEditCorreo.text().strip()
    
    if not nombre or not correo or not telefono:
        QMessageBox.warning(form_widget, "Campos obligatorios", "Todos los campos excepto dirección son obligatorios.")
        return

    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute(
            """
            UPDATE proveedores
            SET nombre = %s, 
                telefono = %s,
                direccion = %s,
                correo = %s
            WHERE id_proveedor = %s
            """,
            (nombre, telefono , direccion, correo, id_proveedor)
        )
        conexion_db.commit()
        
        QMessageBox.information(form_widget, "Éxito", "Proveedor actualizado correctamente.")
        form_widget.close()

        # Recargar tabla
        cargar_proveedores(tableWidget, edit_callback=edit_callback, main_form_widget=main_form_widget)

    except Exception as e:
        try:
            if conexion_db:
                conexion_db.rollback()
        except Exception:
            pass
        QMessageBox.critical(form_widget, "Error", f"No se pudo actualizar el proveedor.{str(e)}")

    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass


def eliminar_proveedor(id_proveedor, tableWidget):
    confirm = QMessageBox.question(None, "Eliminar", "¿Estás seguro de eliminar este proveedor?",
        QMessageBox.Yes | QMessageBox.No)
    if confirm == QMessageBox.Yes:
        conexion_db = None
        cursor = None
        try:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s;", (id_proveedor,))
            conexion_db.commit()
        
            for fila in range(tableWidget.rowCount()):
                item = tableWidget.item(fila, 0)
                if item and int(item.text()) == id_proveedor:
                    tableWidget.removeRow(fila)
                    break

        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo eliminar el proveedor.{str(e)}")

        finally:
            try:
                if cursor:
                    cursor.close()
                if conexion_db:
                    conexion_db.close()
            except Exception:
                pass


def obtener_proveedor_por_id(id_proveedor):
    conexion_db = None
    cursor = None
    try:
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("SELECT id_proveedor, nombre, telefono, direccion, correo FROM proveedores WHERE id_proveedor = %s;", (id_proveedor,))
        proveedor = cursor.fetchone()
        return proveedor
    except Exception as e:
        print(f"Error al obtener proveedor: {e}")
        return None
    finally:
        try:
            if cursor:
                cursor.close()
            if conexion_db:
                conexion_db.close()
        except Exception:
            pass
