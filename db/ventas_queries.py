# -*- coding: utf-8 -*-
from db.conexion import conexion
from PySide6.QtWidgets import (
    QComboBox, QTableWidgetItem, QPushButton, QWidget, QTreeWidgetItem, QHBoxLayout, QMessageBox, QSpinBox
)
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QDateTime, QSize
from utils.utilsVentas import calcular_total_general
from functools import partial
from forms.ui_helpers import style_edit_button, style_delete_button
from utils.normNumbers import formatear_numero

# ---------------------------
# Helpers locales (no rompen lógica)
# ---------------------------

def _fetch_productos(cursor):
    """
    Trae productos una sola vez: (id_producto, nombre, precio_venta).
    Devuelve:
      - lista [(id, nombre, precio)]
      - dict_precio_por_id {id: precio}
      - dict_nombre_por_id {id: nombre}
    """
    cursor.execute("SELECT id_producto, nombre, precio_venta FROM productos;")
    rows = cursor.fetchall()
    precio_por_id = {r[0]: float(r[2] or 0) for r in rows}
    nombre_por_id = {r[0]: r[1] for r in rows}
    return rows, precio_por_id, nombre_por_id


def _ensure_product_cache(ui_nueva_venta, cursor):
    """
    Garantiza caches en el UI del formulario:
      ui_nueva_venta._productos_lista
      ui_nueva_venta._precio_por_id
      ui_nueva_venta._nombre_por_id
    """
    if not hasattr(ui_nueva_venta, "_precio_por_id") or ui_nueva_venta._precio_por_id is None:
        productos, precio_por_id, nombre_por_id = _fetch_productos(cursor)
        ui_nueva_venta._productos_lista = productos
        ui_nueva_venta._precio_por_id = precio_por_id
        ui_nueva_venta._nombre_por_id = nombre_por_id


def _set_no_edit(item: QTableWidgetItem, text: str):
    item.setText(text)
    item.setFlags(item.flags() & ~Qt.ItemIsEditable)


