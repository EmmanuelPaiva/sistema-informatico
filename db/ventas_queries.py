from db.conexion import conexion
from PySide6.QtWidgets import QSpinBox, QComboBox, QTableWidgetItem, QPushButton, QWidget, QVBoxLayout, QTableWidget, QTreeWidget, QTreeWidgetItem, QHBoxLayout
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime
from utils.utilsVentas import calcular_total_general, borrar_fila, toggle_subtabla

#FUNCION GUARDAR VENTA EN LA BASE DE DATOS


def guardar_venta_en_db(ui_nueva_venta,ui,Form):
    # Conexión a la base de datos
    conexion_db = conexion()
    cursor = conexion_db.cursor()

    try:
        # 🔹1. Insertar la venta general en la tabla 'ventas'
        id_cliente = ui_nueva_venta.comboBox.currentData()
        fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        total = 0
        cantidad_total = 0

        # Primero calculamos el total de la venta sumando los subtotales de cada fila
        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)
            medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()
            subtotal = float(item_subtotal.text()) if item_subtotal else 0
            total += subtotal

            cantidad_spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            if cantidad_spin:
                cantidad_total += cantidad_spin.value()
               # Insertamos la venta en la tabla 'ventas' y obtenemos su ID generado
        cursor.execute("""
            INSERT INTO ventas (id_cliente, cantidad, total_venta, fecha_venta, medio_pago)
            VALUES (%s, %s, %s,%s,%s)
            RETURNING id_venta;
        """, (id_cliente, cantidad_total, total, fecha, medio_pago ))

        id_venta = cursor.fetchone()[0]

        # 🔹2. Insertar cada producto vendido en 'detalle_venta'
        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
            cantidad_spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            item_precio_unitario = ui_nueva_venta.tableWidget.item(row, 2)
            item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)

            # Validación por si faltara algún campo
            if combo and cantidad_spin and item_precio_unitario and item_subtotal:
                id_producto = combo.currentData()
                cantidad = cantidad_spin.value()
                precio_unitario = float(item_precio_unitario.text())
                subtotal = float(item_subtotal.text())

                cursor.execute("""
                    INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s);
                """, (id_venta, id_producto, cantidad, precio_unitario, subtotal))

        # 🔹3. Confirmar la transacción
        conexion_db.commit()
        print("Venta guardada exitosamente.")

    except Exception as e:
        conexion_db.rollback()
        print(f"Error al guardar la venta: {e}")

    finally:
        ui.treeWidget.clear()
        cargar_ventas(ui, Form)
        ui.formulario_nueva_venta.close()
        cursor.close()
        conexion_db.close()
        
        
        
             
        
#FUNCION PARA AGREGAR FILAS AL FORMULARIO
       

def agregar_filas(ui_nueva_venta):
     row_position = ui_nueva_venta.tableWidget.rowCount()
     ui_nueva_venta.tableWidget.insertRow(row_position)
     
     combo = QComboBox()
     combo.addItem("Seleccione")
     
     spin = QSpinBox()
     spin.setMinimum(1)
     spin.setMaximum(999)
     conexion_db = conexion()
     cursor = conexion_db.cursor()
     cursor.execute("SELECT id_producto, nombre, precio_venta FROM productos;")
     producto = cursor.fetchall()
     
     ui_nueva_venta.precios = {}
     
     for idp, nombrep, preciop in producto:
         combo.addItem(nombrep,idp )
         ui_nueva_venta.precios[nombrep] = preciop
         if idp == producto:
             combo.setCurrentIndex(
                 combo.count() - 1
             )
             
     ui_nueva_venta.tableWidget.setCellWidget(row_position, 0, combo)
     ui_nueva_venta.tableWidget.setCellWidget(row_position, 1, spin)   
     item_precio_unitario = QTableWidgetItem("0")
     item_precio_unitario.setFlags(item_precio_unitario.flags() ^ Qt.ItemIsEditable)  # desactivar edición manual
     ui_nueva_venta.tableWidget.setItem(row_position, 2, item_precio_unitario)
     item_subtotal = QTableWidgetItem("0")
     item_subtotal.setFlags(item_subtotal.flags() ^ Qt.ItemIsEditable)  # desactivar edición manual
     ui_nueva_venta.tableWidget.setItem(row_position, 3, item_subtotal)
     
     
     combo.currentIndexChanged.connect(lambda: actualizar_subtotal(row_position,ui_nueva_venta))
     spin.valueChanged.connect(lambda:  actualizar_subtotal(row_position,ui_nueva_venta))  
     combo.currentIndexChanged.connect(lambda: calcular_total_general(ui_nueva_venta))
     spin.valueChanged.connect(lambda: calcular_total_general(ui_nueva_venta))  
   
   
       
       
        
        

