import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.conexion import conexion
from PySide6.QtWidgets import QSpinBox, QComboBox, QTableWidgetItem, QPushButton, QWidget, QTreeWidgetItem, QHBoxLayout
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QDateTime
from utils.utilsCompras import calcular_total_general



# ---------- CALCULAR SUBTOTAL FILA ----------
def actualizar_subtotal(row, ui):
    try:
        combo = ui.tableWidget.cellWidget(row, 0)  # Producto
        spin = ui.tableWidget.cellWidget(row, 1)   # Cantidad

        if combo is None or spin is None:
            return

        id_producto = combo.currentData()
        cantidad = spin.value() or 1

        if id_producto is None:
            return

        # Precio de referencia (usamos precio_venta por ahora)
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("SELECT precio_venta FROM productos WHERE id_producto = %s", (id_producto,))
                res = cur.fetchone()

        if res:
            precio_unitario = float(res[0] or 0)
            subtotal = precio_unitario * cantidad if cantidad > 0 else precio_unitario

            ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{precio_unitario:.2f}"))
            ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            calcular_total_general(ui)
    except Exception as e:
        print(f"[actualizar_subtotal] Error fila {row}: {e}")


# ---------- AGREGAR UNA FILA ----------
def agrega_prodcuto_a_fila(ui_nueva_compra):
    row = ui_nueva_compra.tableWidget.rowCount()
    ui_nueva_compra.tableWidget.insertRow(row)

    combo = QComboBox()
    ui_nueva_compra.tableWidget.setCellWidget(row, 0, combo)

    # Filtrar productos por proveedor
    id_proveedor = ui_nueva_compra.comboBox.currentData()
    if id_proveedor is None:
        return

    with conexion() as c:
        with c.cursor() as cur:
            cur.execute("""
                SELECT id_producto, nombre, precio_venta
                FROM productos
                WHERE id_proveedor = %s
                ORDER BY nombre;
            """, (id_proveedor,))
            productos = cur.fetchall()

    if not productos:
        return

    ui_nueva_compra.precios = {}
    for idp, nombrep, preciop in productos:
        combo.addItem(nombrep, idp)
        ui_nueva_compra.precios[nombrep] = float(preciop or 0)

    spin = QSpinBox()
    spin.setMinimum(1)
    spin.setMaximum(999)

    ui_nueva_compra.tableWidget.setCellWidget(row, 1, spin)

    # Precio y subtotal inicial
    precio_unitario_valor = ui_nueva_compra.precios.get(combo.currentText(), 0.0)
    item_precio_unitario = QTableWidgetItem(f"{precio_unitario_valor:.2f}")
    item_precio_unitario.setFlags(item_precio_unitario.flags() ^ Qt.ItemIsEditable)
    ui_nueva_compra.tableWidget.setItem(row, 2, item_precio_unitario)

    subtotal = QTableWidgetItem("0.00")
    subtotal.setFlags(subtotal.flags() ^ Qt.ItemIsEditable)
    ui_nueva_compra.tableWidget.setItem(row, 3, subtotal)

    # Señales
    combo.currentIndexChanged.connect(lambda: actualizar_subtotal(row, ui_nueva_compra))
    spin.valueChanged.connect(lambda: actualizar_subtotal(row, ui_nueva_compra))
    combo.currentIndexChanged.connect(lambda: calcular_total_general(ui_nueva_compra))
    spin.valueChanged.connect(lambda: calcular_total_general(ui_nueva_compra))


def reiniciar_tabla_productos(ui):
    ui.tableWidget.setRowCount(0)
    agrega_prodcuto_a_fila(ui)


