from db.conexion import conexion
from PySide6.QtWidgets import (
    QComboBox, QTableWidgetItem, QPushButton, QWidget, QTreeWidgetItem, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QDateTime
from utils.utilsVentas import calcular_total_general


# GUARDAR VENTA (ALTA)
def guardar_venta_en_db(ui_nueva_venta, ui, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()

    try:
        # Datos generales
        id_cliente = ui_nueva_venta.comboBox.currentData()
        fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toPython()
        medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()

        # Calcular totales de UI (triggers en DB igual recalculan)
        total = 0.0
        cantidad_total = 0
        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)
            subtotal = float(item_subtotal.text()) if item_subtotal and item_subtotal.text() else 0.0
            total += subtotal
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            if spin:
                cantidad_total += spin.value()

        # Insert encabezado de venta
        cursor.execute(
            """
            INSERT INTO ventas (id_cliente, cantidad, total_venta, fecha_venta, medio_pago)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_venta;
            """,
            (id_cliente, cantidad_total, total, fecha, medio_pago)
        )
        id_venta = cursor.fetchone()[0]

        # Insert detalles (disparan triggers de stock y triggers de totales)
        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            item_precio = ui_nueva_venta.tableWidget.item(row, 2)
            item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)

            if not (combo and spin and item_precio and item_subtotal):
                continue

            id_producto = combo.currentData()
            cantidad = spin.value()
            precio_unitario = float(item_precio.text() or 0)
            subtotal = float(item_subtotal.text() or 0)

            cursor.execute(
                """
                INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (id_venta, id_producto, cantidad, precio_unitario, subtotal)
            )

        conexion_db.commit()

    except Exception as e:
        conexion_db.rollback()
        QMessageBox.critical(None, "Error al guardar", f"{e}")
    finally:
        cursor.close()
        conexion_db.close()
        ui.treeWidget.clear()
        cargar_ventas(ui, Form)
        if hasattr(ui, 'formulario_nueva_venta'):
            ui.formulario_nueva_venta.close()


# Agregar primera fila al formulario (con combos y spin)
def agregar_filas(ui_nueva_venta):
    row = ui_nueva_venta.tableWidget.rowCount()
    ui_nueva_venta.tableWidget.insertRow(row)

    combo = QComboBox()
    combo.addItem("Seleccione", None)

    # cargar productos
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    cursor.execute("SELECT id_producto, nombre, precio_venta FROM productos;")
    productos = cursor.fetchall()
    cursor.close()
    conexion_db.close()

    # cache de precios (opcional)
    ui_nueva_venta.precios = {}
    for pid, nombre, precio in productos:
        combo.addItem(nombre, pid)
        ui_nueva_venta.precios[nombre] = precio

    ui_nueva_venta.tableWidget.setCellWidget(row, 0, combo)

    # cantidad
    from PySide6.QtWidgets import QSpinBox
    spin = QSpinBox()
    spin.setMinimum(1)
    spin.setMaximum(999)
    ui_nueva_venta.tableWidget.setCellWidget(row, 1, spin)

    # precio unitario (no editable)
    item_precio = QTableWidgetItem("0")
    item_precio.setFlags(item_precio.flags() ^ Qt.ItemIsEditable)
    ui_nueva_venta.tableWidget.setItem(row, 2, item_precio)

    # subtotal (no editable)
    item_subtotal = QTableWidgetItem("0")
    item_subtotal.setFlags(item_subtotal.flags() ^ Qt.ItemIsEditable)
    ui_nueva_venta.tableWidget.setItem(row, 3, item_subtotal)

    # eventos
    combo.currentIndexChanged.connect(lambda: actualizar_subtotal(row, ui_nueva_venta))
    spin.valueChanged.connect(lambda: actualizar_subtotal(row, ui_nueva_venta))
    combo.currentIndexChanged.connect(lambda: calcular_total_general(ui_nueva_venta))
    spin.valueChanged.connect(lambda: calcular_total_general(ui_nueva_venta))


# Botón "Agregar producto" (nuevas filas)
def agrega_prodcuto_a_fila(ui_nueva_venta):
    row = ui_nueva_venta.tableWidget.rowCount()
    ui_nueva_venta.tableWidget.insertRow(row)

    combo = QComboBox()

    # cargar productos
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    cursor.execute("SELECT id_producto, nombre, precio_venta FROM productos;")
    productos = cursor.fetchall()
    cursor.close()
    conexion_db.close()

    ui_nueva_venta.precios = {}
    for pid, nombre, precio in productos:
        combo.addItem(nombre, pid)
        ui_nueva_venta.precios[nombre] = precio

    ui_nueva_venta.tableWidget.setCellWidget(row, 0, combo)

    from PySide6.QtWidgets import QSpinBox
    spin = QSpinBox()
    spin.setMinimum(1)
    spin.setMaximum(999)
    ui_nueva_venta.tableWidget.setCellWidget(row, 1, spin)

    precio_unitario_valor = 0
    if combo.count() > 0:
        precio_unitario_valor = ui_nueva_venta.precios.get(combo.currentText(), 0)

    item_precio = QTableWidgetItem(str(precio_unitario_valor))
    item_precio.setFlags(item_precio.flags() ^ Qt.ItemIsEditable)
    ui_nueva_venta.tableWidget.setItem(row, 2, item_precio)

    item_subtotal = QTableWidgetItem("0")
    item_subtotal.setFlags(item_subtotal.flags() ^ Qt.ItemIsEditable)
    ui_nueva_venta.tableWidget.setItem(row, 3, item_subtotal)

    combo.currentIndexChanged.connect(lambda: actualizar_subtotal(row, ui_nueva_venta))
    spin.valueChanged.connect(lambda: actualizar_subtotal(row, ui_nueva_venta))
    combo.currentIndexChanged.connect(lambda: calcular_total_general(ui_nueva_venta))
    spin.valueChanged.connect(lambda: calcular_total_general(ui_nueva_venta))


# Cargar ventas en el árbol principal
def cargar_ventas(ui, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    cursor.execute("""
        SELECT v.id_venta, v.fecha_venta, c.nombre, v.cantidad, v.total_venta, v.medio_pago
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id
        ORDER BY v.fecha_venta DESC;
    """)
    ventas = cursor.fetchall()

    for venta in ventas:
        id_venta, fecha, cliente, cantidad, total, medio = venta

        item_venta = QTreeWidgetItem()
        item_venta.setText(0, str(id_venta))
        item_venta.setText(1, fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha))
        item_venta.setText(2, str(cliente))
        item_venta.setText(3, str(cantidad))
        item_venta.setText(4, f"{float(total):.2f}")
        item_venta.setText(5, medio or "")
        # Col 6 = Factura (si no usás, queda vacío)
        item_venta.setText(6, "")

        ui.treeWidget.addTopLevelItem(item_venta)

        # Encabezado de subtabla
        header_hijo = QTreeWidgetItem()
        header_hijo.setText(1, "Producto")
        header_hijo.setText(2, "Cantidad")
        header_hijo.setText(3, "Precio Unitario")
        header_hijo.setText(4, "Subtotal")
        item_venta.addChild(header_hijo)

        # estilo header hijo
        for col in range(1, 5):
            header_hijo.setBackground(col, QBrush(QColor("#dcdcdc")))
            header_hijo.setForeground(col, QBrush(QColor("#2c3e50")))
            font = QFont()
            font.setBold(True)
            header_hijo.setFont(col, font)

        # Detalles de venta
        cursor.execute("""
            SELECT p.nombre, vd.cantidad, vd.precio_unitario, vd.subtotal
            FROM ventas_detalle vd
            JOIN productos p ON vd.id_producto = p.id_producto
            WHERE vd.id_venta = %s
        """, (id_venta,))
        detalles = cursor.fetchall()

        for nombre_prod, cant, precio, sub in detalles:
            item_sub = QTreeWidgetItem()
            item_sub.setText(1, str(nombre_prod))
            item_sub.setText(2, str(cant))
            item_sub.setText(3, f"{float(precio):.2f}")
            item_sub.setText(4, f"{float(sub):.2f}")
            item_venta.addChild(item_sub)

        # botones (una sola vez por venta)
        agregar_botones_opciones(ui.treeWidget, item_venta, ui, Form)

    cursor.close()
    conexion_db.close()


# Eliminar venta (revierte stock por triggers al borrar detalles)
def eliminar_venta(treeWidget, item_venta):
    if not item_venta:
        return
    id_venta = item_venta.text(0)

    reply = QMessageBox.question(None, 'Eliminar venta',
                                 f"¿Eliminar la venta #{id_venta}? Esto revierte stock.",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    conexion_db = conexion()
    cursor = conexion_db.cursor()
    try:
        cursor.execute("DELETE FROM ventas_detalle WHERE id_venta = %s", (id_venta,))
        cursor.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))
        conexion_db.commit()
        treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(item_venta))
    except Exception as e:
        conexion_db.rollback()
        QMessageBox.critical(None, "Error", f"No se pudo eliminar: {e}")
    finally:
        cursor.close()
        conexion_db.close()


def editar_venta(item_venta, ui, Form):
    if not item_venta:
        return

    id_venta = item_venta.text(0)
    ui.formulario_id_venta = id_venta

    # Abrir formulario en modo edición
    if not hasattr(ui, 'formulario_nueva_venta') or not ui.formulario_nueva_venta.isVisible():
        ui.abrir_formulario_nueva_venta(Form, edicion=True)

    ui_nueva_venta = ui.ui_nueva_venta

    conexion_db = conexion()
    cursor = conexion_db.cursor()

    # Datos generales
    cursor.execute("""
        SELECT id_cliente, fecha_venta, total_venta, medio_pago
        FROM ventas
        WHERE id_venta = %s
    """, (id_venta,))
    venta = cursor.fetchone()
    if not venta:
        cursor.close()
        conexion_db.close()
        QMessageBox.warning(None, "Aviso", "Venta no encontrada.")
        return

    id_cliente, fecha, total, medio_pago = venta

    # clientes
    cursor.execute("SELECT id, nombre FROM clientes")
    clientes = cursor.fetchall()
    ui_nueva_venta.comboBox.clear()
    idx = 0
    for i, (idc, nombre) in enumerate(clientes):
        ui_nueva_venta.comboBox.addItem(nombre, idc)
        if idc == id_cliente:
            idx = i
    ui_nueva_venta.comboBox.setCurrentIndex(idx)

    # fecha
    dt = fecha if isinstance(fecha, QDateTime) else QDateTime.fromSecsSinceEpoch(int(fecha.timestamp()))
    ui_nueva_venta.dateTimeEditCliente.setDateTime(dt)

    # medio de pago
    ind_m = ui_nueva_venta.comboBoxMedioPago.findText(medio_pago or "")
    if ind_m >= 0:
        ui_nueva_venta.comboBoxMedioPago.setCurrentIndex(ind_m)

    # limpiar tabla y cargar productos
    ui_nueva_venta.tableWidget.setRowCount(0)
    cursor.execute("SELECT id_producto, nombre FROM productos")
    productos = cursor.fetchall()

    # detalles
    cursor.execute("""
        SELECT id_producto, cantidad, precio_unitario, subtotal
        FROM ventas_detalle
        WHERE id_venta = %s
    """, (id_venta,))
    detalles = cursor.fetchall()

    from PySide6.QtWidgets import QSpinBox
    for i, (pid, cant, precio_u, sub) in enumerate(detalles):
        ui_nueva_venta.tableWidget.insertRow(i)
        combo = QComboBox()
        idx_prod = 0
        for j, (idp, nom) in enumerate(productos):
            combo.addItem(nom, idp)
            if idp == pid:
                idx_prod = j
        combo.setCurrentIndex(idx_prod)

        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setValue(cant)

        ui_nueva_venta.tableWidget.setCellWidget(i, 0, combo)
        ui_nueva_venta.tableWidget.setCellWidget(i, 1, spin)

        # celdas calculadas
        ui_nueva_venta.tableWidget.setItem(i, 2, QTableWidgetItem(""))  # precio
        ui_nueva_venta.tableWidget.setItem(i, 3, QTableWidgetItem(""))  # subtotal

        combo.currentIndexChanged.connect(lambda _, row=i: actualizar_subtotal(row, ui_nueva_venta))
        spin.valueChanged.connect(lambda _, row=i: actualizar_subtotal(row, ui_nueva_venta))
        actualizar_subtotal(i, ui_nueva_venta)

    calcular_total_general(ui_nueva_venta)

    # limpiar señales previas y conectar aceptar->actualizar
    try:
        ui_nueva_venta.pushButtonAceptar.clicked.disconnect()
    except Exception:
        pass
    ui_nueva_venta.pushButtonAceptar.clicked.connect(
        lambda: actualizar_venta_en_db(ui_nueva_venta, id_venta, ui, Form)
    )

    cursor.close()
    conexion_db.close()


def cargar_detalles_venta(id_venta, ui):
    # (Opcional: no usado en esta versión del flujo)
    pass


def actualizar_subtotal(row, ui):
    try:
        combo = ui.tableWidget.cellWidget(row, 0)
        spin = ui.tableWidget.cellWidget(row, 1)
        if combo is None or spin is None:
            return

        id_producto = combo.currentData()
        cantidad = spin.value()
        if id_producto is None:
            return

        # precio desde DB
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("SELECT precio_venta FROM productos WHERE id_producto = %s", (id_producto,))
        res = cursor.fetchone()
        cursor.close()
        conexion_db.close()

        if not res:
            return

        precio_unitario = float(res[0])
        subtotal = precio_unitario * cantidad

        ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{precio_unitario:.2f}"))
        ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))

        calcular_total_general(ui)

    except Exception as e:
        print(f"[actualizar_subtotal] Error fila {row}: {e}")


def agregar_botones_opciones(treeWidget, item_venta, ui, Form):
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    btn_editar = QPushButton("Editar")
    btn_editar.setObjectName("btnVentaEditar")               # PATCH permisos
    btn_editar.setProperty("perm_code", "ventas.update")
    btn_eliminar = QPushButton("Eliminar")
    btn_eliminar.setObjectName("btnVentaEliminar")           # PATCH permisos
    btn_eliminar.setProperty("perm_code", "ventas.delete")
    btn_editar.setFixedHeight(25)
    btn_eliminar.setFixedHeight(25)

    layout.addWidget(btn_editar)
    layout.addWidget(btn_eliminar)
    widget.setLayout(layout)

    treeWidget.setItemWidget(item_venta, 7, widget)

    btn_editar.clicked.connect(lambda: editar_venta(item_venta, ui, Form))
    btn_eliminar.clicked.connect(lambda: eliminar_venta(ui.treeWidget, item_venta))


def actualizar_venta_en_db(ui_nueva_venta, id_venta, ui, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    try:
        # eliminar detalles viejos (dispara IN por triggers)
        cursor.execute("DELETE FROM ventas_detalle WHERE id_venta = %s", (id_venta,))

        cantidad_total = 0
        # insertar nuevos detalles (dispara OUT por triggers)
        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            if not combo or not spin:
                continue
            id_producto = combo.currentData()
            cantidad = spin.value()
            cantidad_total += cantidad

            precio_unitario = float(ui_nueva_venta.tableWidget.item(row, 2).text() or 0)
            subtotal = float(ui_nueva_venta.tableWidget.item(row, 3).text() or 0)

            cursor.execute(
                """
                INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (id_venta, id_producto, cantidad, precio_unitario, subtotal)
            )

        # datos generales
        id_cliente = ui_nueva_venta.comboBox.currentData()
        fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toPython()
        medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()
        total_venta = calcular_total_general(ui_nueva_venta)

        cursor.execute(
            """
            UPDATE ventas
            SET id_cliente = %s, cantidad = %s, fecha_venta = %s, total_venta = %s, medio_pago = %s
            WHERE id_venta = %s
            """,
            (id_cliente, cantidad_total, fecha, total_venta, medio_pago, id_venta)
        )

        conexion_db.commit()

        ui.treeWidget.clear()
        cargar_ventas(ui, Form)
        if hasattr(ui, 'formulario_nueva_venta'):
            ui.formulario_nueva_venta.close()

    except Exception as e:
        conexion_db.rollback()
        QMessageBox.critical(None, "Error", f"No se pudo actualizar la venta:\n{e}")
    finally:
        cursor.close()
        conexion_db.close()


