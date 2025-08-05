
from db.conexion import conexion
from PySide6.QtWidgets import QSpinBox, QComboBox, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout, QTableWidget, QTreeWidget, QTreeWidgetItem, QHBoxLayout
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime
from utils.utilsCompras import calcular_total_general

    

#FUNCION DE ACTUALIZAR PRODUCTOS
def actualizar_subtotal(row, ui):
    try:
        print("Se actualizo el subtotal")
        combo = ui.tableWidget.cellWidget(row, 0)  # Producto
        spin = ui.tableWidget.cellWidget(row, 1)   # Cantidad

        if combo is None or spin is None:
            print(f"[Fila {row}] Combo o Spin no existen todavía.")
            return

        id_producto = combo.currentData()
        cantidad_texto = spin.text().strip()
        if cantidad_texto == "":
            cantidad = 1  # valor por defecto si está vacío
        else:
            cantidad = int(cantidad_texto)

        if id_producto is None:
            print(f"[Fila {row}] Producto no seleccionado.")
            return

        # Obtener precio desde la BD
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("SELECT precio_venta FROM productos WHERE id_producto = %s", (id_producto,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion_db.close()

        if resultado:
            precio_unitario = resultado[0]
            if cantidad <= 0:
                subtotal = precio_unitario
            else:
                subtotal = precio_unitario * cantidad

            # Insertar en la tabla
            ui.tableWidget.setItem(row, 2, QTableWidgetItem(f"{precio_unitario:.2f}"))
            ui.tableWidget.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))

            # Opcional: actualizar total general
            calcular_total_general(ui)

        else:
            print(f"[Fila {row}] No se encontró precio para el producto con ID {id_producto}.")

    except Exception as e:
        print(f"Error en actualizar_subtotal (fila {row}): {e}")
        

    
        

#FUNCION PARA EL BOTON AGREGAR MAS FILAS
def agrega_prodcuto_a_fila(ui_nueva_compra):
    row_position = ui_nueva_compra.tableWidget.rowCount()
    ui_nueva_compra.tableWidget.insertRow(row_position)

    ui_nueva_compra.combo = QComboBox()
    
    
    # Obtener ID del proveedor actual
    id_proveedor = ui_nueva_compra.comboBox.currentData()

    if id_proveedor is None:
        print("Ningún proveedor seleccionado.")
        return

    conexion_db = conexion()
    cursor = conexion_db.cursor()

    # Solo productos de este proveedor
    cursor.execute("""
        SELECT id_producto, nombre, precio_venta
        FROM productos 
        WHERE id_proveedor = %s;
    """, (id_proveedor,))
    
    productos = cursor.fetchall()
    cursor.close()
    conexion_db.close()

    if not productos:
        print(f"No hay productos para el proveedor {id_proveedor}")
        return

    ui_nueva_compra.precios = {}

    for idp, nombrep, preciop in productos:
        ui_nueva_compra.combo.addItem(nombrep, idp)
        ui_nueva_compra.precios[nombrep] = preciop

    ui_nueva_compra.tableWidget.setCellWidget(row_position, 0, ui_nueva_compra.combo)

    # SpinBox
    spin = QSpinBox()
    spin.setMinimum(1)
    spin.setMaximum(999)
    ui_nueva_compra.tableWidget.setCellWidget(row_position, 1, spin)

    # Precio y Subtotal
    precio_unitario_valor = ui_nueva_compra.precios.get(ui_nueva_compra.combo.currentText(), 0)
    item_precio_unitario = QTableWidgetItem(str(precio_unitario_valor))
    item_precio_unitario.setFlags(item_precio_unitario.flags() ^ Qt.ItemIsEditable)
    ui_nueva_compra.tableWidget.setItem(row_position, 2, item_precio_unitario)

    subtotal = QTableWidgetItem("0")
    ui_nueva_compra.tableWidget.setItem(row_position, 3, subtotal)

    # Conexiones
    ui_nueva_compra.combo.currentIndexChanged.connect(lambda: actualizar_subtotal(row_position, ui_nueva_compra))
    spin.valueChanged.connect(lambda: actualizar_subtotal(row_position, ui_nueva_compra))
    ui_nueva_compra.combo.currentIndexChanged.connect(lambda: calcular_total_general(ui_nueva_compra))
    spin.valueChanged.connect(lambda: calcular_total_general(ui_nueva_compra))
    