#FUNCION PARA EL BOTON AGREGAR MAS FILAS
def agrega_prodcuto_a_fila(ui_nueva_venta):
    row_position = ui_nueva_venta.tableWidget.rowCount()
    ui_nueva_venta.tableWidget.insertRow(row_position)
    
    combo = QComboBox()
    
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    cursor.execute("SELECT id_producto, nombre, precio_venta FROM productos;")
    producto = cursor.fetchall()
    
    ui_nueva_venta.precios = {}
    
    for idp, nombrep, preciop in producto:
        combo.addItem(nombrep,idp )
        ui_nueva_venta.precios[nombrep] = preciop
        combo.setCurrentIndex(
            combo.count() - 1
        )        
    
    ui_nueva_venta.tableWidget.setCellWidget(row_position, 0, combo)
    # Crear un QSpinBox de cantidad en la columna 1
    spin = QSpinBox()
    spin.setMinimum(1)
    spin.setMaximum(999)
    ui_nueva_venta.tableWidget.setCellWidget(row_position, 1, spin)
    # Crear un precio unitario en la columna 2
    precio_unitario_valor = ui_nueva_venta.precios.get(combo.currentText(), 0)
    item_precio_unitario = QTableWidgetItem(str(precio_unitario_valor))
    item_precio_unitario.setFlags(item_precio_unitario.flags() ^ Qt.ItemIsEditable)  # desactiva edición
    ui_nueva_venta.tableWidget.setItem(row_position, 2, item_precio_unitario)
    # Crear un subtotal en la columna 3
    subtotal = QTableWidgetItem("0")
    ui_nueva_venta.tableWidget.setItem(row_position, 3, subtotal)
    
    combo.currentIndexChanged.connect(lambda: actualizar_subtotal(row_position,ui_nueva_venta))
    spin.valueChanged.connect(lambda: actualizar_subtotal(row_position,ui_nueva_venta))    
    combo.currentIndexChanged.connect(lambda: calcular_total_general(ui_nueva_venta))
    spin.valueChanged.connect(lambda: calcular_total_general(ui_nueva_venta))
    
    


