

def calcular_total_general(ui_nueva_venta):
    total = 0
    filas = ui_nueva_venta.tableWidget.rowCount()
    for row in range(filas):
        item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)
        if item_subtotal:
            try:
                subtotal = float(item_subtotal.text())
            except ValueError:
                subtotal = 0
            total += subtotal
    ui_nueva_venta.lineEditPrecioTotal.setText(str(total))
    
    return total 
    
    
#FUNCION BORRAR FILA DE PRODUCTO A VENDER

def borrar_fila(ui_nueva_venta):
    row_position = ui_nueva_venta.tableWidget.rowCount()
    if row_position > 0:
        ui_nueva_venta.tableWidget.removeRow(row_position - 1)
        
        
def toggle_subtabla(item_venta):
    if item_venta.isExpanded():
        item_venta.setExpanded(False)
    else:
        # Si está colapsado, lo expande
        item_venta.setExpanded(True)