def reiniciar_tabla_productos(ui):
    ui.tableWidget.setRowCount(0)
    agrega_prodcuto_a_fila(ui) 
    
    
def obtener_productos_por_proveedor(proveedor_id):
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    query = """
        SELECT id_producto, nombre
        FROM productos
        WHERE id_proveedor = %s
    """
    cursor.execute(query, (proveedor_id,))
    productos = cursor.fetchall()  # [(1, 'Cemento Cecon'), (2, 'Hierro Cecon')]
    conexion_db.close()
    return productos

def on_proveedor_selected(ui_nueva_compra):
    proveedor_id = ui_nueva_compra.comboBox.currentData()
    productos = obtener_productos_por_proveedor(proveedor_id)
     
    if not productos:
        ui_nueva_compra.labelErrorProveedor.setText("⚠️ Este proveedor no tiene productos registrados.")
        ui_nueva_compra.labelErrorProveedor.setStyleSheet("color: red;")
        ui_nueva_compra.labelErrorProveedor.show()
        
        
        ui_nueva_compra.pushButtonAgregarProducto.setEnabled(False)
        return
    
    ui_nueva_compra.labelErrorProveedor.hide()
    ui_nueva_compra.comboBox.setEnabled(True)
    
    #for id_producto, nombre in productos:
    #    ui_nueva_compra.comboBox.addItem(nombre, id_producto)
        
    validar_filas_por_proveedor(ui_nueva_compra)
    ui_nueva_compra.pushButtonAgregarProducto.clicked.connect(lambda: validar_filas_por_proveedor(ui_nueva_compra))
    ui_nueva_compra.pushButtonQuitarProducto.clicked.connect(lambda: validar_filas_por_proveedor(ui_nueva_compra))
        
def validar_filas_por_proveedor(ui_nueva_compra):
    proveedor_id = ui_nueva_compra.comboBox.currentData()
    productos = obtener_productos_por_proveedor(proveedor_id)
    row_position = ui_nueva_compra.tableWidget.rowCount()

    if row_position >= len(productos):
        ui_nueva_compra.pushButtonAgregarProducto.setEnabled(False)
    else:
        ui_nueva_compra.pushButtonAgregarProducto.setEnabled(True)

    print(f"Filas actuales: {row_position} / Productos posibles: {len(productos)}")



def SaveSellIntoDb(ui_nueva_venta, ui, form):
    
    conexion_db = conexion()
    cursor = conexion_db.cursor()    
    
    try:
        fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        id_proveedor = ui_nueva_venta.comboBox.currentData()
        medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()
        #factura = ui_nueva_venta.checkBox_factura.isChecked()




        cursor.execute("""
                    INSERT INTO compras (fecha, id_proveedor, medio_pago)  
                    VALUES (%s, %s, %s)
                    RETURNING id_compra
                    """, (fecha, id_proveedor, medio_pago))
        conexion_db.commit()

        id_compra = cursor.fetchone()[0]

        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            item_producto = ui_nueva_venta.tableWidget.cellWidget(row, 0) 
            cantidad_producto = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            item_precio_unitario = ui_nueva_venta.tableWidget.item(row, 2)
            
            if item_producto and cantidad_producto and item_precio_unitario:
                id_producto = item_producto.currentData()
                cantidad = cantidad_producto.value()
                precio_unitario = float(item_precio_unitario.text())

                cursor.execute("""
                               INSERT INTO compra_detalles (id_compra, id_producto, cantidad, precio_unitario)
                               VALUES (%s, %s, %s, %s)
                                """, (id_compra, id_producto, cantidad, precio_unitario))

        conexion_db.commit() 
        print(f"Compra registrada con ID: {id_compra}")

        cursor.close()
        conexion_db.close()
    except Exception as e:
        conexion_db.rollback()
        print(f'Error al guardar la compra: {e}')

    
    finally:
        ui.treeWidget.clear()
        setRowsTreeWidget(ui, form)
        ui.formulario_nueva_compra.close()
        conexion_db.close()
        cursor.close()
        
        
                

