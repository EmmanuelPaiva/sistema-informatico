from utils.normNumbers import formatear_numero


def calcular_total_general(ui_nueva_venta):
    total = 0.0
    rows = ui_nueva_venta.tableWidget.rowCount()

    for row in range(rows):
        item_sub = ui_nueva_venta.tableWidget.item(row, 3)
        if not item_sub:
            continue

        texto = item_sub.text().strip()
        if not texto:
            continue

        try:
            # desformatear número
            valor = texto.replace(".", "").replace(",", ".")
            total += float(valor)
        except ValueError:
            pass

    ui_nueva_venta.lineEditPrecioTotal.setText(formatear_numero(total))
    return total



def borrar_fila(ui_nueva_venta):
    rows = ui_nueva_venta.tableWidget.rowCount()
    if rows > 0:
        ui_nueva_venta.tableWidget.removeRow(rows - 1)
        calcular_total_general(ui_nueva_venta)



def toggle_subtabla(item_venta):
    item_venta.setExpanded(not item_venta.isExpanded())
