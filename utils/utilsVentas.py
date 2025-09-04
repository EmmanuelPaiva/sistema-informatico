def calcular_total_general(ui_nueva_venta):
    total = 0.0
    rows = ui_nueva_venta.tableWidget.rowCount()
    for row in range(rows):
        item_sub = ui_nueva_venta.tableWidget.item(row, 3)
        if item_sub:
            try:
                total += float(item_sub.text() or 0)
            except ValueError:
                pass
    ui_nueva_venta.lineEditPrecioTotal.setText(f"{total:.2f}")
    return total


def borrar_fila(ui_nueva_venta):
    rows = ui_nueva_venta.tableWidget.rowCount()
    if rows > 0:
        ui_nueva_venta.tableWidget.removeRow(rows - 1)


def toggle_subtabla(item_venta):
    item_venta.setExpanded(not item_venta.isExpanded())
