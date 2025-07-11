# -*- coding: utf-8 -*-
# Módulo: Clientes
# Objetivo: Registrar información de clientes frecuentes o que solicitan facturas

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon, QImage, QKeySequence,
    QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QTableView, QVBoxLayout, QWidget,
    QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

class Ui_ClientesForm(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"ClientesForm")
        Form.resize(1000, 600)
        
        # Layout principal
        self.verticalLayout = QVBoxLayout(Form)
        
        # Frame de búsqueda
        self.searchFrame = QFrame()
        self.searchLayout = QHBoxLayout(self.searchFrame)
        
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Buscar por nombre, RUC/CI o teléfono...")
        self.searchButton = QPushButton("Buscar")
        self.clearSearchButton = QPushButton("Limpiar")
        
        self.searchLayout.addWidget(self.searchInput)
        self.searchLayout.addWidget(self.searchButton)
        self.searchLayout.addWidget(self.clearSearchButton)
        
        # Frame de botones
        self.buttonsFrame = QFrame()
        self.buttonsLayout = QHBoxLayout(self.buttonsFrame)
        
        self.addButton = QPushButton("Agregar Cliente")
        self.editButton = QPushButton("Editar")
        self.deleteButton = QPushButton("Eliminar")
        
        self.buttonsLayout.addWidget(self.addButton)
        self.buttonsLayout.addWidget(self.editButton)
        self.buttonsLayout.addWidget(self.deleteButton)
        
        # Tabla de clientes
        self.clientesTable = QTableView()
        self.clientesTable.setSelectionBehavior(QTableView.SelectRows)
        self.clientesTable.setSelectionMode(QTableView.SingleSelection)
        
        # Agregar elementos al layout principal
        self.verticalLayout.addWidget(self.searchFrame)
        self.verticalLayout.addWidget(self.buttonsFrame)
        self.verticalLayout.addWidget(self.clientesTable)

class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_id=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar/Editar Cliente")
        self.cliente_id = cliente_id
        
        layout = QFormLayout(self)
        
        # Campos del formulario
        self.nombreInput = QLineEdit()
        self.rucInput = QLineEdit()
        self.telefonoInput = QLineEdit()
        self.emailInput = QLineEdit()
        
        # Configurar placeholders
        self.nombreInput.setPlaceholderText("Nombre o Razón Social")
        self.rucInput.setPlaceholderText("RUC o Cédula")
        self.telefonoInput.setPlaceholderText("Número de teléfono")
        self.emailInput.setPlaceholderText("Correo electrónico")
        
        # Agregar campos al formulario
        layout.addRow("Nombre/Razón Social:", self.nombreInput)
        layout.addRow("RUC/CI:", self.rucInput)
        layout.addRow("Teléfono:", self.telefonoInput)
        layout.addRow("Email:", self.emailInput)
        
        # Botones
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        layout.addRow(self.buttons)
        
        self.buttons.accepted.connect(self.validate)
        self.buttons.rejected.connect(self.reject)
        
        # Si es edición, cargar datos
        if cliente_id:
            self.load_cliente_data()
    
    def load_cliente_data(self):
        query = QSqlQuery()
        query.prepare("SELECT nombre, ruc, telefono, email FROM clientes WHERE id = ?")
        query.addBindValue(self.cliente_id)
        
        if query.exec() and query.next():
            self.nombreInput.setText(query.value(0))
            self.rucInput.setText(query.value(1))
            self.telefonoInput.setText(query.value(2))
            self.emailInput.setText(query.value(3))
    
    def validate(self):
        nombre = self.nombreInput.text().strip()
        ruc = self.rucInput.text().strip()
        telefono = self.telefonoInput.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre/razón social es obligatorio")
            return
        
        if not ruc:
            QMessageBox.warning(self, "Error", "El RUC/CI es obligatorio")
            return
        
        if not telefono:
            QMessageBox.warning(self, "Error", "El teléfono es obligatorio")
            return
        
        # Verificar RUC/CI único (excepto para el cliente actual en edición)
        query = QSqlQuery()
        query.prepare("SELECT id FROM clientes WHERE ruc = ?")
        query.addBindValue(ruc)
        
        if query.exec() and query.next():
            existing_id = query.value(0)
            if not self.cliente_id or existing_id != self.cliente_id:
                QMessageBox.warning(self, "Error", "Ya existe un cliente con este RUC/CI")
                return
        
        self.accept()
    
    def get_data(self):
        return {
            "nombre": self.nombreInput.text().strip(),
            "ruc": self.rucInput.text().strip(),
            "telefono": self.telefonoInput.text().strip(),
            "email": self.emailInput.text().strip()
        }

