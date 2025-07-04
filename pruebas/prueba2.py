from PySide6.QtWidgets import QTableView, QMainWindow
from PySide6.QtGui import QStandardItemModel, QStandardItem

model = QStandardItemModel()
model.setHorizontalHeaderLabels(["ID", "Nombre", "Rol"])

datos = [
    (1, "Juan", "admin"),
    (2, "Ana", "empleado")
]

for fila in datos:
    items = [QStandardItem(str(col)) for col in fila]
    model.appendRow(items)

self.ui.tableView.setModel(model)