def setRowsTreeWidget(ui, Form):
    
    ui.treeWidget.clear()

    conexion_db = conexion()
    cursor = conexion_db.cursor()
    cursor.execute("""
                   SELECT id_compra, fecha, p.nombre , total_compra, medio_pago, factura FROM compras
                   JOIN proveedores p ON compras.id_proveedor = p.id_proveedor
                   ORDER BY compras.fecha DESC
                   """)
    
    compra = cursor.fetchall()
    
    for item in compra:
        id_compra, fecha, id_proveedor, total_compra, medio_pago, factura = item
        
        item_compra = QTreeWidgetItem()
        item_compra.setText(0, str(id_compra))
        item_compra.setText(1, fecha.strftime("%Y-%m-%d %H:%M:%S"))
        item_compra.setText(2, str(id_proveedor))
        item_compra.setText(3, str(total_compra))
        item_compra.setText(4, medio_pago)
        
        ui.treeWidget.addTopLevelItem(item_compra)
        
        header_hijo = QTreeWidgetItem()
        header_hijo.setText(0, "ID Producto")
        header_hijo.setText(1, "Nombre Producto")
        header_hijo.setText(2, "Cantidad")
        header_hijo.setText(3, "Precio Unitario")
        header_hijo.setText(4, "Subtotal")
        
        item_compra.addChild(header_hijo)
        
        for col in range(1, 5):
            header_hijo.setBackground(col, QBrush(QColor("#dcdcdc")))  # gris claro
            header_hijo.setForeground(col, QBrush(QColor("#2c3e50")))  # texto oscuro

        font = QFont()
        font.setBold(True)
        for col in range(1, 5):
            header_hijo.setFont(col, font)
        

        cursor.execute("""
                       SELECT id_detalle, id_compra, p.nombre, cantidad, precio_unitario, subtotal FROM compra_detalles
                       JOIN productos p ON compra_detalles.id_producto = p.id_producto
                       WHERE id_compra = %s
                          """, (id_compra,))
        
        detalles = cursor.fetchall()
        
        for detalle in detalles:
            id_detalle, id_compra, nombre, cantidad, precio_unitario, subtotal = detalle
            
            item_subVenta = QTreeWidgetItem()
            item_subVenta.setText(0, str(id_detalle))
            item_subVenta.setText(1, nombre)
            item_subVenta.setText(2, str(cantidad))
            item_subVenta.setText(3, str(precio_unitario))
            item_subVenta.setText(4, str(subtotal))
            
            item_compra.addChild(item_subVenta)
            
        agregar_botones_opciones_compra(ui.treeWidget, item_compra, ui, Form)
            

    conexion_db.close()
    cursor.close()
            
