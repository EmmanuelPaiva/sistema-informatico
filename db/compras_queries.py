# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functools import partial
from db.conexion import conexion
from PySide6.QtWidgets import (
    QSpinBox, QComboBox, QTableWidgetItem, QPushButton, QWidget,
    QTreeWidgetItem, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QDateTime
from utils.utilsCompras import calcular_total_general
from main.themes import themed_icon
from utils.normNumbers import formatear_numero


# -------------------- helpers internos --------------------
def _set_ro(item: QTableWidgetItem, text: str):
    """Set texto + deshabilita edición."""
    item.setText(text)
    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

def _ensure_producto_cache(ui_form, proveedor_id):
    """
    Garantiza caches por proveedor en el formulario de compras:
      - ui_form._prod_lista: [(id_producto, nombre, precio_venta)]
      - ui_form._precio_por_id: {id_producto: precio_venta}
      - ui_form._nombre_por_id: {id_producto: nombre}
    """
    if getattr(ui_form, "_cache_proveedor", None) == proveedor_id \
       and getattr(ui_form, "_precio_por_id", None):
        return

    with conexion() as c, c.cursor() as cur:
        cur.execute("""
            SELECT id_producto, nombre, precio_venta
            FROM productos
            WHERE id_proveedor = %s
            ORDER BY nombre;
        """, (proveedor_id,))
        rows = cur.fetchall()

    ui_form._cache_proveedor = proveedor_id
    ui_form._prod_lista = rows
    ui_form._precio_por_id = {r[0]: float(r[2] or 0) for r in rows}
    ui_form._nombre_por_id = {r[0]: r[1] for r in rows}


# ---------- CALCULAR SUBTOTAL FILA ----------
def actualizar_subtotal(row, ui, *__):
    """
    Recalcula precio y subtotal de la fila.
    Acepta *__ para tolerar parámetros extra provenientes de señales Qt.
    """
    try:
        combo = ui.tableWidget.cellWidget(row, 0)  # Producto
        spin  = ui.tableWidget.cellWidget(row, 1)  # Cantidad
        if combo is None or spin is None:
            return

        id_producto = combo.currentData()
        # Si no hay producto seleccionado, precio/subtotal = 0
        if id_producto is None:
            ui.tableWidget.setItem(row, 2, QTableWidgetItem("0.00"))
            ui.tableWidget.setItem(row, 3, QTableWidgetItem("0.00"))
            calcular_total_general(ui)
            return

        # precio desde caché (cargado al agregar/editar)
        precio_unitario = float(getattr(ui, "_precio_por_id", {}).get(id_producto, 0.0))
        cantidad = max(1, int(spin.value() or 1))
        subtotal = precio_unitario * cantidad

        ui.tableWidget.setItem(row, 2, QTableWidgetItem(formatear_numero(precio_unitario)))
        ui.tableWidget.setItem(row, 3, QTableWidgetItem(formatear_numero(subtotal)))
        calcular_total_general(ui)
    except Exception as e:
        print(f"[actualizar_subtotal] Error fila {row}: {e}")


# ---------- AGREGAR UNA FILA ----------
def agrega_prodcuto_a_fila(ui_nueva_compra):
    row = ui_nueva_compra.tableWidget.rowCount()
    ui_nueva_compra.tableWidget.insertRow(row)

    combo = QComboBox()
    ui_nueva_compra.tableWidget.setCellWidget(row, 0, combo)

    # productos por proveedor (cacheados)
    id_proveedor = ui_nueva_compra.comboBox.currentData()
    if id_proveedor is None:
        return
    _ensure_producto_cache(ui_nueva_compra, id_proveedor)

    # llenar combo
    combo.addItem("Seleccione", None)
    for pid, nombrep, _precio in ui_nueva_compra._prod_lista:
        combo.addItem(nombrep, pid)

    # cantidad
    spin = QSpinBox(); spin.setMinimum(1); spin.setMaximum(999)
    ui_nueva_compra.tableWidget.setCellWidget(row, 1, spin)

    # precio / subtotal iniciales (no editables)
    item_precio = QTableWidgetItem(); _set_ro(item_precio, formatear_numero(0))
    ui_nueva_compra.tableWidget.setItem(row, 2, item_precio)

    item_subtotal = QTableWidgetItem(); _set_ro(item_subtotal, formatear_numero(0))
    ui_nueva_compra.tableWidget.setItem(row, 3, item_subtotal)

    # señales: ignoramos el parámetro extra con lambda *_:
    combo.currentIndexChanged.connect(lambda *_: actualizar_subtotal(row, ui_nueva_compra))
    spin.valueChanged.connect(lambda *_: actualizar_subtotal(row, ui_nueva_compra))
    combo.currentIndexChanged.connect(lambda *_: calcular_total_general(ui_nueva_compra))
    spin.valueChanged.connect(lambda *_: calcular_total_general(ui_nueva_compra))

def reiniciar_tabla_productos(ui):
    ui.tableWidget.setRowCount(0)
    agrega_prodcuto_a_fila(ui)


def obtener_productos_por_proveedor(proveedor_id):
    with conexion() as c, c.cursor() as cur:
        cur.execute("""
            SELECT id_producto, nombre
            FROM productos
            WHERE id_proveedor = %s
            ORDER BY nombre;
        """, (proveedor_id,))
        return cur.fetchall()


def on_proveedor_selected(ui_nueva_compra):
    proveedor_id = ui_nueva_compra.comboBox.currentData()
    productos = obtener_productos_por_proveedor(proveedor_id)

    if not productos:
        if hasattr(ui_nueva_compra, "labelErrorProveedor"):
            ui_nueva_compra.labelErrorProveedor.setText("⚠️ Este proveedor no tiene productos.")
            ui_nueva_compra.labelErrorProveedor.setStyleSheet("color: red;")
            ui_nueva_compra.labelErrorProveedor.show()
        ui_nueva_compra.pushButtonAgregarProducto.setEnabled(False)
        return

    if hasattr(ui_nueva_compra, "labelErrorProveedor"):
        ui_nueva_compra.labelErrorProveedor.hide()
    ui_nueva_compra.pushButtonAgregarProducto.setEnabled(True)


# ---------- GUARDAR COMPRA ----------
def _validar_fila(ui_tbl, row):
    combo = ui_tbl.cellWidget(row, 0)
    spin  = ui_tbl.cellWidget(row, 1)
    item_precio = ui_tbl.item(row, 2)
    if not (combo and spin and item_precio):
        return False, "Fila incompleta."

    id_producto = combo.currentData()
    if id_producto is None:
        return False, "Hay filas sin producto seleccionado."

    try:
        cantidad = int(spin.value())
    except Exception:
        cantidad = 0
    if cantidad <= 0:
        return False, "Hay filas con cantidad inválida."

    try:
        precio_unitario = float(item_precio.text().replace(".", "").replace(",", ".") or 0)
    except Exception:
        precio_unitario = 0.0
    if precio_unitario <= 0:
        return False, "Hay filas con precio unitario 0."

    return True, ""


def SaveSellIntoDb(ui_nueva_venta, ui, form):
    try:
        # Validaciones previas
        filas = ui_nueva_venta.tableWidget.rowCount()
        if filas == 0:
            QMessageBox.warning(None, "Datos incompletos", "Agregá al menos un producto.")
            return

        for r in range(filas):
            ok, msg = _validar_fila(ui_nueva_venta.tableWidget, r)
            if not ok:
                QMessageBox.warning(None, "Datos incompletos", msg)
                return

        with conexion() as c, c.cursor() as cur:
            fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            id_proveedor = ui_nueva_venta.comboBox.currentData()
            medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()

            # Encabezado
            cur.execute("""
                INSERT INTO compras (fecha, id_proveedor, medio_pago, total_compra)
                VALUES (%s, %s, %s, 0)
                RETURNING id_compra;
            """, (fecha, id_proveedor, medio_pago))
            id_compra = cur.fetchone()[0]

            # Detalles (triggers ajustan stock/total)
            for r in range(filas):
                combo = ui_nueva_venta.tableWidget.cellWidget(r, 0)
                spin  = ui_nueva_venta.tableWidget.cellWidget(r, 1)
                item_precio = ui_nueva_venta.tableWidget.item(r, 2)
                id_producto = combo.currentData()
                cantidad = int(spin.value())
                precio_unitario = float(item_precio.text().replace(".", "").replace(",", ".") or 0)

                cur.execute("""
                    INSERT INTO compra_detalles (id_compra, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s);
                """, (id_compra, id_producto, cantidad, precio_unitario))
            c.commit()

        # Refrescar UI
        ui.treeWidget.clear()
        setRowsTreeWidget(ui, form)
        if hasattr(ui, "_post_refresh"):
            ui._post_refresh()
        ui.formulario_nueva_compra.close()
        print(f"Compra registrada con ID: {id_compra}")

    except Exception as e:
        print(f"[SaveSellIntoDb] Error: {e}")
        QMessageBox.critical(None, "Error", f"No se pudo registrar la compra.\n{e}")


# ---------- CARGAR LISTA DE COMPRAS ----------
def setRowsTreeWidget(ui, Form):
    ui.treeWidget.clear()
    with conexion() as c, c.cursor() as cur:
        # Encabezados
        cur.execute("""
            SELECT cp.id_compra, cp.fecha, pr.nombre, cp.total_compra, cp.medio_pago, cp.factura
            FROM compras cp
            JOIN proveedores pr ON cp.id_proveedor = pr.id_proveedor
            ORDER BY cp.fecha DESC;
        """)
        compras = cur.fetchall()
        if not compras:
            return

        # Traer detalles en lote (evita N+1)
        ids = [row[0] for row in compras]
        cur.execute("""
            SELECT cd.id_compra, p.nombre, cd.cantidad, cd.precio_unitario, cd.subtotal
            FROM compra_detalles cd
            JOIN productos p ON p.id_producto = cd.id_producto
            WHERE cd.id_compra = ANY(%s)
            ORDER BY cd.id_compra, p.nombre;
        """, (ids,))
        det_rows = cur.fetchall()

    # Indexar detalles por compra
    det_map = {}
    for id_compra, nombre, cant, precio, subtotal in det_rows:
        det_map.setdefault(id_compra, []).append((nombre, cant, precio, subtotal))

    # Poblar árbol
    for id_compra, fecha, proveedor, total, medio, factura in compras:
        item_compra = QTreeWidgetItem()
        item_compra.setText(0, str(id_compra))
        # soporta datetime o string
        fecha_txt = fecha.strftime("%Y-%m-%d %H:%M:%S") if hasattr(fecha, "strftime") else str(fecha)
        item_compra.setText(1, fecha_txt)
        item_compra.setText(2, str(proveedor))
        item_compra.setText(3, formatear_numero(total))
        item_compra.setText(4, str(medio))
        item_compra.setText(5, "Sí" if factura else "No")
        ui.treeWidget.addTopLevelItem(item_compra)

        # Header de detalle
        header_hijo = QTreeWidgetItem()
        header_hijo.setText(1, "Producto")
        header_hijo.setText(2, "Cantidad")
        header_hijo.setText(3, "Precio Unitario")
        header_hijo.setText(4, "Subtotal")
        item_compra.addChild(header_hijo)

        for col in range(1, 5):
            header_hijo.setBackground(col, QBrush(QColor("#dcdcdc")))
            header_hijo.setForeground(col, QBrush(QColor("#2c3e50")))
            f = QFont(); f.setBold(True)
            header_hijo.setFont(col, f)

        for nombre, cantidad, precio, subtotal in det_map.get(id_compra, []):
            hijo = QTreeWidgetItem()
            hijo.setText(1, nombre)
            hijo.setText(2, str(cantidad))
            hijo.setText(3, formatear_numero(precio))
            hijo.setText(4, formatear_numero(subtotal))
            item_compra.addChild(hijo)

        # Botones
        agregar_botones_opciones_compra(ui.treeWidget, item_compra, ui, Form)


def eliminar_compra(treeWidget, item_compra):
    if not item_compra:
        return
    id_compra = int(item_compra.text(0))

    reply = QMessageBox.question(None, 'Eliminar compra',
                                 f"¿Eliminar la compra #{id_compra}? (se revertirá el stock)",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    try:
        with conexion() as c, c.cursor() as cur:
            # Borrar detalles primero (triggers restan stock)
            cur.execute("DELETE FROM compra_detalles WHERE id_compra = %s", (id_compra,))
            # Luego encabezado
            cur.execute("DELETE FROM compras WHERE id_compra = %s", (id_compra,))
            c.commit()
        treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(item_compra))
    except Exception as e:
        print(f"[eliminar_compra] Error: {e}")


def agregar_botones_opciones_compra(treeWidget, item_compra, ui, Form):
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 15, 0)
    layout.setSpacing(12)

    # Editar (icon-only)
    btn_editar = QPushButton()
    btn_editar.setObjectName("btnCompraEditar")
    btn_editar.setProperty("perm_code", "compras.update")
    btn_editar.setProperty("type", "icon")
    btn_editar.setProperty("variant", "edit")
    btn_editar.setCursor(Qt.PointingHandCursor)
    btn_editar.setIcon(themed_icon("edit"))
    btn_editar.setText("")
    btn_editar.setToolTip("Editar compra")
    btn_editar.setFixedHeight(25)

    # Eliminar (icon-only)
    btn_eliminar = QPushButton()
    btn_eliminar.setObjectName("btnCompraEliminar")
    btn_eliminar.setProperty("perm_code", "compras.delete")
    btn_eliminar.setProperty("type", "icon")
    btn_eliminar.setProperty("variant", "delete")
    btn_eliminar.setCursor(Qt.PointingHandCursor)
    btn_eliminar.setIcon(themed_icon("trash"))
    btn_eliminar.setText("")
    btn_eliminar.setToolTip("Eliminar compra")
    btn_eliminar.setFixedHeight(25)

    # refrescar estilo para que tome las props
    btn_editar.style().unpolish(btn_editar); btn_editar.style().polish(btn_editar)
    btn_eliminar.style().unpolish(btn_eliminar); btn_eliminar.style().polish(btn_eliminar)

    layout.addWidget(btn_editar)
    layout.addWidget(btn_eliminar)
    widget.setLayout(layout)

    treeWidget.setItemWidget(item_compra, 6, widget)
    treeWidget.setColumnWidth(6, 120)

    btn_editar.clicked.connect(lambda: editar_compra(item_compra, ui, Form))
    btn_eliminar.clicked.connect(lambda: eliminar_compra(treeWidget, item_compra))