def obtener_productos_por_proveedor(proveedor_id):
    with conexion() as c:
        with c.cursor() as cur:
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
def SaveSellIntoDb(ui_nueva_venta, ui, form):
    try:
        with conexion() as c:
            with c.cursor() as cur:
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

                # Detalles (triggers ajustan stock y total_compra)
                for row in range(ui_nueva_venta.tableWidget.rowCount()):
                    combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
                    spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
                    item_precio_unitario = ui_nueva_venta.tableWidget.item(row, 2)

                    if not (combo and spin and item_precio_unitario):
                        continue

                    id_producto = combo.currentData()
                    cantidad = spin.value()
                    precio_unitario = float(item_precio_unitario.text() or 0)

                    cur.execute("""
                        INSERT INTO compra_detalles (id_compra, id_producto, cantidad, precio_unitario)
                        VALUES (%s, %s, %s, %s);
                    """, (id_compra, id_producto, cantidad, precio_unitario))

            c.commit()

        # Refrescar UI
        ui.treeWidget.clear()
        setRowsTreeWidget(ui, form)
        ui.formulario_nueva_compra.close()
        print(f"Compra registrada con ID: {id_compra}")

    except Exception as e:
        print(f"[SaveSellIntoDb] Error: {e}")


# ---------- CARGAR LISTA DE COMPRAS ----------
def setRowsTreeWidget(ui, Form):
    ui.treeWidget.clear()
    with conexion() as c:
        with c.cursor() as cur:
            cur.execute("""
                SELECT cp.id_compra, cp.fecha, pr.nombre, cp.total_compra, cp.medio_pago, cp.factura
                FROM compras cp
                JOIN proveedores pr ON cp.id_proveedor = pr.id_proveedor
                ORDER BY cp.fecha DESC;
            """)
            compras = cur.fetchall()

            for id_compra, fecha, proveedor, total, medio, factura in compras:
                item_compra = QTreeWidgetItem()
                item_compra.setText(0, str(id_compra))
                item_compra.setText(1, fecha.strftime("%Y-%m-%d %H:%M:%S"))
                item_compra.setText(2, str(proveedor))
                item_compra.setText(3, f"{total:.2f}")
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
                    font = QFont()
                    font.setBold(True)
                    header_hijo.setFont(col, font)

                # Detalles
                cur.execute("""
                    SELECT p.nombre, cd.cantidad, cd.precio_unitario, cd.subtotal
                    FROM compra_detalles cd
                    JOIN productos p ON p.id_producto = cd.id_producto
                    WHERE cd.id_compra = %s
                    ORDER BY p.nombre;
                """, (id_compra,))
                detalles = cur.fetchall()

                for nombre, cantidad, precio, subtotal in detalles:
                    hijo = QTreeWidgetItem()
                    hijo.setText(1, nombre)
                    hijo.setText(2, str(cantidad))
                    hijo.setText(3, f"{precio:.2f}")
                    hijo.setText(4, f"{subtotal:.2f}")
                    item_compra.addChild(hijo)

                # Botones
                agregar_botones_opciones_compra(ui.treeWidget, item_compra, ui, Form)