def editar_compra(item_compra, ui, Form, edicion = False):
    if not item_compra:
        print("No se ha seleccionado ninguna compra.")
        return

    id_compra = item_compra.text(0)
    print(f"Editando compra con ID: {id_compra}")

    if not hasattr(ui, 'formulario_nueva_compra') or not ui.formulario_nueva_compra.isVisible():
        ui.abrir_formulario_nueva_compra(Form, edicion=True)

    ui_nueva_compra = ui.ui_nueva_compra

    conexion_db = conexion()
    cursor = conexion_db.cursor()

    # Cargar cabecera de la compra
    cursor.execute("""
        SELECT id_proveedor, fecha, factura, medio_pago
        FROM compras
        WHERE id_compra = %s
    """, (id_compra,))
    
    compra = cursor.fetchone()
    if not compra:
        print(f"No se encontró la compra con ID {id_compra}.")
        return

    id_proveedor, fecha, factura, medio_pago = compra


    # Cargar proveedores en el comboBox
    cursor.execute("SELECT id_proveedor, nombre FROM proveedores")
    proveedores = cursor.fetchall()
    
    ui_nueva_compra.comboBox.clear()
    
    index_proveedor = 0
    for j, (idprov, nombreprov) in enumerate(proveedores):
        ui_nueva_compra.comboBox.addItem(nombreprov, idprov)
        if idprov == id_proveedor:
            index_proveedor = j
    
    
    ui_nueva_compra.comboBox.setCurrentIndex(index_proveedor)

    ## Ejecutar la función solo después de haber seleccionado el proveedor
    #on_proveedor_selected(ui_nueva_compra)


    # Cargar fecha
    fecha_qt = QDateTime.fromSecsSinceEpoch(int(fecha.timestamp()))
    ui_nueva_compra.dateTimeEditCliente.setDateTime(fecha_qt)

    # Cargar medio de pago
    index_medio_pago = ui_nueva_compra.comboBoxMedioPago.findText(medio_pago)
    if index_medio_pago >= 0:
        ui_nueva_compra.comboBoxMedioPago.setCurrentIndex(index_medio_pago)

    # Cargar productos comprados (detalle de compra)
    cursor.execute("""
        SELECT cd.id_producto, p.nombre, cd.cantidad, cd.precio_unitario, cd.subtotal
        FROM compra_detalles cd
        JOIN productos p ON p.id_producto = cd.id_producto
        WHERE cd.id_compra = %s
    """, (id_compra,))

    detalles = cursor.fetchall()
    ui_nueva_compra.tableWidget.setRowCount(0)
    
    cursor.execute("""
                    SELECT id_producto, nombre FROM productos
                    WHERE id_proveedor = %s
                    """, (id_proveedor,))
    
    productos = cursor.fetchall()

    for fila, (id_producto, nombre_producto, cantidad, precio_unitario, subtotal) in enumerate(detalles):
        ui_nueva_compra.tableWidget.insertRow(fila)
        
        combo = QComboBox()
        index_producto = 0
        
        for k, (idp, nombrep) in enumerate(productos):
            combo.addItem(nombrep, idp)
            if idp == id_producto:
                index_producto = k
        combo.setCurrentIndex(index_producto)
            
        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setValue(int(cantidad))
        
        
        ui_nueva_compra.tableWidget.setCellWidget(fila, 0, combo)
        ui_nueva_compra.tableWidget.setCellWidget(fila, 1, spin)
        
        if detalles:
            precio_unitario = precio_unitario
            ui_nueva_compra.tableWidget.setItem(fila, 2, QTableWidgetItem(f"{precio_unitario:.2f}"))
            
            ui_nueva_compra.tableWidget.setItem(fila, 3, QTableWidgetItem(f"{subtotal:.2f}"))
        else:
            print(f"No se encontró el precio o el subtotal del producto ID {id_producto}")
            
            
        
        
        try:
            ui_nueva_compra.pushButtonAceptar.clicked.disconnect()
        except Exception:
            pass 
        
    ui_nueva_compra.comboBox.currentIndexChanged.connect(lambda: reiniciar_tabla_productos(ui_nueva_compra))
    ui_nueva_compra.comboBox.currentIndexChanged.connect(lambda: on_proveedor_selected(ui_nueva_compra))
    on_proveedor_selected(ui_nueva_compra)
    combo.currentIndexChanged.connect(lambda _, row=fila: actualizar_subtotal(row, ui_nueva_compra))
    spin.valueChanged.connect(lambda _, row=fila: actualizar_subtotal(row, ui_nueva_compra))
    spin.lineEdit().textChanged.connect(lambda _, row=fila: actualizar_subtotal(row, ui_nueva_compra))    
    
    ui_nueva_compra.pushButtonAceptar.clicked.connect(lambda: actualizar_compra_en_db(ui_nueva_compra, id_compra, ui, Form))

        

        
    cursor.close()
    conexion_db.close()
    
    

