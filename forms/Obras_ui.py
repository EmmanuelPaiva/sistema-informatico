import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QGridLayout, QFrame, QPushButton, QMessageBox, QSizePolicy
)
from db.conexion import conexion
from forms.formulario_nueva_obra import FormularioNuevaObra
from forms.detalles_obra import DetallesObraWidget


class ObrasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animacion_actual = None
        self.id_obra_en_edicion = None
        self.cards = []  # [(frame, data_dict, es_nueva_obra)]
        self.layout_principal = QVBoxLayout(self)

        # === Encabezado ===
        self.encabezado = QWidget()
        encabezado_layout = QHBoxLayout(self.encabezado)
        self.label_titulo = QLabel("Obras")
        self.label_titulo.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2f3640;")
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar obra...")
        self.buscador.setStyleSheet("padding: 6px; border-radius: 6px; border: 1px solid #ccc;")
        self.buscador.textChanged.connect(self._filtrar_cards)  # buscador funcional
        encabezado_layout.addWidget(self.label_titulo)
        encabezado_layout.addStretch()
        encabezado_layout.addWidget(self.buscador)
        self.layout_principal.addWidget(self.encabezado)

        # === Listado (grid con scroll) ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setHorizontalSpacing(12)
        self.grid_layout.setVerticalSpacing(12)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout_principal.addWidget(self.scroll_area)

        # === Contenedor de detalles inline (oculto por defecto) ===
        self.detalles_container = QFrame()
        self.detalles_container.setVisible(False)
        self.detalles_container.setMaximumHeight(0)
        self.detalles_layout = QVBoxLayout(self.detalles_container)
        self.layout_principal.addWidget(self.detalles_container)

        # === Formulario nueva/editar obra (oculto por defecto) ===
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

    # ===================== CRUD =====================

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
        # Limpia estructuras previas
        self.cards.clear()
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
        # Limpia grid y vuelve a cargar de DB
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.cards.clear()
        self.cargar_obras()
        self._reflow()
        self._filtrar_cards()  # mantiene el filtro actual si hay texto

    # ===================== Navegación / Vistas =====================

    def _mostrar_detalles_inline(self, widget):
        """Muestra el contenedor de detalles y oculta el grid (con flechita para volver)."""
        # Limpia contenedor
        for i in reversed(range(self.detalles_layout.count())):
            item = self.detalles_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()

        # === Flechita volver arriba ===
        barra = QHBoxLayout()
        btn_volver = QPushButton("←")
        btn_volver.setFixedWidth(40)
        btn_volver.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                font-weight: bold;
                color: #2f3640;
                background: transparent;
                border: none;
            }
            QPushButton:hover { color: #0097e6; }
        """)
        btn_volver.clicked.connect(self._cerrar_detalles_inline)
        barra.addWidget(btn_volver, 0, Qt.AlignLeft)
        self.detalles_layout.addLayout(barra)

        # Agrega el widget de detalles debajo
        self.detalles_layout.addWidget(widget)

        # Alterna visibilidad con animación
        self.scroll_area.setVisible(False)
        self.detalles_container.setVisible(True)
        anim = QPropertyAnimation(self.detalles_container, b"maximumHeight")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(800)
        anim.start()
        self.animacion_actual = anim

    def _cerrar_detalles_inline(self):
        anim = QPropertyAnimation(self.detalles_container, b"maximumHeight")
        anim.setDuration(300)
        anim.setStartValue(self.detalles_container.height())
        anim.setEndValue(0)

        def _after():
            self.detalles_container.setVisible(False)
            self.scroll_area.setVisible(True)
            # Reaplica filtro + orden actual del buscador para que todo quede prolijo
            self._filtrar_cards()

        anim.finished.connect(_after)
        anim.start()
        self.animacion_actual = anim

    def abrir_detalles_obra(self, id_obra):
        # Abre DetallesObraWidget dentro del mismo widget (inline), NO como QDialog
        detalle = DetallesObraWidget(id_obra, parent=self)
        self._mostrar_detalles_inline(detalle)

    # ===================== UI Cards =====================

    def _estilizar_card(self, frame):
        frame.setMinimumHeight(180)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def agregar_card_obra(self, obra):
        frame = QFrame()
        self._estilizar_card(frame)

        layout = QVBoxLayout(frame)
        titulo = QLabel(f"{obra['nombre']}")
        titulo.setStyleSheet("font-weight: 600; font-size: 12.5pt;")
        layout.addWidget(titulo)
        layout.addWidget(QLabel(f"Estado: {obra['estado']}"))
        layout.addWidget(QLabel(f"Presupuesto: {obra['presupuesto_total']} Gs."))
        layout.addWidget(QLabel(f"Inicio: {obra['fecha_inicio']}"))

        botones = QHBoxLayout()
        btn_ver = QPushButton("Ver detalles")
        btn_ver.clicked.connect(lambda _, id=obra['id_obra']: self.abrir_detalles_obra(id))
        btn_editar = QPushButton("✎")
        btn_eliminar = QPushButton("🗑")

        btn_editar.clicked.connect(lambda: self.editar_obra(obra['id_obra']))
        btn_eliminar.clicked.connect(lambda: self.eliminar_obra(obra['id_obra']))

        botones.addWidget(btn_ver)
        botones.addStretch()
        botones.addWidget(btn_editar)
        botones.addWidget(btn_eliminar)
        layout.addLayout(botones)

        # Guarda referencia para filtro
        self.cards.append((frame, obra, False))
        self.grid_layout.addWidget(frame)
        self._reflow()

    def editar_obra(self, id_obra):
        conexion_db = conexion()
        cursor = conexion_db.cursor()
        cursor.execute("""
            SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion
            FROM obras WHERE id_obra=%s
        """, (id_obra,))
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
        self._estilizar_card(frame)
        layout = QVBoxLayout(frame)

        # Botón "+" sin círculo, símbolo centrado y color azul
        boton = QPushButton("+")
        boton.setStyleSheet("""
            QPushButton {
                font-size: 48pt;
                font-weight: 500;
                background: transparent;
                border: none;
                color: #0097e6;
                padding: 0px;
            }
            QPushButton:hover { color: #00a8ff; }
            QPushButton:pressed { color: #0984e3; }
        """)
        layout.addStretch()
        layout.addWidget(boton, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        boton.clicked.connect(self.mostrar_formulario_con_animacion)

        self.cards.append((frame, {"nombre": "Nueva obra", "estado": "", "presupuesto_total": "", "fecha_inicio": ""}, True))
        self.grid_layout.addWidget(frame)
        self._reflow()

    # ===================== Animaciones formulario =====================

    def mostrar_formulario_con_animacion(self):
        # Si estaban abiertos los detalles, cerrarlos para volver al grid
        if self.detalles_container.isVisible():
            self._cerrar_detalles_inline()

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

    # ===================== Layout / Flow =====================

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow()

    def _reflow(self):
        """Distribuye en columnas, **sin** cambiar el orden actual del grid."""
        grid = self.grid_layout
        if grid is None or self.scroll_area is None:
            return

        viewport_w = self.scroll_area.viewport().width()
        hspacing = grid.horizontalSpacing() or 12
        vspacing = grid.verticalSpacing() or 12
        min_card_w = 280  # ancho mínimo por card

        # cuántas columnas entran
        columnas = max(1, (viewport_w + hspacing) // (min_card_w + hspacing))
        col_w_total = viewport_w - (columnas - 1) * hspacing
        col_w = max(min_card_w, col_w_total // columnas)

        # Tomar el **orden actual** del grid y reubicar respetándolo
        current_widgets = []
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                current_widgets.append(w)
                w.setParent(None)

        for i, w in enumerate(current_widgets):
            # Ajustes por columna
            w.setMaximumWidth(col_w)
            w.setMinimumWidth(col_w)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row = i // columnas
            col = i % columnas
            grid.addWidget(w, row, col)

        # estirar columnas
        for c in range(columnas):
            grid.setColumnStretch(c, 1)

        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        grid.setHorizontalSpacing(hspacing)
        grid.setVerticalSpacing(vspacing)
        grid.update()

    def _reordenar_frames(self, frames_en_orden):
        """Reinserta los frames al grid en el orden dado (sin cambiar estilos)."""
        grid = self.grid_layout
        if grid is None:
            return

        # Extrae TODOS los widgets actuales del grid
        widgets = []
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                widgets.append(w)
                w.setParent(None)

        # Volvemos a agregar según el orden pedido (solo los que existen)
        for w in frames_en_orden:
            if w in widgets:
                grid.addWidget(w)

        # Los que no estaban en la lista (por seguridad) los mandamos al final
        for w in widgets:
            if w not in frames_en_orden:
                grid.addWidget(w)

    # ===================== Filtro =====================

    def _filtrar_cards(self):
        texto = self.buscador.text().strip().lower()

        visibles = []
        ocultas = []
        frame_nueva = None

        # 1) Determinar visibilidad y construir ranking
        for frame, obra, es_nueva in self.cards:
            if es_nueva:
                frame_nueva = frame
                # La card "Nueva obra" solo visible si no hay búsqueda
                frame.setVisible(texto == "")
                continue

            nombre = str(obra.get("nombre", "")).lower()
            estado = str(obra.get("estado", "")).lower()
            inicio = str(obra.get("fecha_inicio", "")).lower()

            if texto == "":
                # Sin filtro: todas visibles
                frame.setVisible(True)
                # orden natural (por ahora: como se cargó)
                visibles.append((frame, obra, (0, 0, nombre)))
            else:
                # Matcheo
                hay_match = (texto in nombre) or (texto in estado) or (texto in inicio)
                frame.setVisible(hay_match)

                if hay_match:
                    # Ranking: prefijo primero, luego posición, luego alfabético
                    pos = nombre.find(texto)
                    starts = 0 if nombre.startswith(texto) else 1
                    visibles.append((frame, obra, (starts, pos if pos != -1 else 10**6, nombre)))
                else:
                    ocultas.append((frame, obra, (9, 10**6, nombre)))

        # 2) Ordenar: primero visibles por ranking, luego ocultas (al final)
        visibles.sort(key=lambda t: t[2])
        ocultas.sort(key=lambda t: t[2])

        # 3) Armar orden final de frames
        frames_ordenados = [t[0] for t in visibles] + [t[0] for t in ocultas]

        # La card "Nueva obra": al final solo cuando no hay texto
        if texto == "" and frame_nueva is not None:
            frames_ordenados.append(frame_nueva)

        # 4) Reinsertar en ese orden y redistribuir
        self._reordenar_frames(frames_ordenados)
        self._reflow()

    # ===================== Estilos =====================

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