# ==========================================
# GUARDAR VENTA (ALTA)
# ==========================================
def guardar_venta_en_db(ui_nueva_venta, ui, Form):
    con = conexion()
    cur = con.cursor()
    try:
        # Datos generales desde UI
        id_cliente = ui_nueva_venta.comboBox.currentData()
        fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toPython()
        medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()

        # Totales desde tabla UI (triggers igual recalculan en DB)
        total = 0.0
        cantidad_total = 0
        rows = ui_nueva_venta.tableWidget.rowCount()
        for row in range(rows):
            item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)
            sub = item_subtotal.data(Qt.UserRole) if item_subtotal else 0.0
            total += sub
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            if spin:
                cantidad_total += int(spin.value())

        # Encabezado
        cur.execute(
            """
            INSERT INTO ventas (id_cliente, cantidad, total_venta, fecha_venta, medio_pago)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_venta;
            """,
            (id_cliente, cantidad_total, total, fecha, medio_pago)
        )
        id_venta = cur.fetchone()[0]

        # Detalles
        for row in range(rows):
            combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            item_precio = ui_nueva_venta.tableWidget.item(row, 2)
            item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)
            if not (combo and spin and item_precio and item_subtotal):
                continue

            id_producto = combo.currentData()
            cantidad = int(spin.value())
            precio_unitario = item_precio.data(Qt.UserRole) or 0.0
            subtotal = item_subtotal.data(Qt.UserRole) or 0.0

            cur.execute(
                """
                INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (id_venta, id_producto, cantidad, precio_unitario, subtotal)
            )

        con.commit()

    except Exception as e:
        con.rollback()
        QMessageBox.critical(None, "Error al guardar", f"{e}")
    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass
        ui.treeWidget.clear()
        cargar_ventas(ui, Form)
        if hasattr(ui, "_post_refresh"):
            ui._post_refresh()
        if hasattr(ui, 'formulario_nueva_venta'):
            ui.formulario_nueva_venta.close()


# ==========================================
# Agregar primera fila al formulario
# ==========================================
def agregar_filas(ui):

    con = conexion()
    cur = con.cursor()

    _ensure_product_cache(ui, cur)
    table = ui.tableWidget

    row = table.rowCount()
    table.insertRow(row)

    # =========================
    # Combo de productos
    # =========================
    combo = QComboBox()
    combo.addItem("Seleccione", None)
    for pid, nombre, _precio in ui._productos_lista:
        combo.addItem(nombre, pid)
    table.setCellWidget(row, 0, combo)
    combo.currentIndexChanged.connect(
        lambda *_: _actualizar_tooltip_producto(combo)
    )

    # =========================
    # Cantidad
    # =========================
    spin = QSpinBox()
    spin.setMinimum(1)
    spin.setMaximum(999)
    table.setCellWidget(row, 1, spin)

    # =========================
    # Precio unitario (EDITABLE)
    # =========================
    item_precio = QTableWidgetItem(formatear_numero(0))
    item_precio.setData(Qt.UserRole, 0.0)
    item_precio.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    table.setItem(row, 2, item_precio)

    # =========================
    # Subtotal (NO editable)
    # =========================
    item_sub = QTableWidgetItem(formatear_numero(0))
    item_sub.setData(Qt.UserRole, 0.0)
    item_sub.setFlags(item_sub.flags() & ~Qt.ItemIsEditable)
    item_sub.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    table.setItem(row, 3, item_sub)

    # =========================
    # Señales
    # =========================
    combo.currentIndexChanged.connect(
        partial(on_producto_changed, row, ui)
    )

    spin.valueChanged.connect(
        partial(actualizar_subtotal, row, ui)
    )

def _actualizar_tooltip_producto(combo):
    texto = combo.currentText()
    combo.setToolTip(texto)


def _on_item_changed(item, ui):
    if ui._bloqueando_item_changed:
        return

    if item.column() == 2:  # precio
        texto = item.text().strip()

        try:
            valor = float(texto.replace(".", "").replace(",", "."))
        except ValueError:
            valor = 0.0

        ui._bloqueando_item_changed = True
        item.setData(Qt.UserRole, valor)
        item.setText(formatear_numero(valor))
        ui._bloqueando_item_changed = False

        actualizar_subtotal(item.row(), ui)


# ==========================================
# Cargar ventas en el árbol principal
# ==========================================
def cargar_ventas(ui, Form):
    """
    Optimizado: 2 consultas (encabezados + todos los detalles con WHERE IN).
    Antes hacía 1 consulta por cada venta (N+1).
    """
    con = conexion()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT v.id_venta, v.fecha_venta, c.nombre, v.total_venta, v.medio_pago
            FROM ventas v
            JOIN clientes c ON v.id_cliente = c.id
            ORDER BY v.fecha_venta DESC;
        """)
        ventas = cur.fetchall()

        if not ventas:
            return

        # Preparar un único batch para detalles
        ids = [v[0] for v in ventas]
        # Nota: ANY(%s) requiere adaptar lista.
        cur.execute("""
            SELECT vd.id_venta, p.nombre, vd.cantidad, vd.precio_unitario, vd.subtotal
            FROM ventas_detalle vd
            JOIN productos p ON p.id_producto = vd.id_producto
            WHERE vd.id_venta = ANY(%s)
            ORDER BY vd.id_venta;
        """, (ids,))
        detalles_rows = cur.fetchall()

        # Indexar detalles por venta
        detalles_map = {}
        for id_venta, nombre, cant, precio, sub in detalles_rows:
            detalles_map.setdefault(id_venta, []).append((nombre, cant, precio, sub))

        # Poblar árbol
        for venta in ventas:
            id_venta, fecha, cliente, total, medio = venta
            item_venta = QTreeWidgetItem()
            item_venta.setText(0, str(id_venta))
            item_venta.setText(1, fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha))
            item_venta.setText(2, str(cliente))
            item_venta.setText(3, formatear_numero(total))
            item_venta.setText(4, medio or "")
            item_venta.setText(5, "")  # factura (si no usas)

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

            # Detalles (desde el mapa)
            for nombre_prod, cant, precio, sub in detalles_map.get(id_venta, []):
                item_sub = QTreeWidgetItem()
                item_sub.setText(1, str(nombre_prod))
                item_sub.setText(2, str(cant))
                item_sub.setText(3, formatear_numero(precio))
                item_sub.setText(4, formatear_numero(sub))
                item_venta.addChild(item_sub)

            # Botones una sola vez
            agregar_botones_opciones(ui.treeWidget, item_venta, ui, Form)

    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass


# ==========================================
# Eliminar venta (revierte stock por triggers)
# ==========================================
def eliminar_venta(treeWidget, item_venta):
    if not item_venta:
        return
    id_venta = item_venta.text(0)

    reply = QMessageBox.question(None, 'Eliminar venta',
                                 f"¿Eliminar la venta #{id_venta}? Esto revierte stock.",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    con = conexion()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM ventas_detalle WHERE id_venta = %s", (id_venta,))
        cur.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))
        con.commit()
        treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(item_venta))
    except Exception as e:
        con.rollback()
        QMessageBox.critical(None, "Error", f"No se pudo eliminar: {e}")
    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass


# ==========================================
# Editar venta
# ==========================================
def editar_venta(item_venta, ui, Form):
    if not item_venta:
        return

    id_venta = item_venta.text(0)
    ui.formulario_id_venta = id_venta

    # Abrir formulario en modo edición
    if not hasattr(ui, 'formulario_nueva_venta') or not ui.formulario_nueva_venta.isVisible():
        ui.abrir_formulario_nueva_venta(Form, edicion=True)

    ui_nueva_venta = ui.ui_nueva_venta

    con = conexion()
    cur = con.cursor()
    try:
        # Datos generales
        cur.execute("""
            SELECT id_cliente, fecha_venta, total_venta, medio_pago
            FROM ventas
            WHERE id_venta = %s
        """, (id_venta,))
        venta = cur.fetchone()
        if not venta:
            QMessageBox.warning(None, "Aviso", "Venta no encontrada.")
            return

        id_cliente, fecha, total, medio_pago = venta

        # clientes
        cur.execute("SELECT id, nombre FROM clientes;")
        clientes = cur.fetchall()
        ui_nueva_venta.comboBox.clear()
        idx_sel = 0
        for i, (idc, nombre) in enumerate(clientes):
            ui_nueva_venta.comboBox.addItem(nombre, idc)
            if idc == id_cliente:
                idx_sel = i
        ui_nueva_venta.comboBox.setCurrentIndex(idx_sel)

        # fecha
        if isinstance(fecha, QDateTime):
            dt = fecha
        else:
            try:
                # fecha es datetime
                dt = QDateTime.fromSecsSinceEpoch(int(fecha.timestamp()))
            except Exception:
                # fallback a ahora para evitar crash si el tipo viene raro
                dt = QDateTime.currentDateTime()
        ui_nueva_venta.dateTimeEditCliente.setDateTime(dt)

        # medio de pago
        ind_m = ui_nueva_venta.comboBoxMedioPago.findText(medio_pago or "")
        if ind_m >= 0:
            ui_nueva_venta.comboBoxMedioPago.setCurrentIndex(ind_m)

        # limpiar tabla y cargar productos con cache completa (incluye precio)
        ui_nueva_venta.tableWidget.setRowCount(0)
        _ensure_product_cache(ui_nueva_venta, cur)

        # detalles
        cur.execute("""
            SELECT id_producto, cantidad, precio_unitario, subtotal
            FROM ventas_detalle
            WHERE id_venta = %s
        """, (id_venta,))
        detalles = cur.fetchall()

        for i, (pid, cant, precio_u, sub) in enumerate(detalles):
            ui_nueva_venta.tableWidget.insertRow(i)

            combo = QComboBox()
            sel_idx = 0
            for j, (idp, nom, _pr) in enumerate(ui_nueva_venta._productos_lista):
                combo.addItem(nom, idp)
                if idp == pid:
                    sel_idx = j
            combo.setCurrentIndex(sel_idx)

            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setValue(int(cant))

            ui_nueva_venta.tableWidget.setCellWidget(i, 0, combo)
            ui_nueva_venta.tableWidget.setCellWidget(i, 1, spin)

            # celdas calculadas; se recalculan con actualizar_subtotal
            item_precio = QTableWidgetItem(formatear_numero(precio_u))
            _set_no_edit(item_precio, formatear_numero(precio_u))
            ui_nueva_venta.tableWidget.setItem(i, 2, item_precio)

            item_sub = QTableWidgetItem(formatear_numero(sub))
            _set_no_edit(item_sub, formatear_numero(sub))
            ui_nueva_venta.tableWidget.setItem(i, 3, item_sub)

            combo.currentIndexChanged.connect(partial(actualizar_subtotal, i, ui_nueva_venta))
            spin.valueChanged.connect(partial(actualizar_subtotal, i, ui_nueva_venta))
            actualizar_subtotal(i, ui_nueva_venta)

        calcular_total_general(ui_nueva_venta)

        # Conectar aceptar->actualizar (limpiando conexiones previas)
        try:
            ui_nueva_venta.pushButtonAceptar.clicked.disconnect()
        except Exception:
            pass
        ui_nueva_venta.pushButtonAceptar.clicked.connect(
            lambda: actualizar_venta_en_db(ui_nueva_venta, id_venta, ui, Form)
        )
    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass


def cargar_detalles_venta(id_venta, ui):
    # (Opcional: placeholder para futuras mejoras)
    pass


def actualizar_subtotal(row, ui, *_):
    try:
        table = ui.tableWidget

        combo = table.cellWidget(row, 0)
        spin = table.cellWidget(row, 1)
        item_precio = table.item(row, 2)
        item_sub = table.item(row, 3)

        if not (combo and spin and item_precio and item_sub):
            return

        # Cantidad
        cantidad = spin.value()

        # Precio unitario (SIEMPRE desde UserRole)
        precio_unitario = item_precio.data(Qt.UserRole)
        if precio_unitario is None:
            precio_unitario = 0.0

        # Subtotal real
        subtotal = precio_unitario * cantidad

        # Bloqueo de señales
        ui._bloqueando_item_changed = True

        item_sub.setData(Qt.UserRole, subtotal)
        item_sub.setText(formatear_numero(subtotal))

        ui._bloqueando_item_changed = False

        calcular_total_general(ui)

    except Exception as e:
        print(f"[actualizar_subtotal] Error fila {row}: {e}")


def on_producto_changed(row, ui, *_):
    combo = ui.tableWidget.cellWidget(row, 0)
    item_precio = ui.tableWidget.item(row, 2)

    if not combo or not item_precio:
        return

    pid = combo.currentData()
    if pid is None:
        return

    precio = ui._precio_por_id.get(pid, 0.0)

    item_precio.setData(Qt.UserRole, precio)
    item_precio.setText(formatear_numero(precio))

    actualizar_subtotal(row, ui)


# ==========================================
# Botones por venta
# ==========================================
def agregar_botones_opciones(treeWidget, item_venta, ui, Form):
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    btn_editar = QPushButton()
    btn_editar.setObjectName("btnVentaEditar")               # PATCH permisos
    btn_editar.setProperty("perm_code", "ventas.update")
    btn_editar.setFixedHeight(25)
    btn_editar.setIconSize(QSize(18, 18))
    style_edit_button(btn_editar, "Editar venta")

    btn_eliminar = QPushButton()
    btn_eliminar.setObjectName("btnVentaEliminar")           # PATCH permisos
    btn_eliminar.setProperty("perm_code", "ventas.delete")
    btn_eliminar.setFixedHeight(25)
    btn_eliminar.setIconSize(QSize(18, 18))
    style_delete_button(btn_eliminar, "Eliminar venta")

    layout.addWidget(btn_editar)
    layout.addWidget(btn_eliminar)
    widget.setLayout(layout)

    treeWidget.setItemWidget(item_venta, 6, widget)

    btn_editar.clicked.connect(lambda: editar_venta(item_venta, ui, Form))
    btn_eliminar.clicked.connect(lambda: eliminar_venta(ui.treeWidget, item_venta))