def buscar_ventas(ui, criterio, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()

    if not criterio:
        cursor.execute("""
            SELECT v.id_venta, c.nombre, v.fecha_venta, v.total_venta, v.medio_pago, v.cantidad
            FROM ventas v
            JOIN clientes c ON v.id_cliente = c.id
            ORDER BY v.fecha_venta DESC
        """)
    else:
        consulta = """
            SELECT v.id_venta, c.nombre, v.fecha_venta, v.total_venta, v.medio_pago, v.cantidad
            FROM ventas v
            JOIN clientes c ON v.id_cliente = c.id
            WHERE c.nombre ILIKE %s OR v.medio_pago ILIKE %s OR CAST(v.fecha_venta AS TEXT) ILIKE %s
            ORDER BY v.fecha_venta DESC
        """
        like = f"%{criterio}%"
        cursor.execute(consulta, (like, like, like))

    ventas = cursor.fetchall()
    ui.treeWidget.clear()

    for id_venta, cliente, fecha, total, medio_pago, cantidad in ventas:
        item = QTreeWidgetItem([
            str(id_venta),
            fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha),
            cliente,
            str(cantidad),
            f"{float(total):.2f}",
            medio_pago or "",
            "",  # factura
            ""   # opciones (widget se agrega abajo)
        ])
        ui.treeWidget.addTopLevelItem(item)
        agregar_botones_opciones(ui.treeWidget, item, ui, Form)

        # detalles
        con2 = conexion()
        cur2 = con2.cursor()
        cur2.execute("""
            SELECT p.nombre, vd.cantidad, vd.precio_unitario, vd.subtotal
            FROM ventas_detalle vd
            JOIN productos p ON p.id_producto = vd.id_producto
            WHERE vd.id_venta = %s
        """, (id_venta,))
        detalles = cur2.fetchall()
        for nombre_producto, cant, precio_u, sub in detalles:
            det = QTreeWidgetItem([
                "", nombre_producto, str(cant),
                f"{float(precio_u):.2f}", f"{float(sub):.2f}"
            ])
            item.addChild(det)
        cur2.close()
        con2.close()

    cursor.close()
    conexion_db.close()