def editar_compra(item_compra, ui, Form, edicion=False):
    if not item_compra:
        return

    id_compra = item_compra.text(0)
    ui.abrir_formulario_nueva_compra(Form, edicion=True)
    ui_nueva = ui.ui_nueva_compra

    # Cabecera + proveedores
    with conexion() as c, c.cursor() as cur:
        cur.execute("""
            SELECT id_proveedor, fecha, factura, medio_pago
            FROM compras
            WHERE id_compra = %s
        """, (id_compra,))
        compra = cur.fetchone()
        if not compra:
            return
        id_proveedor, fecha, factura, medio_pago = compra

        cur.execute("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre")
        proveedores = cur.fetchall()

    # Llenar combo de proveedores sin disparar señales que limpien la tabla
    ui_nueva.comboBox.blockSignals(True)
    ui_nueva.comboBox.clear()
    idx = 0
    for i, (idp, nombre) in enumerate(proveedores):
        ui_nueva.comboBox.addItem(nombre, idp)
        if idp == id_proveedor:
            idx = i
    ui_nueva.comboBox.setCurrentIndex(idx)
    ui_nueva.comboBox.blockSignals(False)

    # Fecha y medio
    try:
        ui_nueva.dateTimeEditCliente.setDateTime(QDateTime.fromSecsSinceEpoch(int(fecha.timestamp())))
    except Exception:
        pass
    pos_medio = ui_nueva.comboBoxMedioPago.findText(medio_pago)
    if pos_medio >= 0:
        ui_nueva.comboBoxMedioPago.setCurrentIndex(pos_medio)

    # Detalles
    with conexion() as c, c.cursor() as cur:
        cur.execute("""
            SELECT cd.id_producto, cd.cantidad, cd.precio_unitario, cd.subtotal
            FROM compra_detalles cd
            WHERE cd.id_compra = %s
        """, (id_compra,))
        detalles = cur.fetchall()

    # cache productos/precios
    _ensure_producto_cache(ui_nueva, id_proveedor)

    ui_nueva.tableWidget.blockSignals(True)
    ui_nueva.tableWidget.setRowCount(0)
    for i, (id_producto, cantidad, precio_unitario, subtotal) in enumerate(detalles):
        ui_nueva.tableWidget.insertRow(i)

        combo = QComboBox()
        combo.addItem("Seleccione", None)
        pos_prod = 0
        for j, (pid, nombrep, _pr) in enumerate(ui_nueva._prod_lista):
            combo.addItem(nombrep, pid)
            if pid == id_producto:
                pos_prod = j + 1  # +1 por "Seleccione"
        combo.blockSignals(True)
        combo.setCurrentIndex(pos_prod)
        combo.blockSignals(False)

        spin = QSpinBox(); spin.setMinimum(1); spin.setValue(int(cantidad))
        ui_nueva.tableWidget.setCellWidget(i, 0, combo)
        ui_nueva.tableWidget.setCellWidget(i, 1, spin)

        item_precio = QTableWidgetItem(formatear_numero(precio_unitario))
        _set_ro(item_precio, item_precio.text()); ui_nueva.tableWidget.setItem(i, 2, item_precio)

        item_sub = QTableWidgetItem(formatear_numero(subtotal))
        _set_ro(item_sub, item_sub.text()); ui_nueva.tableWidget.setItem(i, 3, item_sub)

        # conectar señales ignorando el parámetro extra
        combo.currentIndexChanged.connect(lambda *_ , rr=i, uu=ui_nueva: actualizar_subtotal(rr, uu))
        spin.valueChanged.connect(lambda *_ , rr=i, uu=ui_nueva: actualizar_subtotal(rr, uu))

    ui_nueva.tableWidget.blockSignals(False)
    calcular_total_general(ui_nueva)

    # Aceptar -> actualizar compra
    try:
        ui_nueva.pushButtonAceptar.clicked.disconnect()
    except Exception:
        pass
    ui_nueva.pushButtonAceptar.clicked.connect(lambda: actualizar_compra_en_db(ui_nueva, id_compra, ui, Form))