#CARGAR DATOS EN EL FORMULARIO PRINCIPAL
def cargar_ventas(ui, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    
    cursor.execute("""
                   SELECT v.id_venta, v.fecha_venta, c.nombre, v.cantidad, v.total_venta, v.medio_pago FROM ventas v
                   JOIN clientes c ON v.id_cliente = c.id
                   ORDER BY v.fecha_venta DESC;
                   """)
    ventas = cursor.fetchall()
    
    for venta in ventas:
        id_venta, fecha, id_cliente, cantidad, total, medio = venta
        
        item_venta = QTreeWidgetItem()
        item_venta.setText(0, str(id_venta))
        item_venta.setText(1, fecha.strftime("%Y-%m-%d %H:%M:%S"))
        item_venta.setText(2, str(id_cliente))
        item_venta.setText(3, str(cantidad))
        item_venta.setText(4, str(total))
        item_venta.setText(5, medio)
        
        ui.treeWidget.addTopLevelItem(item_venta)  
        
        
        header_hijo = QTreeWidgetItem()
        header_hijo.setText(1, "Producto")
        header_hijo.setText(2, "Cantidad")
        header_hijo.setText(3, "Precio Unitario")
        header_hijo.setText(4, "Subtotal")
        
        item_venta.addChild(header_hijo)
        
        # Cambiar color de fondo a gris claro
        for col in range(1, 5):
            header_hijo.setBackground(col, QBrush(QColor("#dcdcdc")))  # gris claro
            header_hijo.setForeground(col, QBrush(QColor("#2c3e50")))  # texto oscuro

        # Poner en negrita
        font = QFont()
        font.setBold(True)
        for col in range(1, 5):
            header_hijo.setFont(col, font)

        cursor.execute("""
                       SELECT vd.id_venta, p.nombre, vd.cantidad, vd.precio_unitario, vd.subtotal FROM ventas_detalle vd
                       JOIN productos p ON vd.id_producto = p.id_producto
                       WHERE id_venta = %s""", (id_venta,))   
        detalles =  cursor.fetchall()  
        
        
        for detalle in detalles:
            id_venta, producto, cantidad, precio, subtotal = detalle 
            
            item_subVenta = QTreeWidgetItem()
            item_subVenta.setText(0, str(id_venta))
            item_subVenta.setText(1, str(producto))
            item_subVenta.setText(2, str(cantidad))
            item_subVenta.setText(3, str(precio))
            item_subVenta.setText(4, str(subtotal))
            
        
            
            item_venta.addChild(item_subVenta)
            agregar_botones_opciones(ui.treeWidget, item_venta, ui, Form)
        
            


            
            
    conexion_db.close()
    cursor.close()
    
    
#FUNCION ELIMIINAR VENTA

def eliminar_venta(treeWidget, item_venta):
    if item_venta:
        id_venta = item_venta.text(0)

        # Confirmación básica
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(None, 'Eliminar venta',
                                     f"¿Estás seguro de eliminar la venta con ID {id_venta}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            try:
                # Elimina primero los detalles para evitar error de clave foránea
                cursor.execute("DELETE FROM ventas_detalle WHERE id_venta = %s", (id_venta,))
                cursor.execute("DELETE FROM ventas WHERE id_venta = %s", (id_venta,))
                conexion_db.commit()

                # Eliminar de la vista
                treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(item_venta))
                print(f"Venta {id_venta} eliminada correctamente.")
            except Exception as e:
                conexion_db.rollback()
                print(f"Error al eliminar: {e}")
            finally:
                cursor.close()
                conexion_db.close()
                
                

          
def editar_venta(item_venta, ui, Form):


    if not item_venta:
        print("No se seleccionó ninguna venta.")
        return

    id_venta = item_venta.text(0)
    print("ID de la venta seleccionada:", id_venta)
    ui.formulario_id_venta = id_venta

    # Abrir el formulario de venta si no está visible
    if not hasattr(ui, 'formulario_nueva_venta') or not ui.formulario_nueva_venta.isVisible():
        ui.abrir_formulario_nueva_venta(Form, edicion=True)

    ui_nueva_venta = ui.ui_nueva_venta

    conexion_db = conexion()
    cursor = conexion_db.cursor()

    # Obtener datos generales de la venta
    cursor.execute("""
        SELECT id_cliente, fecha_venta, total_venta, medio_pago
        FROM ventas
        WHERE id_venta = %s
    """, (id_venta,))
    venta = cursor.fetchone()

    if not venta:
        print("No se encontró la venta.")
        return

    id_cliente, fecha, total, medio_pago = venta

    # Cargar combo de clientes
    cursor.execute("SELECT id, nombre FROM clientes")
    clientes = cursor.fetchall()

    ui_nueva_venta.comboBox.clear()
    index_cliente = 0
    for i, (idc, nombre) in enumerate(clientes):
        ui_nueva_venta.comboBox.addItem(nombre, idc)
        if idc == id_cliente:
            index_cliente = i
    ui_nueva_venta.comboBox.setCurrentIndex(index_cliente)

    # Fecha
    fecha_qt = QDateTime.fromSecsSinceEpoch(int(fecha.timestamp()))
    ui_nueva_venta.dateTimeEditCliente.setDateTime(fecha_qt)

    # Medio de pago
    index_medio = ui_nueva_venta.comboBoxMedioPago.findText(medio_pago)
    if index_medio >= 0:
        ui_nueva_venta.comboBoxMedioPago.setCurrentIndex(index_medio)

    # Limpiar tabla
    ui_nueva_venta.tableWidget.setRowCount(0)

    # Obtener productos disponibles
    cursor.execute("SELECT id_producto, nombre FROM productos")
    productos = cursor.fetchall()

    # Obtener detalles de la venta
    cursor.execute("""
        SELECT id_producto, cantidad, precio_unitario, subtotal
        FROM ventas_detalle
        WHERE id_venta = %s
    """, (id_venta,))
    detalles = cursor.fetchall()

    for i, (id_producto, cantidad, precio_unitario, subtotal) in enumerate(detalles):
        ui_nueva_venta.tableWidget.insertRow(i)

        combo = QComboBox()
        index_producto = 0
        for j, (idp, nombre) in enumerate(productos):
            combo.addItem(nombre, idp)
            if idp == id_producto:
                index_producto = j
        combo.setCurrentIndex(index_producto)

        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setValue(cantidad)

        ui_nueva_venta.tableWidget.setCellWidget(i, 0, combo)
        ui_nueva_venta.tableWidget.setCellWidget(i, 1, spin)

        # Celdas vacías, se rellenan por actualizar_subtotal
        ui_nueva_venta.tableWidget.setItem(i, 2, QTableWidgetItem(""))  # Precio unitario
        ui_nueva_venta.tableWidget.setItem(i, 3, QTableWidgetItem(""))  # Subtotal

        # Conectar cambios
        try:
            ui_nueva_venta.pushButtonAceptar.clicked.disconnect()
        except Exception:
            pass  # Si no estaba conectado, no importa
        
        ui_nueva_venta.pushButtonAceptar.clicked.connect(
            lambda: actualizar_venta_en_db(ui_nueva_venta, ui.formulario_id_venta, ui, Form)
        )
        combo.currentIndexChanged.connect(lambda _, row=i: actualizar_subtotal(row, ui_nueva_venta))
        spin.valueChanged.connect(lambda _, row=i: actualizar_subtotal(row, ui_nueva_venta))

        # Llamar una vez para que se actualice en pantalla al cargar
        actualizar_subtotal(i, ui_nueva_venta)

    calcular_total_general(ui_nueva_venta)
    ui_nueva_venta.pushButtonAceptar.clicked.connect(lambda: actualizar_venta_en_db(ui_nueva_venta, id_venta, ui, Form))

    cursor.close()
    conexion_db.close()
    
    
    
    
    
    
    

def cargar_detalles_venta(id_venta, ui):
    conexion_db = conexion()
    cursor = conexion_db.cursor()

    # Traemos los detalles de la venta
    cursor.execute("""
        SELECT id_producto, cantidad, precio_unitario, subtotal
        FROM ventas_detalle
        WHERE id_venta = %s
    """, (id_venta,))
    detalles = cursor.fetchall()

    # Traemos todos los productos
    cursor.execute("SELECT id_producto, nombre FROM productos")
    productos = cursor.fetchall()

    cursor.close()
    conexion_db.close()

    # Limpiamos la tabla
    ui.tableWidget.setRowCount(0)

    for id_producto, cantidad, precio_unitario, subtotal in detalles:
        row_position = ui.tableWidget.rowCount()
        ui.tableWidget.insertRow(row_position)

        # ComboBox de productos
        combo_producto = QComboBox()
        index_producto = 0
        for i, (pid, nombre) in enumerate(productos):
            combo_producto.addItem(nombre, pid)
            if pid == id_producto:
                index_producto = i
        combo_producto.setCurrentIndex(index_producto)

        # SpinBox de cantidad
        spin_cantidad = QSpinBox()
        spin_cantidad.setValue(cantidad)
        spin_cantidad.setMinimum(1)

        # Insertar widgets en las celdas
        ui.tableWidget.setCellWidget(row_position, 0, combo_producto)  # columna producto
        ui.tableWidget.setCellWidget(row_position, 1, spin_cantidad)   # columna cantidad

        # Precio unitario y subtotal como texto
        item_precio = QTableWidgetItem(f"{precio_unitario:.0f}")
        item_subtotal = QTableWidgetItem(f"{subtotal:.0f}")
        ui.tableWidget.setItem(row_position, 2, item_precio)  # columna precio
        ui.tableWidget.setItem(row_position, 3, item_subtotal)  # columna subtotal

    # Recalcular el total general si es necesario
    from utils.utilsVentas import calcular_total_general
    calcular_total_general(ui)





#FUNCION DE ACTUALIZAR PRODUCTOS
def actualizar_subtotal(row, ui):
    try:
        combo = ui.tableWidget.cellWidget(row, 0)  # Producto
        spin = ui.tableWidget.cellWidget(row, 1)   # Cantidad

        if combo is None or spin is None:
            print(f"[Fila {row}] Combo o Spin no existen todavía.")
            return

        id_producto = combo.currentData()
        cantidad = spin.value()

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








def agregar_botones_opciones(treeWidget, item_venta, ui, Form):
    
    # Crear un widget contenedor
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)  # sin margen interno
    
    # Crear botones
    btn_editar = QPushButton("Editar")
    btn_editar.setObjectName("btnEditar")

    btn_eliminar = QPushButton("Eliminar")
    btn_eliminar.setObjectName("btnEliminar")
    
    # Opcional: cambiar tamaño o estilo
    btn_editar.setFixedHeight(25)
    btn_eliminar.setFixedHeight(25)
    
    # Agregar al layout
    layout.addWidget(btn_editar)
    layout.addWidget(btn_eliminar)
    
    # Asignar layout al widget
    widget.setLayout(layout)
    
    # Insertar el widget en la columna correspondiente
    treeWidget.setItemWidget(item_venta, 7, widget)
    
    # 🔗 Conectar señales de los botones
    btn_editar.clicked.connect(lambda: editar_venta(item_venta, ui, Form))
    btn_eliminar.clicked.connect(lambda: eliminar_venta(ui.treeWidget, item_venta))
    
    