def eliminar_compra(treeWidget, item_compra):
    if item_compra:
        id_compra = int(item_compra.text(0))

        # Confirmación básica
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(None, 'Eliminar compra',
                                     f"¿Estás seguro de eliminar la compra con ID {id_compra}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            try:
                # Elimina primero los detalles para evitar error de clave foránea
                cursor.execute("DELETE FROM compra_detalles WHERE id_compra = %s", (id_compra,))
                cursor.execute("DELETE FROM compras WHERE id_compra = %s", (id_compra,))
                conexion_db.commit()

                # Eliminar de la vista
                treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(item_compra))
                print(f" Compra {id_compra} eliminada correctamente.")
            except Exception as e:
                conexion_db.rollback()
                print(f"Error al eliminar: {e}")
            finally:
                cursor.close()
                conexion_db.close()
                   

def agregar_botones_opciones_compra(treeWidget, item_compra, ui, Form):
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

    # Crear un widget contenedor
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 15, 0) 
    layout.setSpacing(20)  


    # Crear botones
    btn_editar = QPushButton("Editar")
    btn_editar.setObjectName("btnEditarCompra")
    btn_editar.setMinimumWidth(70)


    btn_eliminar = QPushButton("Eliminar")
    btn_eliminar.setObjectName("btnEliminarCompra")
    btn_eliminar .setMinimumWidth(80)
    # Estilo opcional
    btn_editar.setFixedHeight(25)
    btn_eliminar.setFixedHeight(25)
    btn_editar.setStyleSheet("""
    font-size: 11px;
    padding: 6px 12px;
    background-color: black;
    """)
    btn_eliminar.setStyleSheet("""
        font-size: 11px;
        padding: 6px 12px;
        background-color: red;
        color: white;
    """)

    # Agregar botones al layout
    layout.addWidget(btn_editar)
    layout.addWidget(btn_eliminar)

    # Asignar layout al widget
    widget.setLayout(layout)
    # Insertar el widget en la columna 7 (o la que uses para los botones)
    treeWidget.setItemWidget(item_compra, 6, widget)
    treeWidget.setColumnWidth(6, 100)  
    treeWidget.resizeColumnToContents(6)

    # Conectar señales a funciones reales
    btn_editar.clicked.connect(lambda: editar_compra(item_compra, ui, Form))
    btn_eliminar.clicked.connect(lambda: eliminar_compra(treeWidget, item_compra))
    
    
    
def actualizar_compra_en_db(ui_nueva_compra, id_compra, ui, Form):
    
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    
    try:
        
        cursor.execute("""
            DELETE FROM compra_detalles
            WHERE id_compra = %s
        """, (id_compra,))
        
        for row in range(ui_nueva_compra.tableWidget.rowCount()):
            
            combo = ui_nueva_compra.tableWidget.cellWidget(row, 0)
            spin = ui_nueva_compra.tableWidget.cellWidget(row, 1)
            id_producto = combo.currentData()
            cantidad = spin.value()
            precio_unitario = float(ui_nueva_compra.tableWidget.item(row, 2).text())
            
            cursor.execute("""
                INSERT INTO compra_detalles (id_compra, id_producto, cantidad, precio_unitario )
                VALUES (%s, %s, %s, %s)
            """, (id_compra, id_producto, cantidad, precio_unitario))
              
        id_proveedor =  ui_nueva_compra.comboBox.currentData()
        fecha = ui_nueva_compra.dateTimeEditCliente.dateTime().toPython()
        medio_pago = ui_nueva_compra.comboBoxMedioPago.currentText()
        
        cursor.execute("""
            UPDATE compras 
            set id_proveedor = %s, fecha = %s,  medio_pago = %s
            WHERE id_compra = %s
        """, (id_proveedor, fecha, medio_pago, id_compra))

        conexion_db.commit()
        print(f"Compra {id_compra} actualizada correctamente.")
        
        ui.treeWidget.clear()
        setRowsTreeWidget(ui, Form)
        
        

    except Exception as e:
        conexion_db.rollback()
        print(f"Error al actualizar la venta: {e}")
        
    finally:
        ui.formulario_nueva_compra.close()
        cursor.close()
        conexion_db.close()