def actualizar_compra_en_db(ui_nueva_compra, id_compra, ui, Form):
    try:
        # Validaciones previas
        filas = ui_nueva_compra.tableWidget.rowCount()
        if filas == 0:
            QMessageBox.warning(None, "Datos incompletos", "Agregá al menos un producto.")
            return
        for r in range(filas):
            ok, msg = _validar_fila(ui_nueva_compra.tableWidget, r)
            if not ok:
                QMessageBox.warning(None, "Datos incompletos", msg)
                return

        with conexion() as c, c.cursor() as cur:
            # Borrar detalles viejos (triggers restan stock)
            cur.execute("DELETE FROM compra_detalles WHERE id_compra = %s", (id_compra,))

            # Insertar detalles nuevos (triggers suman stock)
            for r in range(filas):
                combo = ui_nueva_compra.tableWidget.cellWidget(r, 0)
                spin  = ui_nueva_compra.tableWidget.cellWidget(r, 1)
                id_producto = combo.currentData()
                cantidad = int(spin.value())
                precio_unitario = float(
                    ui_nueva_compra.tableWidget.item(r, 2).text()
                    .replace(".", "")
                    .replace(",", ".") or 0
                )

                cur.execute("""
                    INSERT INTO compra_detalles (id_compra, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (id_compra, id_producto, cantidad, precio_unitario))

            # Cabecera
            id_proveedor = ui_nueva_compra.comboBox.currentData()
            fecha = ui_nueva_compra.dateTimeEditCliente.dateTime().toPython()
            medio_pago = ui_nueva_compra.comboBoxMedioPago.currentText()

            cur.execute("""
                UPDATE compras
                SET id_proveedor = %s, fecha = %s, medio_pago = %s
                WHERE id_compra = %s
            """, (id_proveedor, fecha, medio_pago, id_compra))
            c.commit()

        ui.treeWidget.clear()
        setRowsTreeWidget(ui, Form)
        if hasattr(ui, "_post_refresh"):
            ui._post_refresh()
        ui.formulario_nueva_compra.close()
        print(f"Compra {id_compra} actualizada correctamente.")

    except Exception as e:
        print(f"[actualizar_compra_en_db] Error: {e}")
        QMessageBox.critical(None, "Error", f"No se pudo actualizar la compra.\n{e}")
