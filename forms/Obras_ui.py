import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, QDate
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QGridLayout, QFrame, QPushButton, QMessageBox, QSizePolicy, QFileDialog
)
from db.conexion import conexion
from forms.formulario_nueva_obra import FormularioNuevaObra
from forms.detalles_obra import DetallesObraWidget

# estilos del sistema
try:
    from ui_helpers import apply_global_styles, mark_title, style_search, make_primary, make_danger
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles, mark_title, style_search, make_primary, make_danger

# errores específicos de Postgres (opcional, mejora mensajes)
try:
    import psycopg2
    from psycopg2 import errors as pg_errors
except Exception:
    psycopg2 = None
    pg_errors = None

from reports.excel import export_todas_obras_excel


class ObrasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animacion_actual = None
        self.id_obra_en_edicion = None
        self.cards = []  # [(frame, data_dict, es_nueva_obra)]
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(12, 12, 12, 12)
        self.layout_principal.setSpacing(12)

        # === Encabezado ===
        self.encabezado = QWidget()
        encabezado_layout = QHBoxLayout(self.encabezado)
        encabezado_layout.setContentsMargins(0, 0, 0, 0)
        encabezado_layout.setSpacing(10)

        self.label_titulo = QLabel("Obras")
        mark_title(self.label_titulo)

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar obra…")
        self.buscador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        style_search(self.buscador)
        self.buscador.textChanged.connect(self._filtrar_cards)

        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.setCursor(Qt.PointingHandCursor)
        make_primary(self.btn_exportar)
        self.btn_exportar.clicked.connect(self._exportar_excel_click)

        encabezado_layout.addWidget(self.label_titulo)
        encabezado_layout.addStretch()
        encabezado_layout.addWidget(self.buscador, 1)
        encabezado_layout.addWidget(self.btn_exportar, 0, Qt.AlignRight)
        self.layout_principal.addWidget(self.encabezado)

        # === Listado (grid con scroll) ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setHorizontalSpacing(12)
        self.grid_layout.setVerticalSpacing(12)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout_principal.addWidget(self.scroll_area, 1)

        # === Contenedor de detalles inline (oculto por defecto) ===
        self.detalles_container = QFrame()
        self.detalles_container.setVisible(False)
        self.detalles_container.setMaximumHeight(0)
        self.detalles_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.detalles_layout = QVBoxLayout(self.detalles_container)
        self.detalles_layout.setContentsMargins(0, 0, 0, 0)
        self.detalles_layout.setSpacing(8)
        self.layout_principal.addWidget(self.detalles_container, 0)

        # === Formulario nueva/editar obra (oculto por defecto) ===
        self.formulario_nueva_obra = FormularioNuevaObra(self)
        self.formulario_nueva_obra.setMaximumHeight(0)
        self.formulario_nueva_obra.setVisible(False)
        self.formulario_nueva_obra.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout_principal.addWidget(self.formulario_nueva_obra, 0)

        self.formulario_nueva_obra.btn_cancelar.clicked.connect(self.ocultar_formulario_con_animacion)
        self.formulario_nueva_obra.btn_aceptar.clicked.connect(self.procesar_formulario_obra)

        # estilos globales + locales
        apply_global_styles(self)
        self.setStyleSheet(self.estilos())

        QTimer.singleShot(0, self._reflow)
        self.cargar_obras()

    # ===================== EXPORTACIÓN =====================

    def _exportar_excel_click(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar como", "Obras.xlsx", "Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            export_todas_obras_excel(conexion, ruta)
            QMessageBox.information(self, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", f"No se pudo exportar todas las obras:\n{e}")

    # ===================== Helpers ids actuales =====================

    def _id_obra_desde_detalles(self):
        if not self.detalles_container.isVisible():
            return None
        for i in range(self.detalles_layout.count()):
            item = self.detalles_layout.itemAt(i)
            w = item.widget()
            if isinstance(w, DetallesObraWidget) and hasattr(w, "id_obra"):
                return getattr(w, "id_obra", None)
        return None

    def _id_obra_unica_visible(self):
        visibles = []
        for frame, obra, es_nueva in self.cards:
            if es_nueva:
                continue
            if frame.isVisible():
                visibles.append(obra)
        if len(visibles) == 1:
            return visibles[0].get("id_obra")
        return None

    # ===================== CRUD OBRAS =====================

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
            QMessageBox.critical(self, "Error", f"No se pudo guardar la obra:\n{e}")

    def insertar_obra_en_bd(self, datos):
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("""
                    INSERT INTO obras (nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_obra
                """, (
                    datos['nombre'], datos['direccion'], datos['fecha_inicio'], datos['fecha_fin'],
                    datos['estado'], datos['metros_cuadrados'], datos['presupuesto_total'], datos['descripcion']
                ))
            c.commit()

    def actualizar_obra_en_bd(self, id_obra, datos):
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("""
                    UPDATE obras
                    SET nombre=%s, direccion=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s,
                        metros_cuadrados=%s, presupuesto_total=%s, descripcion=%s
                    WHERE id_obra=%s
                """, (
                    datos['nombre'], datos['direccion'], datos['fecha_inicio'], datos['fecha_fin'],
                    datos['estado'], datos['metros_cuadrados'], datos['presupuesto_total'], datos['descripcion'], id_obra
                ))
            c.commit()
        self.id_obra_en_edicion = None

    def eliminar_obra_de_bd(self, id_obra):
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute("DELETE FROM obras WHERE id_obra = %s", (id_obra,))
                c.commit()
            return True
        except Exception as e:
            fk_block = False
            if pg_errors and isinstance(e, pg_errors.ForeignKeyViolation):
                fk_block = True
            if not fk_block and psycopg2 and hasattr(e, 'pgcode') and e.pgcode == '23503':
                fk_block = True

            if fk_block:
                resp = QMessageBox.question(
                    self,
                    "No se puede eliminar",
                    "Esta obra tiene consumos registrados y no puede eliminarse.\n\n"
                    "¿Querés marcarla como 'Cerrada' en su lugar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if resp == QMessageBox.Yes:
                    self.cerrar_obra(id_obra)
                return False
            else:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la obra:\n{e}")
                return False

    def cerrar_obra(self, id_obra):
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute("UPDATE obras SET estado = 'Cerrada' WHERE id_obra = %s", (id_obra,))
                c.commit()
            QMessageBox.information(self, "Obra cerrada", "La obra fue marcada como 'Cerrada'.")
            self.refrescar_cards()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cerrar la obra:\n{e}")

    def cargar_obras(self):
        self.cards.clear()
        try:
            with conexion() as c:
                with c.cursor() as cur:
                    cur.execute("""
                        SELECT id_obra, nombre, estado, presupuesto_total, fecha_inicio
                        FROM obras
                        ORDER BY id_obra DESC
                    """)
                    obras = cur.fetchall()
            for (id_obra, nombre, estado, presupuesto_total, fecha_inicio) in obras:
                self.agregar_card_obra({
                    "id_obra": id_obra,
                    "nombre": nombre,
                    "estado": estado,
                    "presupuesto_total": presupuesto_total,
                    "fecha_inicio": fecha_inicio if isinstance(fecha_inicio, (str,)) else (fecha_inicio or QDate.currentDate())
                })
        except Exception as e:
            print("Error cargando obras:", e)
        finally:
            self.agregar_card_nueva_obra()

    def refrescar_cards(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.cards.clear()
        self.cargar_obras()
        self._reflow()
        self._filtrar_cards()

    # ===================== Consumos de obra (helpers para DetallesObraWidget) =====================

    def registrar_consumo(self, id_obra: int, id_producto: int, cantidad: float, nota: str = None):
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("""
                    INSERT INTO obras_consumos (id_obra, id_producto, cantidad, nota)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_consumo
                """, (id_obra, id_producto, cantidad, nota))
            c.commit()

    def actualizar_consumo(self, id_consumo: int, id_obra: int, id_producto: int, cantidad: float, nota: str = None):
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("""
                    UPDATE obras_consumos
                    SET id_obra=%s, id_producto=%s, cantidad=%s, nota=%s
                    WHERE id_consumo=%s
                """, (id_obra, id_producto, cantidad, nota, id_consumo))
            c.commit()

    def eliminar_consumo(self, id_consumo: int):
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM obras_consumos WHERE id_consumo = %s", (id_consumo,))
            c.commit()

    # ===================== Navegación / Vistas =====================

    def _mostrar_detalles_inline(self, widget):
        # limpiar contenido previo
        for i in reversed(range(self.detalles_layout.count())):
            item = self.detalles_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()

        # barra de volver
        barra = QHBoxLayout()
        barra.setContentsMargins(0, 0, 8, 8)
        btn_volver = QPushButton("←")
        btn_volver.setFixedWidth(40)
        btn_volver.setCursor(Qt.PointingHandCursor)
        make_primary(btn_volver)
        btn_volver.clicked.connect(self._cerrar_detalles_inline)
        barra.addWidget(btn_volver, 0, Qt.AlignLeft)
        self.detalles_layout.addLayout(barra)

        # el widget de detalles debe poder expandir
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detalles_layout.addWidget(widget)

        self.scroll_area.setVisible(False)
        self.detalles_container.setVisible(True)

        # animación controlada por alto disponible
        target = max(200, int(self.height() * 0.65))
        anim = QPropertyAnimation(self.detalles_container, b"maximumHeight")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(target)
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
            self._filtrar_cards()

        anim.finished.connect(_after)
        anim.start()
        self.animacion_actual = anim

    def abrir_detalles_obra(self, id_obra):
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
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        titulo = QLabel(f"{obra['nombre']}")
        titulo.setStyleSheet("font-weight: 600; font-size: 13pt;")
        titulo.setWordWrap(True)
        titulo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(titulo)

        lbl_estado = QLabel(f"Estado: {obra['estado']}")
        lbl_pres = QLabel(f"Presupuesto: {obra['presupuesto_total']} Gs.")
        lbl_inicio = QLabel(f"Inicio: {obra['fecha_inicio']}")
        for lab in (lbl_estado, lbl_pres, lbl_inicio):
            lab.setWordWrap(True)
            lab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layout.addWidget(lab)

        botones = QHBoxLayout()
        botones.setContentsMargins(0, 4, 0, 0)
        botones.setSpacing(8)

        btn_ver = QPushButton("Ver detalles")
        btn_editar = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")

        for b in (btn_ver, btn_editar, btn_eliminar):
            b.setCursor(Qt.PointingHandCursor)

        make_primary(btn_ver)
        make_primary(btn_editar)
        make_danger(btn_eliminar)

        btn_ver.clicked.connect(lambda _, id=obra['id_obra']: self.abrir_detalles_obra(id))
        btn_editar.clicked.connect(lambda: self.editar_obra(obra['id_obra']))
        btn_eliminar.clicked.connect(lambda: self.eliminar_obra(obra['id_obra']))

        botones.addWidget(btn_ver)
        botones.addStretch()
        botones.addWidget(btn_editar)
        botones.addWidget(btn_eliminar)
        layout.addLayout(botones)

        self.cards.append((frame, obra, False))
        self.grid_layout.addWidget(frame)
        self._reflow()

    def editar_obra(self, id_obra):
        with conexion() as c:
            with c.cursor() as cur:
                cur.execute("""
                    SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion
                    FROM obras WHERE id_obra=%s
                """, (id_obra,))
                datos = cur.fetchone()

        if datos:
            self.id_obra_en_edicion = id_obra
            self.formulario_nueva_obra.input_nombre.setText(datos[0] or "")
            self.formulario_nueva_obra.input_direccion.setText(datos[1] or "")
            self.formulario_nueva_obra.input_fecha_inicio.setDate(datos[2] or QDate.currentDate())
            self.formulario_nueva_obra.input_fecha_fin.setDate(datos[3] or QDate.currentDate())
            self.formulario_nueva_obra.input_estado.setCurrentText(datos[4] or "")
            self.formulario_nueva_obra.input_metros.setValue(float(datos[5] or 0))
            self.formulario_nueva_obra.input_presupuesto.setValue(float(datos[6] or 0))
            self.formulario_nueva_obra.input_descripcion.setText(datos[7] or "")
            self.mostrar_formulario_con_animacion()

    def eliminar_obra(self, id_obra):
        confirmacion = QMessageBox.question(
            self, "Eliminar obra",
            "¿Estás seguro de que querés eliminar esta obra?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacion != QMessageBox.Yes:
            return
        ok = self.eliminar_obra_de_bd(id_obra)
        if ok:
            self.refrescar_cards()

    def agregar_card_nueva_obra(self):
        frame = QFrame()
        self._estilizar_card(frame)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        boton = QPushButton("+")
        boton.setCursor(Qt.PointingHandCursor)
        boton.setStyleSheet("""
            QPushButton {
                font-size: 44pt;
                font-weight: 500;
                background: transparent;
                border: none;
            }
        """)
        make_primary(boton)

        layout.addStretch()
        layout.addWidget(boton, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        boton.clicked.connect(self.mostrar_formulario_con_animacion)

        self.cards.append((frame, {"id_obra": None, "nombre": "Nueva obra", "estado": "", "presupuesto_total": "", "fecha_inicio": ""}, True))
        self.grid_layout.addWidget(frame)
        self._reflow()

    # ===================== Animaciones formulario =====================

    def mostrar_formulario_con_animacion(self):
        if self.detalles_container.isVisible():
            self._cerrar_detalles_inline()

        form = self.formulario_nueva_obra
        form.setVisible(True)
        target = max(220, int(self.height() * 0.6))
        anim = QPropertyAnimation(form, b'maximumHeight')
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(target)
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
        # ajustar alturas visibles para evitar cortes
        if self.detalles_container.isVisible():
            self.detalles_container.setMaximumHeight(max(220, int(self.height() * 0.65)))
        if self.formulario_nueva_obra.isVisible():
            self.formulario_nueva_obra.setMaximumHeight(max(220, int(self.height() * 0.6)))

    def _reflow(self):
        grid = self.grid_layout
        if grid is None or self.scroll_area is None:
            return

        viewport_w = self.scroll_area.viewport().width()
        hspacing = grid.horizontalSpacing() or 12
        vspacing = grid.verticalSpacing() or 12
        min_card_w = 300  # un poco más ancho para evitar cortes

        columnas = max(1, (viewport_w + hspacing) // (min_card_w + hspacing))
        col_w_total = viewport_w - (columnas - 1) * hspacing
        col_w = max(min_card_w, col_w_total // columnas)

        current_widgets = []
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                current_widgets.append(w)
                w.setParent(None)

        for i, w in enumerate(current_widgets):
            w.setMaximumWidth(col_w)
            w.setMinimumWidth(col_w)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row = i // columnas
            col = i % columnas
            grid.addWidget(w, row, col)

        for c in range(columnas):
            grid.setColumnStretch(c, 1)

        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        grid.setHorizontalSpacing(hspacing)
        grid.setVerticalSpacing(vspacing)
        grid.update()

    def _reordenar_frames(self, frames_en_orden):
        grid = self.grid_layout
        if grid is None:
            return

        widgets = []
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                widgets.append(w)
                w.setParent(None)

        for w in frames_en_orden:
            if w in widgets:
                grid.addWidget(w)

        for w in widgets:
            if w not in frames_en_orden:
                grid.addWidget(w)

    # ===================== Filtro =====================

    def _filtrar_cards(self):
        texto = self.buscador.text().strip().lower()

        visibles = []
        ocultas = []
        frame_nueva = None

        for frame, obra, es_nueva in self.cards:
            if es_nueva:
                frame_nueva = frame
                frame.setVisible(texto == "")
                continue

            nombre = str(obra.get("nombre", "")).lower()
            estado = str(obra.get("estado", "")).lower()
            inicio = str(obra.get("fecha_inicio", "")).lower()

            if texto == "":
                frame.setVisible(True)
                visibles.append((frame, obra, (0, 0, nombre)))
            else:
                hay_match = (texto in nombre) or (texto in estado) or (texto in inicio)
                frame.setVisible(hay_match)

                if hay_match:
                    pos = nombre.find(texto)
                    starts = 0 if nombre.startswith(texto) else 1
                    visibles.append((frame, obra, (starts, pos if pos != -1 else 10**6, nombre)))
                else:
                    ocultas.append((frame, obra, (9, 10**6, nombre)))

        visibles.sort(key=lambda t: t[2])
        ocultas.sort(key=lambda t: t[2])
        frames_ordenados = [t[0] for t in visibles] + [t[0] for t in ocultas]

        if texto == "" and frame_nueva is not None:
            frames_ordenados.append(frame_nueva)

        self._reordenar_frames(frames_ordenados)
        self._reflow()

    # ===================== Estilos =====================

    def estilos(self):
        return """
        QWidget {
            background-color: #f7f9fc;
        }
        QScrollArea { border: none; }
        QFrame {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 12px;
            border: 1px solid #dfe7f5;
        }
        QFrame:hover {
            border: 1px solid #8ec5ff;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
        }
        QLabel { color: #0d1b2a; }
        QPushButton {
            border-radius: 10px;
            padding: 8px 14px;
        }
        QLineEdit {
            border-radius: 10px;
            padding: 8px 12px;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ObrasWidget()
    window.show()
    sys.exit(app.exec())
