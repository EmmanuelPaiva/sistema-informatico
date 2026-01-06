from utils.normNumbers import formatear_numero

def borrar_fila(ui_nueva_venta):
    row_position = ui_nueva_venta.tableWidget.rowCount()
    if row_position > 0:
        ui_nueva_venta.tableWidget.removeRow(row_position - 1)


def calcular_total_general(ui_nueva_venta):
    total = 0.0
    filas = ui_nueva_venta.tableWidget.rowCount()

    for row in range(filas):
        item_subtotal = ui_nueva_venta.tableWidget.item(row, 3)
        if item_subtotal and item_subtotal.text():
            try:
                subtotal = float(
                    item_subtotal.text()
                    .replace(".", "")
                    .replace(",", ".")
                )
            except ValueError:
                subtotal = 0.0
            total += subtotal

    ui_nueva_venta.lineEditPrecioTotal.setText(formatear_numero(total))
    return total