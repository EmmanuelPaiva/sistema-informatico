# obras_willow.py — versión optimizada y con fixes de estado/fechas
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea,
    QGridLayout, QFrame, QPushButton, QMessageBox, QSizePolicy, QFileDialog,
    QStackedLayout
)
from PySide6.QtGui import QIcon

from db.conexion import conexion
from forms.formulario_nueva_obra import FormularioNuevaObra
from forms.detalles_obra import DetallesObraWidget
from reports.excel import export_todas_obras_excel

try:
    from ui_helpers import apply_global_styles, mark_title, style_search, make_primary, make_danger
except ModuleNotFoundError:
    from forms.ui_helpers import apply_global_styles, mark_title, style_search, make_primary, make_danger

try:
    import psycopg2
    from psycopg2 import errors as pg_errors
except Exception:
    psycopg2 = None
    pg_errors = None

from main.themes import themed_icon
def icon(name: str) -> QIcon:
    return themed_icon(name)


def _to_qdate(v) -> QDate:
    if isinstance(v, QDate):
        return v if v.isValid() else QDate.currentDate()
    try:
        if hasattr(v, "year") and hasattr(v, "month") and hasattr(v, "day"):
            return QDate(v.year, v.month, v.day)
    except Exception:
        pass
    if isinstance(v, str):
        q = QDate.fromString(v, "yyyy-MM-dd")
        if not q.isValid():
            q = QDate.fromString(v, "dd/MM/yyyy")
        if q.isValid():
            return q
    return QDate.currentDate()


class ObrasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.id_obra_en_edicion = None
        self.cards = []

        root = QVBoxLayout(self); root.setContentsMargins(12, 12, 12, 12); root.setSpacing(12)

        self.headerCard = QFrame(self); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16, 12, 16, 12); hl.setSpacing(10)

        self.label_titulo = QLabel("Obras"); 
        self.label_titulo.setObjectName("obrasTitle")
        self.label_titulo.setProperty("role", "pageTitle")
        mark_title(self.label_titulo)
        self.label_titulo.setStyleSheet("""
            #obrasTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)

        self.search = QLineEdit(self.headerCard)
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Buscar obra por nombre, estado o fecha…")
        self.search.setClearButtonEnabled(True)
        self.search.addAction(icon("search"), QLineEdit.LeadingPosition)
        style_search(self.search)

        self.btnExport = QPushButton("Exportar", self.headerCard)
        self.btnExport.setProperty("type","primary"); self.btnExport.setIcon(icon("file-spreadsheet"))
        make_primary(self.btnExport); self.btnExport.clicked.connect(self._exportar_excel_click)

        self.btnNueva = QPushButton("Nueva obra", self.headerCard)
        self.btnNueva.setObjectName("btnObraNueva")
        self.btnNueva.setProperty("type","primary")
        self.btnNueva.setProperty("perm_code", "obras.create")
        self.btnNueva.setIcon(icon("plus"))
        make_primary(self.btnNueva)
        self.btnNueva.clicked.connect(self._abrir_nueva_obra)

        hl.addWidget(self.label_titulo); hl.addStretch(1)
        hl.addWidget(self.search, 1); hl.addWidget(self.btnExport); hl.addWidget(self.btnNueva)
        root.addWidget(self.headerCard)

        self.center = QFrame(self); root.addWidget(self.center, 1)
        self.stack = QStackedLayout(self.center); self.stack.setContentsMargins(0, 0, 0, 0); self.stack.setSpacing(12)

        self.page_list = QFrame()
        pl = QVBoxLayout(self.page_list); pl.setContentsMargins(0,0,0,0); pl.setSpacing(0)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_w = QWidget()
        self.grid = QGridLayout(self.scroll_w); self.grid.setContentsMargins(0, 0, 0, 0); self.grid.setHorizontalSpacing(12); self.grid.setVerticalSpacing(12)
        self.scroll.setWidget(self.scroll_w)
        pl.addWidget(self.scroll)
        self.stack.addWidget(self.page_list)

        self.page_det = QFrame()
        pd = QVBoxLayout(self.page_det); pd.setContentsMargins(0,0,0,0); pd.setSpacing(0)
        self.det_container = QFrame()
        self.det_layout = QVBoxLayout(self.det_container); self.det_layout.setContentsMargins(0,0,0,0); self.det_layout.setSpacing(0)
        pd.addWidget(self.det_container, 1)
        self.stack.addWidget(self.page_det)

        self.page_form = QFrame()
        pf = QVBoxLayout(self.page_form); pf.setContentsMargins(0,0,0,0)
        self.form = FormularioNuevaObra(self.page_form)
        pf.addWidget(self.form, 1)
        self.stack.addWidget(self.page_form)

        try:
            self.form.btn_cancelar.clicked.disconnect()
        except Exception:
            pass
        self.form.btn_cancelar.clicked.connect(self.ocultar_formulario_con_animacion)

        try:
            self.form.btn_aceptar.clicked.disconnect()
        except Exception:
            pass
        self.form.btn_aceptar.clicked.connect(self.procesar_formulario_obra)

        self.search.textChanged.connect(self._filtrar_cards)

        apply_global_styles(self)
        self.label_titulo.setStyleSheet("""
            #obrasTitle {
                font-size: 32px;
                font-weight: 400;
                text-transform: none;
            }
        """)
        self.label_titulo.style().unpolish(self.label_titulo)
        self.label_titulo.style().polish(self.label_titulo)

        QTimer.singleShot(0, self._reflow)
        self.cargar_obras()

    def _exportar_excel_click(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar como", "Obras.xlsx", "Excel (*.xlsx)")
        if not ruta: return
        try:
            export_todas_obras_excel(conexion, ruta)
            QMessageBox.information(self, "Éxito", "Exportación completada.")
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", f"No se pudo exportar:\n{e}")

    def procesar_formulario_obra(self):
        datos = self.form.obtener_datos()
        if not datos:
            QMessageBox.warning(self, "Datos inválidos", "Completá los campos obligatorios.")
            return
        try:
            if self.id_obra_en_edicion is not None:
                self.actualizar_obra_en_bd(self.id_obra_en_edicion, datos)
            else:
                self.insertar_obra_en_bd(datos)
            self.form.limpiar_campos()
            self.ocultar_formulario_con_animacion()
            self.refrescar_cards()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la obra:\n{e}")

    def insertar_obra_en_bd(self, datos):
        with conexion() as c, c.cursor() as cur:
            cur.execute("""
                INSERT INTO obras (nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                datos['nombre'], datos['direccion'], datos['fecha_inicio'], datos['fecha_fin'],
                datos['estado'], datos['metros_cuadrados'], datos['presupuesto_total'], datos['descripcion']
            ))
            c.commit()

    def actualizar_obra_en_bd(self, id_obra, datos):
        with conexion() as c, c.cursor() as cur:
            cur.execute("""
                UPDATE obras
                SET nombre=%s, direccion=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s,
                    metros_cuadrados=%s, presupuesto_total=%s, descripcion=%s
                WHERE id_obra=%s
            """, (
                datos['nombre'], datos['direccion'], datos['fecha_inicio'], datos['fecha_fin'],
                datos['estado'], datos['metros_cuadrados'], datos['presupuesto_total'],
                datos['descripcion'], id_obra
            ))
            c.commit()
        self.id_obra_en_edicion = None

    def eliminar_obra_de_bd(self, id_obra):
        try:
            with conexion() as c, c.cursor() as cur:
                cur.execute("DELETE FROM obras WHERE id_obra = %s", (id_obra,))
                c.commit()
            return True
        except Exception as e:
            fk_block = False
            if pg_errors and isinstance(e, pg_errors.ForeignKeyViolation): fk_block = True
            if not fk_block and psycopg2 and getattr(e, 'pgcode', '') == '23503': fk_block = True
            if fk_block:
                resp = QMessageBox.question(self, "No se puede eliminar",
                                            "La obra tiene consumos. ¿Marcar como 'Cerrada'?",
                                            QMessageBox.Yes | QMessageBox.No)
                if resp == QMessageBox.Yes:
                    self.cerrar_obra(id_obra)
                return False
            QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")
            return False

    def cerrar_obra(self, id_obra):
        try:
            with conexion() as c, c.cursor() as cur:
                cur.execute("UPDATE obras SET estado='Cerrada' WHERE id_obra=%s", (id_obra,))
                c.commit()
            QMessageBox.information(self, "Ok", "Obra cerrada.")
            self.refrescar_cards()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cerrar:\n{e}")

    def cargar_obras(self):
        self.cards.clear()
        try:
            with conexion() as c, c.cursor() as cur:
                cur.execute("""
                    SELECT id_obra, nombre, estado, presupuesto_total, fecha_inicio
                    FROM obras
                    ORDER BY fecha_inicio DESC NULLS LAST, id_obra DESC
                """)
                obras = cur.fetchall()

            for (id_obra, nombre, estado, presupuesto_total, fecha_inicio) in obras:
                fecha_txt = _to_qdate(fecha_inicio).toString("yyyy-MM-dd")
                self._agregar_card({
                    "id_obra": id_obra,
                    "nombre": nombre,
                    "estado": estado or "",
                    "presupuesto_total": float(presupuesto_total or 0),
                    "fecha_inicio": fecha_txt,
                })
        except Exception as e:
            print("Error cargando obras:", e)
        finally:
            self._agregar_card_nueva()

    def refrescar_cards(self):
        self._clear_grid(self.grid)
        self.cards.clear()
        self.cargar_obras()
        self._reflow()
        self._filtrar_cards()

    def _mostrar_detalles_inline(self, widget: QWidget):
        self.headerCard.setVisible(False)
        self._clear_layout(self.det_layout)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.det_layout.addWidget(widget, 1)
        try:
            widget.backRequested.disconnect()
        except Exception:
            pass
        widget.backRequested.connect(self._cerrar_detalles_inline)
        self.stack.setCurrentIndex(1)

    def _cerrar_detalles_inline(self):
        self.stack.setCurrentIndex(0)
        self.headerCard.setVisible(True)
        self._filtrar_cards()

    def abrir_detalles_obra(self, id_obra):
        detalle = DetallesObraWidget(id_obra, parent=self)
        self._mostrar_detalles_inline(detalle)

    def _agregar_card(self, obra):
        card = QFrame(); card.setObjectName("card"); card.setProperty("class","card")
        card.setMinimumHeight(170); card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(card); v.setContentsMargins(16,16,16,16); v.setSpacing(10)

        top = QHBoxLayout(); top.setContentsMargins(0,0,0,0); top.setSpacing(8)
        title = QLabel(obra["nombre"]); title.setStyleSheet("font-size:15px; font-weight:700;")
        pill = QLabel(obra["estado"]); pill.setProperty("pill","true")
        top.addWidget(title); top.addStretch(1); top.addWidget(pill)

        btnEdit = QPushButton(); btnEdit.setObjectName("btnObraEditar")
        btnEdit.setProperty("type", "icon"); btnEdit.setProperty("variant", "edit"); btnEdit.setProperty("perm_code", "obras.update")
        btnEdit.setIcon(icon("edit"))

        btnDel  = QPushButton(); btnDel.setObjectName("btnObraEliminar")
        btnDel.setProperty("type", "icon"); btnDel.setProperty("variant", "delete"); btnDel.setProperty("perm_code", "obras.delete")
        btnDel.setIcon(icon("trash"))

        btnEdit.setToolTip("Editar obra"); btnDel.setToolTip("Eliminar obra")
        btnEdit.style().unpolish(btnEdit); btnEdit.style().polish(btnEdit)
        btnDel.style().unpolish(btnDel);   btnDel.style().polish(btnDel)

        btnEdit.clicked.connect(lambda: self._editar_obra(obra["id_obra"]))
        btnDel.clicked.connect(lambda: self._eliminar_obra(obra["id_obra"]))
        top.addWidget(btnEdit); top.addWidget(btnDel)
        v.addLayout(top)

        meta = QHBoxLayout(); meta.setContentsMargins(0,0,0,0); meta.setSpacing(14)
        lbl_pres = QLabel(f"Presupuesto: {obra['presupuesto_total']:.2f} Gs."); lbl_pres.setProperty("muted","true")
        lbl_ini  = QLabel(f"Inicio: {obra['fecha_inicio']}"); lbl_ini.setProperty("muted","true")
        meta.addWidget(lbl_pres); meta.addWidget(lbl_ini); meta.addStretch(1)
        v.addLayout(meta)

        cta = QHBoxLayout(); cta.setContentsMargins(0,0,0,0)
        btnVer = QPushButton("Ver detalles"); btnVer.setProperty("type","primary"); make_primary(btnVer)
        btnVer.clicked.connect(lambda _, i=obra["id_obra"]: self.abrir_detalles_obra(i))
        cta.addWidget(btnVer, 0, Qt.AlignLeft)
        v.addLayout(cta)

        self.cards.append((card, obra, False))
        self.grid.addWidget(card)
        self._reflow()

    def _agregar_card_nueva(self):
        add = QFrame(); add.setProperty("class","card"); add.setMinimumHeight(170)
        v = QVBoxLayout(add); v.setContentsMargins(16,16,16,16)
        plus = QPushButton("Nueva obra"); plus.setProperty("type","primary"); plus.setIcon(icon("plus"))
        make_primary(plus); plus.setCursor(Qt.PointingHandCursor)
        v.addStretch(1); v.addWidget(plus, 0, Qt.AlignHCenter); v.addStretch(1)
        plus.clicked.connect(self._abrir_nueva_obra)
        self.cards.append((add, {"id_obra": None}, True))
        self.grid.addWidget(add)

    def _abrir_nueva_obra(self):
        self.id_obra_en_edicion = None
        if hasattr(self.form, "limpiar_campos"):
            self.form.limpiar_campos()
        try:
            self.form.input_estado.setCurrentIndex(0)
        except Exception:
            pass
        self.mostrar_formulario_con_animacion()

    def _editar_obra(self, id_obra):
        with conexion() as c, c.cursor() as cur:
            cur.execute("""
                SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion
                FROM obras
                WHERE id_obra=%s
            """, (id_obra,))
            datos = cur.fetchone()
        if not datos:
            return

        self.id_obra_en_edicion = id_obra

        self.form.input_nombre.setText(datos[0] or "")
        self.form.input_direccion.setText(datos[1] or "")
        self.form.input_fecha_inicio.setDate(_to_qdate(datos[2]))
        self.form.input_fecha_fin.setDate(_to_qdate(datos[3]))
        self.form.input_estado.setCurrentText(datos[4] or "")
        try:
            self.form.input_metros.setValue(float(datos[5] or 0))
        except Exception:
            self.form.input_metros.setValue(0.0)
        try:
            self.form.input_presupuesto.setValue(float(datos[6] or 0))
        except Exception:
            self.form.input_presupuesto.setValue(0.0)
        self.form.input_descripcion.setText(datos[7] or "")

        self.mostrar_formulario_con_animacion()

    def _eliminar_obra(self, id_obra):
        if QMessageBox.question(self, "Eliminar obra", "¿Eliminar esta obra?",
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        if self.eliminar_obra_de_bd(id_obra):
            self.refrescar_cards()

    def mostrar_formulario_con_animacion(self):
        self.stack.setCurrentIndex(2)

    def ocultar_formulario_con_animacion(self):
        self.stack.setCurrentIndex(0)
        self.id_obra_en_edicion = None

    def resizeEvent(self, event):
        super().resizeEvent(event); self._reflow()

    def _reflow(self):
        grid = self.grid
        if grid is None or self.scroll is None:
            return
        vw = self.scroll.viewport().width()
        hsp = grid.horizontalSpacing() or 12
        min_w = 310
        cols = max(1, (vw + hsp) // (min_w + hsp))
        col_w = max(min_w, (vw - (cols - 1) * hsp) // cols)

        widgets = []
        while grid.count():
            it = grid.takeAt(0); w = it.widget()
            if w: widgets.append(w); w.setParent(None)

        for i, w in enumerate(widgets):
            w.setMaximumWidth(col_w); w.setMinimumWidth(col_w)
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            r, c = divmod(i, cols); grid.addWidget(w, r, c)

        for c in range(cols): grid.setColumnStretch(c, 1)
        grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def _reordenar(self, ordered_frames):
        widgets = []
        while self.grid.count():
            it = self.grid.takeAt(0); w = it.widget()
            if w: widgets.append(w); w.setParent(None)
        for w in ordered_frames:
            if w in widgets: self.grid.addWidget(w)
        for w in widgets:
            if w not in ordered_frames: self.grid.addWidget(w)

    def _filtrar_cards(self):
        text = (self.search.text() or "").strip().lower()
        visibles, ocultas, add_frame = [], [], None
        for frame, obra, es_nueva in self.cards:
            if es_nueva:
                add_frame = frame
                frame.setVisible(text == "")
                continue
            nombre = str(obra.get("nombre","")).lower()
            estado = str(obra.get("estado","")).lower()
            inicio = str(obra.get("fecha_inicio","")).lower()
            match = (text == "") or (text in nombre) or (text in estado) or (text in inicio)
            frame.setVisible(match)
            key = (0 if (text and nombre.startswith(text)) else 1, nombre)
            (visibles if match else ocultas).append((frame, key))
        visibles.sort(key=lambda t: t[1]); ocultas.sort(key=lambda t: t[1])
        ordered = [f for f,_ in visibles] + [f for f,_ in ocultas]
        if text == "" and add_frame is not None:
            ordered.append(add_frame)
        self._reordenar(ordered)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            it = layout.takeAt(0); w = it.widget()
            if w: w.deleteLater()

    @staticmethod
    def _clear_grid(grid):
        while grid.count():
            it = grid.takeAt(0); w = it.widget()
            if w: w.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ObrasWidget()
    w.show()
    sys.exit(app.exec())
