import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from main.ventana_inicio_sesion_ui import Ui_MainWindow
from db.conexion import conexion

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.BotonIniciarSesion.clicked.connect(self.verificar_informacion)
        
    def verificar_informacion(self):
        usuario = self.ui.LineEditUsuario.text()
        contrasena = self.ui.lineEditContrasena.text()
        
        conexion_db = conexion()
        
        if not conexion_db:
            QMessageBox.critical(self, "Error de conexión", "No se pudo conectar a la base de datos.")
            return 
        cursor = conexion_db.cursor()
        query = "SELECT * FROM usuarios WHERE nombre = %s AND contrasena = %s"
        cursor.execute(query,(usuario, contrasena))
        resultado = cursor.fetchone()
        
        if resultado:
            QMessageBox.information(self, "Éxito", f"Bienvenido, {resultado[1]} ({resultado[4]})")
        else: 
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
        
        cursor.close()
        conexion_db.close()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
            
            