def eliminar_compra(treeWidget, item_compra):
    if not item_compra:
        return
    id_compra = int(item_compra.text(0))
    from PySide6.QtWidgets import QMessageBox
    reply = QMessageBox.question(None, 'Eliminar compra',
                                 f"¿Eliminar la compra #{id_compra}? (se revertirá el stock)",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    try:
        with conexion() as c:
            with c.cursor() as cur:
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

    btn_editar = QPushButton("Editar")
    btn_eliminar = QPushButton("Eliminar")
    btn_editar.setFixedHeight(25)
    btn_eliminar.setFixedHeight(25)
    btn_eliminar.setStyleSheet("background-color: red; color: white;")

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
    # Abrir formulario en modo edición
    ui.abrir_formulario_nueva_compra(Form, edicion=True)
    ui_nueva = ui.ui_nueva_compra

    with conexion() as c:
        with c.cursor() as cur:
            # Cabecera
            cur.execute("""
                SELECT id_proveedor, fecha, factura, medio_pago
                FROM compras
                WHERE id_compra = %s
            """, (id_compra,))
            compra = cur.fetchone()
            if not compra:
                return
            id_proveedor, fecha, factura, medio_pago = compra

            # Proveedores
            cur.execute("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre")
            proveedores = cur.fetchall()
    # Cargar combos fuera del with
    ui_nueva.comboBox.clear()
    idx = 0
    for i, (idp, nombre) in enumerate(proveedores):
        ui_nueva.comboBox.addItem(nombre, idp)
        if idp == id_proveedor:
            idx = i
    ui_nueva.comboBox.setCurrentIndex(idx)

    # Fecha y medio
    ui_nueva.dateTimeEditCliente.setDateTime(QDateTime.fromSecsSinceEpoch(int(fecha.timestamp())))
    pos_medio = ui_nueva.comboBoxMedioPago.findText(medio_pago)
    if pos_medio >= 0:
        ui_nueva.comboBoxMedioPago.setCurrentIndex(pos_medio)

    # Detalles
    ui_nueva.tableWidget.setRowCount(0)

    with conexion() as c:
        with c.cursor() as cur:
            cur.execute("""
                SELECT cd.id_producto, cd.cantidad, cd.precio_unitario, cd.subtotal
                FROM compra_detalles cd
                WHERE cd.id_compra = %s
            """, (id_compra,))
            detalles = cur.fetchall()

            cur.execute("""
                SELECT id_producto, nombre
                FROM productos
                WHERE id_proveedor = %s
                ORDER BY nombre;
            """, (id_proveedor,))
            productos = cur.fetchall()

    # Cargar filas y conectar señales por fila
    for i, (id_producto, cantidad, precio_unitario, subtotal) in enumerate(detalles):
        ui_nueva.tableWidget.insertRow(i)

        combo = QComboBox()
        pos_prod = 0
        for j, (pid, nombrep) in enumerate(productos):
            combo.addItem(nombrep, pid)
            if pid == id_producto:
                pos_prod = j
        combo.setCurrentIndex(pos_prod)

        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setValue(int(cantidad))

        ui_nueva.tableWidget.setCellWidget(i, 0, combo)
        ui_nueva.tableWidget.setCellWidget(i, 1, spin)

        ui_nueva.tableWidget.setItem(i, 2, QTableWidgetItem(f"{float(precio_unitario):.2f}"))
        ui_nueva.tableWidget.setItem(i, 3, QTableWidgetItem(f"{float(subtotal):.2f}"))

        combo.currentIndexChanged.connect(lambda _, row=i: actualizar_subtotal(row, ui_nueva))
        spin.valueChanged.connect(lambda _, row=i: actualizar_subtotal(row, ui_nueva))

    calcular_total_general(ui_nueva)

    # Botón aceptar -> actualizar compra
    try:
        ui_nueva.pushButtonAceptar.clicked.disconnect()
    except Exception:
        pass
    ui_nueva.pushButtonAceptar.clicked.connect(lambda: actualizar_compra_en_db(ui_nueva, id_compra, ui, Form))


def actualizar_compra_en_db(ui_nueva_compra, id_compra, ui, Form):
    try:
        with conexion() as c:
            with c.cursor() as cur:
                # Borrar detalles viejos (triggers restan stock)
                cur.execute("DELETE FROM compra_detalles WHERE id_compra = %s", (id_compra,))

                # Insertar detalles nuevos (triggers suman stock)
                for row in range(ui_nueva_compra.tableWidget.rowCount()):
                    combo = ui_nueva_compra.tableWidget.cellWidget(row, 0)
                    spin = ui_nueva_compra.tableWidget.cellWidget(row, 1)
                    if not (combo and spin):
                        continue
                    id_producto = combo.currentData()
                    cantidad = spin.value()
                    precio_unitario = float(ui_nueva_compra.tableWidget.item(row, 2).text() or 0)

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
        ui.formulario_nueva_compra.close()
        print(f"Compra {id_compra} actualizada correctamente.")

    except Exception as e:
        print(f"[actualizar_compra_en_db] Error: {e}")
