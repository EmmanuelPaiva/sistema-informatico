import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QGridLayout, QFrame, QPushButton, QMessageBox
)
from db.conexion import conexion
from forms.formulario_nueva_obra import FormularioNuevaObra

class ObrasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animacion_actual = None
        self.id_obra_en_edicion = None

        self.layout_principal = QVBoxLayout(self)

        self.encabezado = QWidget()
        encabezado_layout = QHBoxLayout(self.encabezado)
        self.label_titulo = QLabel("Obras")
        self.label_titulo.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2f3640;")
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar obra...")
        self.buscador.setStyleSheet("padding: 6px; border-radius: 6px; border: 1px solid #ccc;")
        encabezado_layout.addWidget(self.label_titulo)
        encabezado_layout.addStretch()
        encabezado_layout.addWidget(self.buscador)
        self.layout_principal.addWidget(self.encabezado)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout_principal.addWidget(self.scroll_area)

        self.formulario_nueva_obra = FormularioNuevaObra(self)
        self.formulario_nueva_obra.setMaximumHeight(0)
        self.formulario_nueva_obra.setVisible(False)
        self.layout_principal.addWidget(self.formulario_nueva_obra)

        self.formulario_nueva_obra.btn_cancelar.clicked.connect(self.ocultar_formulario_con_animacion)
        self.formulario_nueva_obra.btn_aceptar.clicked.connect(self.procesar_formulario_obra)

        self.setStyleSheet("background-color: #f5f6fa;")
        QTimer.singleShot(0, self._reflow)
        self.cargar_obras()
        self.setStyleSheet(self.estilos())

    def procesar_formulario_obra(self):
        datos = self.formulario_nueva_obra.obtener_datos()
        if not datos:
            QMessageBox.warning(self, "Datos inválidos", "Por favor completá todos los campos obligatorios.")
            return

        try:
            if self.id_obra_en_edicion is not None:
                self.actualizar_obra_en_bd(self.id_obra_en_edicion, datos)
            else:
                self.insertar_obra_en_bd(datos)

            self.formulario_nueva_obra.limpiar_campos()
            self.ocultar_formulario_con_animacion()
            self.refrescar_cards()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la obra: {e}")

    def insertar_obra_en_bd(self, datos):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("""
            INSERT INTO obras (nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_obra
        """, (
            datos['nombre'], datos['direccion'], datos['fecha_inicio'], datos['fecha_fin'],
            datos['estado'], datos['metros_cuadrados'], datos['presupuesto_total'], datos['descripcion']
        ))
        conexion_db.commit()
        cursor.close()
        conexion_db.close()

    def actualizar_obra_en_bd(self, id_obra, datos):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("""
            UPDATE obras SET nombre=%s, direccion=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s,
            metros_cuadrados=%s, presupuesto_total=%s, descripcion=%s WHERE id_obra=%s
        """, (
            datos['nombre'], datos['direccion'], datos['fecha_inicio'], datos['fecha_fin'],
            datos['estado'], datos['metros_cuadrados'], datos['presupuesto_total'], datos['descripcion'], id_obra
        ))
        conexion_db.commit()
        cursor.close()
        conexion_db.close()
        self.id_obra_en_edicion = None

    def eliminar_obra_de_bd(self, id_obra):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("DELETE FROM obras WHERE id_obra = %s", (id_obra,))
        conexion_db.commit()
        cursor.close()
        conexion_db.close()

    def cargar_obras(self):
        try:
            conexion_db = conexion()
            cursor = conexion_db.cursor()
            cursor.execute("SELECT id_obra, nombre, estado, presupuesto_total, fecha_inicio FROM obras ORDER BY id_obra DESC")
            obras = cursor.fetchall()
            for obra in obras:
                self.agregar_card_obra({
                    "id_obra": obra[0],
                    "nombre": obra[1],
                    "estado": obra[2],
                    "presupuesto_total": obra[3],
                    "fecha_inicio": obra[4]
                })
            cursor.close()
            conexion_db.close()
        except Exception as e:
            print("Error cargando obras:", e)
        finally:
            self.agregar_card_nueva_obra()

    def refrescar_cards(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cargar_obras()

    def agregar_card_obra(self, obra):
        frame = QFrame()
        frame.setMaximumSize(300, 250)
        layout = QVBoxLayout(frame)

        layout.addWidget(QLabel(f"{obra['nombre']}"))
        layout.addWidget(QLabel(f"Estado: {obra['estado']}"))
        layout.addWidget(QLabel(f"Presupuesto: {obra['presupuesto_total']} Gs."))
        layout.addWidget(QLabel(f"Inicio: {obra['fecha_inicio']}"))

        botones = QHBoxLayout()
        btn_ver = QPushButton("Ver Detalles")
        btn_editar = QPushButton("✎")
        btn_eliminar = QPushButton("🗑")

        btn_editar.clicked.connect(lambda: self.editar_obra(obra['id_obra']))
        btn_eliminar.clicked.connect(lambda: self.eliminar_obra(obra['id_obra']))

        botones.addWidget(btn_ver)
        botones.addWidget(btn_editar)
        botones.addWidget(btn_eliminar)
        layout.addLayout(botones)

        self.grid_layout.addWidget(frame)
        self._reflow()

    def editar_obra(self, id_obra):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion FROM obras WHERE id_obra=%s", (id_obra,))
        datos = cursor.fetchone()
        cursor.close()
        conexion_db.close()

        if datos:
            self.id_obra_en_edicion = id_obra
            self.formulario_nueva_obra.input_nombre.setText(datos[0])
            self.formulario_nueva_obra.input_direccion.setText(datos[1])
            self.formulario_nueva_obra.input_fecha_inicio.setDate(datos[2])
            self.formulario_nueva_obra.input_fecha_fin.setDate(datos[3])
            self.formulario_nueva_obra.input_estado.setCurrentText(datos[4])
            self.formulario_nueva_obra.input_metros.setValue(datos[5])
            self.formulario_nueva_obra.input_presupuesto.setValue(datos[6])
            self.formulario_nueva_obra.input_descripcion.setText(datos[7])
            self.mostrar_formulario_con_animacion()

    def eliminar_obra(self, id_obra):
        confirmacion = QMessageBox.question(self, "Eliminar obra", "¿Estás seguro de que querés eliminar esta obra?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            try:
                self.eliminar_obra_de_bd(id_obra)
                self.refrescar_cards()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la obra: {e}")

    def agregar_card_nueva_obra(self):
        frame = QFrame()
        frame.setMaximumSize(300, 250)
        layout = QVBoxLayout(frame)

        boton = QPushButton("+")
        boton.setFixedSize(80, 80)
        boton.setStyleSheet("""
            QPushButton {
                font-size: 40pt;
                border-radius: 40px;
                background-color: #0097e6;
                color: white;
            }
            QPushButton:hover {
                background-color: #00a8ff;
            }
        """)
        layout.addStretch()
        layout.addWidget(boton, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        boton.clicked.connect(self.mostrar_formulario_con_animacion)

        self.grid_layout.addWidget(frame)
        self._reflow()

    def mostrar_formulario_con_animacion(self):
        form = self.formulario_nueva_obra
        form.setVisible(True)
        anim = QPropertyAnimation(form, b'maximumHeight')
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(600)
        anim.start()
        self.animacion_actual = anim

    def ocultar_formulario_con_animacion(self):
        form = self.formulario_nueva_obra
        anim = QPropertyAnimation(form, b'maximumHeight')
        anim.setDuration(300)
        anim.setStartValue(form.height())
        anim.setEndValue(0)
        anim.finished.connect(lambda: form.setVisible(False))
        anim.start()
        self.animacion_actual = anim
        self.id_obra_en_edicion = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow()

    def _reflow(self):
        grid = self.grid_layout
        if grid is None:
            return

        viewport_w = self.scroll_area.viewport().width()
        hspacing = grid.horizontalSpacing() or 10
        card_w = 300
        columnas = max(1, (viewport_w + hspacing) // (card_w + hspacing))

        widgets = []
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                widgets.append(w)
                w.setParent(None)

        for idx, w in enumerate(widgets):
            row = idx // columnas
            col = idx % columnas
            grid.addWidget(w, row, col)

        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        grid.update()

    def estilos(self):
        return """
        QWidget {
            font-family: 'Segoe UI';
            font-size: 11pt;
            background-color: #f5f6fa;
        }

        QScrollArea {
            border: none;
        }

        QFrame {
            background-color: white;
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #dcdde1;
        }

        QFrame:hover {
            border: 1px solid #0097e6;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.15);
        }

        QLabel {
            color: #2f3640;
        }

        QPushButton {
            background-color: #0097e6;
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #00a8ff;
        }

        QLineEdit {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 4px;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ObrasWidget()
    window.show()
    sys.exit(app.exec())
