import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, QDate
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QGridLayout, QFrame, QPushButton, QMessageBox, QSizePolicy, QFileDialog,
    QStackedLayout, QSpacerItem
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

        # ===== ROOT =====
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)      # sin gap arriba/abajo
        root.setSpacing(0)

        # ===== HEADER (fijo, pegado arriba) =====
        self.header = QFrame()
        self.header.setObjectName("obrasHeader")
        self.header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.header.setFixedHeight(64)

        header_l = QHBoxLayout(self.header)
        header_l.setContentsMargins(16, 10, 16, 10)
        header_l.setSpacing(10)

        self.label_titulo = QLabel("Obras")
        try:
            mark_title(self.label_titulo)
        except Exception:
            # fallback por si mark_title deja un “cuadrado”
            self.label_titulo.setStyleSheet("font-size: 18pt; font-weight: 700; color: #0d1b2a;")
        if not (self.label_titulo.text() or "").strip():
            self.label_titulo.setText("Obras")

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar obra…")
        self.buscador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.buscador.setFixedHeight(36)
        try:
            style_search(self.buscador)
        except Exception:
            self.buscador.setStyleSheet("padding:8px 12px; border-radius:10px; border:1px solid #dfe7f5;")

        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.setCursor(Qt.PointingHandCursor)
        self.btn_exportar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_exportar.setFixedHeight(36)
        make_primary(self.btn_exportar)
        self.btn_exportar.clicked.connect(self._exportar_excel_click)

        header_l.addWidget(self.label_titulo)
        header_l.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        header_l.addWidget(self.buscador, 1)
        header_l.addWidget(self.btn_exportar, 0, Qt.AlignRight)

        root.addWidget(self.header, 0)  # stretch 0 => nunca se estira

        # ===== CENTRO: STACK con 3 páginas (ocupa todo el resto) =====
        self.center = QFrame()
        self.center.setObjectName("obrasCenter")
        self.center.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.center, 1)  # stretch 1 => ocupa todo

        self.stack = QStackedLayout(self.center)
        self.stack.setContentsMargins(12, 12, 12, 12)
        self.stack.setSpacing(12)

        # --- Página 0: LISTADO (grid con scroll) ---
        self.page_listado = QFrame()
        page_list_l = QVBoxLayout(self.page_listado)
        page_list_l.setContentsMargins(0, 0, 0, 0)
        page_list_l.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("obrasScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setHorizontalSpacing(12)
        self.grid_layout.setVerticalSpacing(12)
        self.scroll_area.setWidget(self.scroll_widget)
        page_list_l.addWidget(self.scroll_area, 1)

        self.stack.addWidget(self.page_listado)  # index 0

        # --- Página 1: DETALLES inline (siempre full) ---
        self.page_detalles = QFrame()
        detalles_l = QVBoxLayout(self.page_detalles)
        detalles_l.setContentsMargins(0, 0, 0, 0)
        detalles_l.setSpacing(8)

        # barra volver dentro de la página detalles
        self.detalles_bar = QHBoxLayout()
        self.detalles_bar.setContentsMargins(0, 0, 0, 0)
        self.detalles_bar.setSpacing(8)
        self.btn_volver = QPushButton("←")
        self.btn_volver.setFixedWidth(40)
        self.btn_volver.setFixedHeight(36)
        self.btn_volver.setCursor(Qt.PointingHandCursor)
        make_primary(self.btn_volver)
        self.btn_volver.clicked.connect(self._cerrar_detalles_inline)
        self.detalles_bar.addWidget(self.btn_volver, 0, Qt.AlignLeft)
        self.detalles_bar.addStretch()
        detalles_l.addLayout(self.detalles_bar)

        # contenedor real para el widget de detalles
        self.detalles_container = QFrame()
        self.detalles_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detalles_layout = QVBoxLayout(self.detalles_container)
        self.detalles_layout.setContentsMargins(0, 0, 0, 0)
        self.detalles_layout.setSpacing(0)
        detalles_l.addWidget(self.detalles_container, 1)

        self.stack.addWidget(self.page_detalles)  # index 1

        # --- Página 2: FORM nueva/editar obra (full) ---
        self.page_form = QFrame()
        page_form_l = QVBoxLayout(self.page_form)
        page_form_l.setContentsMargins(0, 0, 0, 0)
        page_form_l.setSpacing(0)

        self.formulario_nueva_obra = FormularioNuevaObra(self)
        self.formulario_nueva_obra.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.formulario_nueva_obra.setVisible(True)  # en esta página, siempre visible
        page_form_l.addWidget(self.formulario_nueva_obra, 1)

        self.stack.addWidget(self.page_form)  # index 2

        # === conexiones ===
        self.formulario_nueva_obra.btn_cancelar.clicked.connect(self.ocultar_formulario_con_animacion)
        self.formulario_nueva_obra.btn_aceptar.clicked.connect(self.procesar_formulario_obra)
        self.buscador.textChanged.connect(self._filtrar_cards)

        # estilos
        apply_global_styles(self)
        self.setStyleSheet(self.estilos())

        # data
        QTimer.singleShot(0, self._reflow)
        self.cargar_obras()

    # ===================== EXPORTACIÓN =====================
    def _exportar_excel_click(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar como", "Obras.xlsx", "Excel (*.xlsx)")
        if not ruta:
            return
        try:
            export_todas_obras_excel(conexion, ruta)
            QMessageBox.information(self, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", f"No se pudo exportar todas las obras:\n{e}")

    # ===================== Helpers ids actuales =====================
    def _id_obra_desde_detalles(self):
        if self.stack.currentIndex() != 1:
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

    # ===================== CRUD OBRAS (lógica intacta) =====================
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

    # ===================== Helpers de Detalles =====================
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
        # limpiar contenedor detalles
        for i in reversed(range(self.detalles_layout.count())):
            item = self.detalles_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()

        # agregar el widget (full)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detalles_layout.addWidget(widget, 1)

        # mostrar página detalles (full alto disponible)
        self.stack.setCurrentIndex(1)

    def _cerrar_detalles_inline(self):
        self.stack.setCurrentIndex(0)
        self._filtrar_cards()

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

    # ===================== Vistas (mantengo nombres) =====================
    def mostrar_formulario_con_animacion(self):
        # Sin animación de altura: página dedicada full-height
        self.stack.setCurrentIndex(2)

    def ocultar_formulario_con_animacion(self):
        self.stack.setCurrentIndex(0)
        self.id_obra_en_edicion = None

    # ===================== Layout / Flow =====================
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow()

    def _reflow(self):
        grid = self.grid_layout
        if grid is None or self.scroll_area is None:
            return

        viewport_w = self.scroll_area.viewport().width()
        hspacing = grid.horizontalSpacing() or 12
        vspacing = grid.verticalSpacing() or 12
        min_card_w = 300

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

    # ===================== Filtro (igual) =====================
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
        QWidget { background-color: #f7f9fc; }
        /* Header pegado arriba, prolijo */
        #obrasHeader {
            background: #ffffff;
            border-bottom: 1px solid #e7eef8;
        }
        #obrasScroll { border: none; }
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