class ClientesModule(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ClientesForm()
        self.ui.setupUi(self)
        
        # Configurar ventana
        self.setWindowTitle("Gestión de Clientes")
        
        # Inicializar base de datos
        self.init_db()
        
        # Configurar modelo de tabla
        self.model = QSqlTableModel(self)
        self.model.setTable("clientes")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        
        # Configurar tabla
        self.ui.clientesTable.setModel(self.model)
        self.ui.clientesTable.hideColumn(0)  # Ocultar columna ID
        self.ui.clientesTable.resizeColumnsToContents()
        
        # Conectar señales
        self.ui.addButton.clicked.connect(self.add_cliente)
        self.ui.editButton.clicked.connect(self.edit_cliente)
        self.ui.deleteButton.clicked.connect(self.delete_cliente)
        self.ui.searchButton.clicked.connect(self.search_clientes)
        self.ui.clearSearchButton.clicked.connect(self.clear_search)
    
    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("clientes.db")
        
        if not self.db.open():
            QMessageBox.critical(self, "Error", "No se pudo abrir la base de datos")
            return False
        
        # Crear tabla si no existe
        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ruc TEXT NOT NULL UNIQUE,
                telefono TEXT NOT NULL,
                email TEXT
            )
        """)
        
        return True
    
    def add_cliente(self):
        dialog = ClienteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            query = QSqlQuery()
            query.prepare("""
                INSERT INTO clientes (nombre, ruc, telefono, email)
                VALUES (?, ?, ?, ?)
            """)
            query.addBindValue(data["nombre"])
            query.addBindValue(data["ruc"])
            query.addBindValue(data["telefono"])
            query.addBindValue(data["email"])
            
            if query.exec():
                self.model.select()
                QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")
            else:
                QMessageBox.critical(self, "Error", "No se pudo agregar el cliente")
    
    def edit_cliente(self):
        selected = self.ui.clientesTable.currentIndex()
        if not selected.isValid():
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente para editar")
            return
        
        row = selected.row()
        cliente_id = self.model.record(row).value("id")
        
        dialog = ClienteDialog(self, cliente_id)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            query = QSqlQuery()
            query.prepare("""
                UPDATE clientes 
                SET nombre = ?, ruc = ?, telefono = ?, email = ?
                WHERE id = ?
            """)
            query.addBindValue(data["nombre"])
            query.addBindValue(data["ruc"])
            query.addBindValue(data["telefono"])
            query.addBindValue(data["email"])
            query.addBindValue(cliente_id)
            
            if query.exec():
                self.model.select()
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el cliente")
    
    def delete_cliente(self):
        selected = self.ui.clientesTable.currentIndex()
        if not selected.isValid():
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente para eliminar")
            return
        
        row = selected.row()
        cliente_id = self.model.record(row).value("id")
        nombre = self.model.record(row).value("nombre")
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Está seguro que desea eliminar al cliente {nombre}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM clientes WHERE id = ?")
            query.addBindValue(cliente_id)
            
            if query.exec():
                self.model.select()
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el cliente")
    
    def search_clientes(self):
        search_text = self.ui.searchInput.text().strip()
        if not search_text:
            self.model.setFilter("")
            self.model.select()
            return
        
        filter_str = (
            f"nombre LIKE '%{search_text}%' OR "
            f"ruc LIKE '%{search_text}%' OR "
            f"telefono LIKE '%{search_text}%'"
        )
        self.model.setFilter(filter_str)
        self.model.select()
    
    def clear_search(self):
        self.ui.searchInput.clear()
        self.model.setFilter("")
        self.model.select()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Establecer estilo visual
    app.setStyle("Fusion")
    
    # Crear y mostrar ventana
    window = ClientesModule()
    window.show()
    
    sys.exit(app.exec())