def actualizar_venta_en_db(ui_nueva_venta, id_venta, ui, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()
    try:
        # 🔴 1. Eliminar los detalles viejos antes de insertar los nuevos
        cursor.execute("DELETE FROM ventas_detalle WHERE id_venta = %s", (id_venta,))
        
        cantidad_total = 0  # 🔢 Inicializar cantidad total de productos

        # 🔴 2. Insertar los nuevos detalles desde la tabla del formulario
        for row in range(ui_nueva_venta.tableWidget.rowCount()):
            combo = ui_nueva_venta.tableWidget.cellWidget(row, 0)
            spin = ui_nueva_venta.tableWidget.cellWidget(row, 1)
            id_producto = combo.currentData()
            cantidad = spin.value()
            cantidad_total += cantidad  # Sumar a la cantidad total

            precio_unitario = float(ui_nueva_venta.tableWidget.item(row, 2).text())
            subtotal = float(ui_nueva_venta.tableWidget.item(row, 3).text())

            cursor.execute("""
                INSERT INTO ventas_detalle (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_venta, id_producto, cantidad, precio_unitario, subtotal))

        # 🔴 3. Obtener datos generales del formulario
        id_cliente = ui_nueva_venta.comboBox.currentData()
        fecha = ui_nueva_venta.dateTimeEditCliente.dateTime().toPython()
        medio_pago = ui_nueva_venta.comboBoxMedioPago.currentText()
        total_venta = calcular_total_general(ui_nueva_venta)  # Asegúrate de que retorne un valor numérico

        print(f"TOTAL VENTA CALCULADO: {total_venta}")
        print(f"CANTIDAD TOTAL CALCULADA: {cantidad_total}")

        # 🔴 4. Actualizar la venta en la tabla ventas
        cursor.execute("""
            UPDATE ventas
            SET id_cliente = %s, cantidad = %s, fecha_venta = %s, total_venta = %s, medio_pago = %s
            WHERE id_venta = %s
        """, (id_cliente, cantidad_total, fecha, total_venta, medio_pago, id_venta))

        # 🔴 5. Confirmar cambios
        conexion_db.commit()
        print(f"Venta {id_venta} actualizada correctamente.")

        # 🔴 6. Refrescar la tabla principal de ventas
        ui.treeWidget.clear()
        cargar_ventas(ui, Form)

        # 🔴 7. Cerrar el formulario de edición
        ui.formulario_nueva_venta.close()

    except Exception as e:
        conexion_db.rollback()
        print(f"Error al actualizar la venta: {e}")
    finally:
        cursor.close()
        conexion_db.close()
        
        
        
        
        
        
        
def buscar_ventas(ui, criterio, Form):
    conexion_db = conexion()
    cursor = conexion_db.cursor()

    # Si el criterio es vacío, mostrar todas ordenadas por fecha descendente
    if not criterio:
        cursor.execute("""
        SELECT v.id_venta, c.nombre, v.fecha_venta, v.total_venta, v.medio_pago, v.cantidad
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id
            ORDER BY v.fecha_venta DESC
        """)
    else:
        # Búsqueda flexible usando ILIKE para insensibilidad a mayúsculas
        consulta = """
        SELECT v.id_venta, c.nombre, v.fecha_venta, v.total_venta, v.medio_pago, v.cantidad
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id
            WHERE c.nombre ILIKE %s OR
                  v.medio_pago ILIKE %s OR
                  CAST(v.fecha_venta AS TEXT) ILIKE %s
            ORDER BY v.fecha_venta DESC
        """
        criterio_like = f"%{criterio}%"
        cursor.execute(consulta, (criterio_like, criterio_like, criterio_like))

    ventas = cursor.fetchall()

    # Limpiar tabla antes de cargar resultados
    ui.treeWidget.clear()

    # Insertar resultados en la tabla principal
    for id_venta, cliente, fecha, total, medio_pago, cantidad in ventas:
        item = QTreeWidgetItem([
            str(id_venta),
            fecha.strftime("%d/%m/%Y"),
            cliente,
            str(cantidad),
            f"{total:.2f}",
            medio_pago
            
        ])
        ui.treeWidget.addTopLevelItem(item)
        
        agregar_botones_opciones(ui.treeWidget,item, ui, Form)

        conexion_detalle = conexion()
        cursor_detalle = conexion_detalle.cursor()

        cursor_detalle.execute("""
            SELECT p.nombre, vd.cantidad, vd.precio_unitario, vd.subtotal
            FROM ventas_detalle vd
            JOIN productos p ON p.id_producto = vd.id_producto
            WHERE vd.id_venta = %s
        """, (id_venta,))

        detalles = cursor_detalle.fetchall()

        for nombre_producto, cantidad, precio_unitario, subtotal in detalles:
            item_detalle = QTreeWidgetItem([
                "",  # si querés dejar la celda de ID de venta vacía en el detalle
                nombre_producto,
                str(cantidad),
                f"{precio_unitario:.2f}",
                f"{subtotal:.2f}"
            ])
            item.addChild(item_detalle)

        cursor_detalle.close()
        conexion_detalle.close()

    cursor.close()
    conexion_db.close()