# ==========================================
# Actualizar venta
# ==========================================
def actualizar_venta_en_db(ui_nueva_venta, id_venta, ui, Form):
    con = conexion()
    cur = con.cursor()
    try:
        # borrar detalles viejos
        cur.execute("DELETE FROM ventas_detalle WHERE id_venta = %s", (id_venta,))

        cantidad_total = 0
        rows = ui_nueva_venta.tableWidget.rowCount()

        # insertar nuevos detalles
        for row in range(rows):
            combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            if not combo or not spin:
                continue

            id_producto = combo.currentData()
            cantidad = int(spin.value())
            cantidad_total += cantidad

            precio_unitario = ui_nueva_venta.tableWidget.item(row, 2).data(Qt.UserRole) or 0.0
            subtotal = ui_nueva_venta.tableWidget.item(row, 3).data(Qt.UserRole) or 0.0

            cur.execute(
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

        cur.execute(
            """
            UPDATE ventas
            SET id_cliente = %s, cantidad = %s, fecha_venta = %s, total_venta = %s, medio_pago = %s
            WHERE id_venta = %s
            """,
            (id_cliente, cantidad_total, fecha, total_venta, medio_pago, id_venta)
        )

        con.commit()

        ui.treeWidget.clear()
        cargar_ventas(ui, Form)
        if hasattr(ui, "_post_refresh"):
            ui._post_refresh()
        if hasattr(ui, 'formulario_nueva_venta'):
            ui.formulario_nueva_venta.close()

    except Exception as e:
        con.rollback()
        QMessageBox.critical(None, "Error", f"No se pudo actualizar la venta:\n{e}")
    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass


# ==========================================
# Buscar ventas (optimizado sin N+1)
# ==========================================
def buscar_ventas(ui, criterio, Form):
    con = conexion()
    cur = con.cursor()
    try:
        if not criterio:
            cur.execute("""
                SELECT v.id_venta, c.nombre, v.fecha_venta, v.total_venta, v.medio_pago
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id
                ORDER BY v.fecha_venta DESC;
            """)
        else:
            like = f"%{criterio}%"
            cur.execute("""
                SELECT v.id_venta, c.nombre, v.fecha_venta, v.total_venta, v.medio_pago
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id
                WHERE c.nombre ILIKE %s
                   OR v.medio_pago ILIKE %s
                   OR CAST(v.fecha_venta AS TEXT) ILIKE %s
                ORDER BY v.fecha_venta DESC;
            """, (like, like, like))

        ventas = cur.fetchall()
        ui.treeWidget.clear()

        if not ventas:
            return

        ids = [v[0] for v in ventas]
        # Traer todos los detalles en un solo batch
        cur.execute("""
            SELECT vd.id_venta, p.nombre, vd.cantidad, vd.precio_unitario, vd.subtotal
            FROM ventas_detalle vd
            JOIN productos p ON p.id_producto = vd.id_producto
            WHERE vd.id_venta = ANY(%s)
            ORDER BY vd.id_venta;
        """, (ids,))
        det_rows = cur.fetchall()
        det_map = {}
        for id_venta, nombre_producto, cant, precio_u, sub in det_rows:
            det_map.setdefault(id_venta, []).append((nombre_producto, cant, precio_u, sub))

        for id_venta, cliente, fecha, total, medio_pago in ventas:
            item = QTreeWidgetItem([
                str(id_venta),
                fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha),
                cliente,
                formatear_numero(total),
                medio_pago or "",
                "",   # factura
                ""    # opciones (widget)
            ])
            ui.treeWidget.addTopLevelItem(item)
            agregar_botones_opciones(ui.treeWidget, item, ui, Form)

            for nombre_producto, cant, precio_u, sub in det_map.get(id_venta, []):
                det = QTreeWidgetItem([
                    "", nombre_producto, str(cant),
                    formatear_numero(precio_u), formatear_numero(sub)
                ])
                item.addChild(det)
    finally:
        try:
            cur.close()
            con.close()
        except Exception:
            pass
