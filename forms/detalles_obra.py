# detalles_obra_willow.py — optimizado (misma lógica; render y refrescos más rápidos)
import sys, os, platform, traceback

from matplotlib import table

from utils.normNumbers import formatear_numero
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from datetime import date, datetime
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QScrollArea, QFrame, QSizePolicy, QHeaderView, QMessageBox,
    QLineEdit, QDateEdit, QTextEdit, QFormLayout, QAbstractScrollArea, QToolButton
)

from db.conexion import conexion
from forms.AgregarGasto import GastoFormWidget
from forms.ui_helpers import style_edit_button, style_delete_button
from utils.normNumbers import formatear_numero

# ===== Iconos
def _desktop_dir() -> Path:
    home = Path.home()
    if platform.system().lower().startswith("win"):
        for env in ("ONEDRIVE", "OneDrive", "OneDriveConsumer"):
            od = os.environ.get(env)
            if od:
                d = Path(od) / "Desktop"
                if d.exists(): return d
        d = Path(os.environ.get("USERPROFILE", str(home))) / "Desktop"
        return d if d.exists() else home
    d = home / "Desktop"
    return d if d.exists() else home

from main.themes import themed_icon
def icon(name: str) -> QIcon:
    return themed_icon(name)

#cantidad .2f
# ===== Form etapa inline (se crea solo cuando se usa)
class EtapaFormWidget(QWidget):
    def __init__(self, on_submit, on_cancel=None, parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        root = QFrame(self); root.setObjectName("card")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(root)

        form = QFormLayout(root); form.setContentsMargins(16, 16, 16, 10); form.setSpacing(10)

        self.inp_nombre = QLineEdit(); self.inp_nombre.setPlaceholderText("Ej.: Cimientos, Muros, Techo…")
        self.inp_desc   = QTextEdit(); self.inp_desc.setPlaceholderText("Descripción (opcional)"); self.inp_desc.setFixedHeight(80)
        self.inp_inicio = QDateEdit(); self.inp_inicio.setCalendarPopup(True); self.inp_inicio.setDate(QDate.currentDate())
        self.inp_fin    = QDateEdit(); self.inp_fin.setCalendarPopup(True); self.inp_fin.setDate(QDate.currentDate())

        form.addRow("Nombre*:", self.inp_nombre)
        form.addRow("Descripción:", self.inp_desc)
        form.addRow("Fecha inicio:", self.inp_inicio)
        form.addRow("Fecha fin:", self.inp_fin)

        btns = QHBoxLayout(); btns.addStretch()
        self.btn_cancelar = QPushButton("Cancelar"); self.btn_cancelar.setProperty("type","primary")
        self.btn_guardar  = QPushButton("Guardar etapa"); self.btn_guardar.setProperty("type","primary")
        btns.addWidget(self.btn_cancelar); btns.addWidget(self.btn_guardar)
        lay.addLayout(btns)

        self.btn_guardar.clicked.connect(self._submit)
        self.btn_cancelar.clicked.connect(lambda: on_cancel() if callable(on_cancel) else None)

    def _submit(self):
        nombre = (self.inp_nombre.text() or "").strip()
        if not nombre:
            QMessageBox.warning(self, "Datos incompletos", "El nombre de la etapa es obligatorio.")
            return
        datos = {
            "nombre": nombre,
            "descripcion": self.inp_desc.toPlainText().strip() or None,
            "fecha_inicio": self.inp_inicio.date().toPython(),
            "fecha_fin": self.inp_fin.date().toPython(),
        }
        if callable(self.on_submit): self.on_submit(datos)

    def limpiar(self):
        self.inp_nombre.clear(); self.inp_desc.clear()
        self.inp_inicio.setDate(QDate.currentDate()); self.inp_fin.setDate(QDate.currentDate())


# ========================= DETALLES OBRA =========================
class DetallesObraWidget(QWidget):
    backRequested = Signal()

    def __init__(self, id_obra, parent=None):
        super().__init__(parent)
        self.id_obra = id_obra

        root = QVBoxLayout(self); root.setContentsMargins(12, 12, 12, 12); root.setSpacing(12)

        # Header
        self.headerCard = QFrame(self); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16, 12, 16, 12); hl.setSpacing(12)

        self.btnBack = QToolButton(self.headerCard); self.btnBack.setProperty("type", "icon")
        self.btnBack.setIcon(icon("chevron-left") or icon("arrow-left")); self.btnBack.setToolTip("Volver")
        self.btnBack.clicked.connect(self.backRequested.emit)
        hl.addWidget(self.btnBack)

        titleBlock = QVBoxLayout(); titleBlock.setSpacing(4); titleBlock.setContentsMargins(0,0,0,0)
        self.lbl_titulo_obra = QLabel("Obra"); self.lbl_titulo_obra.setProperty("role","pageTitle")
        self.lbl_meta = QLabel("—"); self.lbl_meta.setProperty("muted","true")
        titleBlock.addWidget(self.lbl_titulo_obra); titleBlock.addWidget(self.lbl_meta)
        hl.addLayout(titleBlock, 1)
        hl.addStretch(1)

        self.btnNuevaEtapa = QPushButton("Agregar etapa"); self.btnNuevaEtapa.setProperty("type","primary")
        self.btnNuevaEtapa.setIcon(icon("plus"))
        self.btnNuevaEtapa.clicked.connect(lambda: self._toggle_form_etapa(True))
        hl.addWidget(self.btnNuevaEtapa)
        root.addWidget(self.headerCard)

        # Scroll
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_w = QWidget()
        self.v = QVBoxLayout(self.scroll_w); self.v.setContentsMargins(0,0,0,0); self.v.setSpacing(12)
        self.scroll.setWidget(self.scroll_w)
        root.addWidget(self.scroll, 1)

        # Form etapa (lazy visible)
        self.form_etapa = EtapaFormWidget(on_submit=self._crear_etapa_en_db, on_cancel=lambda: self._toggle_form_etapa(False))
        self.form_etapa.setVisible(False)
        self.v.addWidget(self.form_etapa)

        # Secciones (etapas)
        self.sections = QVBoxLayout(); self.sections.setContentsMargins(0,0,0,0); self.sections.setSpacing(12)
        self.v.addLayout(self.sections)
        self.v.addStretch(1)

        # Estructuras
        self.trabajos = []           # [{id, nombre, descripcion, fecha_inicio, fecha_fin, gastos:[...]}]
        self._tablas = {}            # idx -> QTableWidget
        self._forms_gasto = {}       # idx -> GastoFormWidget (lazy)
        self._forms_editar = {}      # idx -> EtapaFormWidget (lazy)

        # Datos
        self._cargar_info_obra()
        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    # ---------- Helpers formato ----------
    def _fmt_date(self, d):
        if isinstance(d, date): return d.strftime("%d/%m/%Y")
        return d or ""

    def _fmt_money(self, n):
        try:
            return f"{formatear_numero(float(n))} Gs."
        except Exception:
            return str(n) if n is not None else ""

    def _qdate(self, v):
        if isinstance(v, (date, datetime)): return QDate(v.year, v.month, v.day)
        if isinstance(v, str):
            qd = QDate.fromString(v, "yyyy-MM-dd")
            if not qd.isValid(): qd = QDate.fromString(v, "dd/MM/yyyy")
            if qd.isValid(): return qd
        return QDate.currentDate()

    # ---------- Carga info obra ----------
    def _cargar_info_obra(self):
        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("""
                    SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total
                    FROM obras
                    WHERE id_obra=%s
                """, (self.id_obra,))
                row = cur.fetchone()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo leer la obra.\n{e}")
            return

        if not row:
            self.lbl_titulo_obra.setText(f"Obra #{self.id_obra}"); self.lbl_meta.setText("—")
            return

        nombre, direccion, f_ini, f_fin, estado, m2, presupuesto = row
        self.lbl_titulo_obra.setText(nombre or f"Obra #{self.id_obra}")
        meta_bits = []
        if estado: meta_bits.append(f"Estado: {estado}")
        if f_ini:  meta_bits.append(f"Inicio: {self._fmt_date(f_ini)}")
        if f_fin:  meta_bits.append(f"Fin: {self._fmt_date(f_fin)}")
        if direccion: meta_bits.append(f"Dirección: {direccion}")
        if m2 is not None:
            meta_bits.append(f"{formatear_numero(float(m2))} m²")
        if presupuesto is not None: meta_bits.append(f"Presupuesto: {self._fmt_money(presupuesto)}")
        self.lbl_meta.setText("  •  ".join(meta_bits))

    # ---------- Carga etapas + gastos (2 queries, ordenados por índices) ----------
    def _cargar_etapas_y_gastos(self):
        try:
            with conexion() as conn, conn.cursor() as cur:
                # Etapas (usa idx_trabajos_obra_fecha_inicio si lo tienes; si no, obra_id + fecha_inicio)
                cur.execute("""
                    SELECT id, nombre, descripcion, fecha_inicio, fecha_fin
                    FROM trabajos
                    WHERE obra_id=%s
                    ORDER BY fecha_inicio DESC NULLS LAST, id DESC
                """, (self.id_obra,))
                filas = cur.fetchall()
                if not filas:
                    self.trabajos = []
                    return

                trabajos = [{
                    "id": t_id, "nombre": nombre, "descripcion": desc,
                    "fecha_inicio": f_ini, "fecha_fin": f_fin, "gastos": []
                } for (t_id, nombre, desc, f_ini, f_fin) in filas]

                ids = [t["id"] for t in trabajos]

                # Gastos de todas las etapas (usa idx_gastos_trabajo_id y/o idx_gastos_fecha si lo creaste)
                cur.execute("""
                    SELECT g.id, g.trabajo_id, g.tipo, g.concepto, g.cantidad, g.unidad,
                           g.costo_unitario,
                           COALESCE(g.costo_total, g.cantidad * g.costo_unitario) AS total,
                           g.fecha
                    FROM gastos g
                    WHERE g.trabajo_id = ANY(%s)
                    ORDER BY g.trabajo_id ASC, g.fecha DESC, g.id DESC
                """, (ids,))

                gastos_by_trabajo = {}
                for g_id, trabajo_id, tipo, concepto, cantidad, unidad, pu, tot, f in cur:
                    gastos_by_trabajo.setdefault(trabajo_id, []).append({
                        "id": g_id,
                        "tipo": tipo or "",
                        "descripcion": concepto or "",
                        "cantidad": float(cantidad or 0),
                        "unidad": unidad or "",
                        "precio": float(pu or 0),
                        "total": float(tot or 0),
                        "fecha": f.strftime("%d/%m/%Y") if hasattr(f, "strftime") else (f or ""),
                    })

                for t in trabajos:
                    t["gastos"] = gastos_by_trabajo.get(t["id"], [])

                self.trabajos = trabajos

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudieron cargar etapas/gastos.\n{e}")

    # ---------- Construcción UI (rápida) ----------
    def _clear_layout(self, layout):
        while layout.count():
            it = layout.takeAt(0); w = it.widget()
            if w: w.deleteLater()

    def _construir_secciones(self):
        self._clear_layout(self.sections)
        self._tablas.clear(); self._forms_gasto.clear(); self._forms_editar.clear()

        if not self.trabajos:
            empty = QFrame(); empty.setObjectName("card")
            el = QVBoxLayout(empty); el.setContentsMargins(24,24,24,24)
            lbl = QLabel("Aún no hay etapas registradas."); lbl.setAlignment(Qt.AlignCenter)
            el.addWidget(lbl)
            self.sections.addWidget(empty)
            return

        for idx, etapa in enumerate(self.trabajos):
            card = QFrame(); card.setObjectName("card")
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
            cv = QVBoxLayout(card); cv.setContentsMargins(16,16,16,16); cv.setSpacing(10)

            # Header etapa
            h = QHBoxLayout(); h.setContentsMargins(0,0,0,0); h.setSpacing(8)
            title = QLabel(etapa["nombre"]); title.setStyleSheet("font-size:14px; font-weight:700;")
            pill = QLabel(f"{self._fmt_date(etapa['fecha_inicio'])} → {self._fmt_date(etapa['fecha_fin'])}"); pill.setProperty("pill","true")
            h.addWidget(title); h.addSpacing(6); h.addWidget(pill); h.addStretch(1)

            btnEdit = QToolButton()
            style_edit_button(btnEdit, "Editar etapa")
            btnDel  = QToolButton()
            style_delete_button(btnDel, "Eliminar etapa")
            btnAddG = QPushButton("Agregar gasto"); btnAddG.setProperty("type","primary"); btnAddG.setIcon(icon("plus"))

            btnEdit.clicked.connect(lambda _, i=idx: self._editar_etapa(i))
            btnDel.clicked.connect(lambda _, i=idx: self._eliminar_etapa(i))
            btnAddG.clicked.connect(lambda _, i=idx: self._toggle_form_gasto(i))

            h.addWidget(btnEdit); h.addWidget(btnDel); h.addWidget(btnAddG)
            cv.addLayout(h)
            cv.addSpacing(6)

            self._forms_editar[idx] = None
            self._forms_gasto[idx]  = None

            table = QTableWidget()

            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            table.setMinimumHeight(180)

            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([
                "Tipo", "Descripción", "Cantidad", "Unidad",
                "Costo Unitario", "Total", "Fecha", "Opciones"
            ])

            th = table.horizontalHeader()
            th.setSectionResizeMode(QHeaderView.Interactive)
            th.setStretchLastSection(True) 

            table.setColumnWidth(0, 110)
            table.setColumnWidth(1, 280)
            table.setColumnWidth(2, 90)
            table.setColumnWidth(3, 90)
            table.setColumnWidth(4, 120)
            table.setColumnWidth(5, 120)
            table.setColumnWidth(6, 110)
            table.setColumnWidth(7, 110)

            table.verticalHeader().setVisible(False)
            table.setWordWrap(False)
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(False)
            table.setUpdatesEnabled(False)
            self._popular_tabla(table, etapa["gastos"])
            table.setUpdatesEnabled(True)
            self._fit_table_height(table, max_height=360)

            cv.addWidget(table)
            self._tablas[idx] = table

            self.sections.addWidget(card)

    # ---------- Toggles (formularios LAZY) ----------
    def _ensure_edit_form(self, idx: int):
        if self._forms_editar.get(idx) is None:
            form_edit = EtapaFormWidget(
                on_submit=lambda datos, i=idx: self._actualizar_etapa_en_db(i, datos),
                on_cancel=lambda i=idx: self._toggle_form_editar_etapa(i, False),
            )
            form_edit.setVisible(False)
            cont = self.sections.itemAt(idx).widget()
            cont.layout().insertWidget(1, form_edit)  # después del header
            self._forms_editar[idx] = form_edit
        return self._forms_editar[idx]

    def _ensure_gasto_form(self, idx: int):
        if self._forms_gasto.get(idx) is None:
            form_gasto = GastoFormWidget(
                on_submit=lambda datos, i=idx: self._guardar_gasto(i, datos),
                on_cancel=lambda i=idx: self._ocultar_form_gasto(i),
            )
            form_gasto.setVisible(False)
            cont = self.sections.itemAt(idx).widget()
            cont.layout().insertWidget(2, form_gasto)  # debajo del form editar si aparece
            self._forms_gasto[idx] = form_gasto
        return self._forms_gasto[idx]

    def _toggle_form_etapa(self, visible: bool):
        self.form_etapa.setVisible(visible)
        if visible: self.form_etapa.inp_nombre.setFocus()

    def _toggle_form_editar_etapa(self, idx: int, visible: bool):
        form = self._ensure_edit_form(idx)
        if visible:
            t = self.trabajos[idx]
            form.inp_nombre.setText(t.get("nombre") or "")
            form.inp_desc.setPlainText(t.get("descripcion") or "")
            # PARCHE: fechas siempre como QDate válido
            form.inp_inicio.setDate(self._qdate(t.get("fecha_inicio")))
            form.inp_fin.setDate(self._qdate(t.get("fecha_fin")))
            g = self._forms_gasto.get(idx)
            if g and g.isVisible(): g.setVisible(False)
        form.setVisible(visible)
        if visible: form.inp_nombre.setFocus()

    def _toggle_form_gasto(self, idx: int):
        g = self._ensure_gasto_form(idx)
        e = self._forms_editar.get(idx)

        if e and e.isVisible():
            e.setVisible(False)

        visible = not g.isVisible()
        g.setVisible(visible)

        if visible:
            g.input_desc.setFocus()

       
        table = self._tablas.get(idx)
        if table:
            self._fit_table_height(table, max_height=360)

    def _ocultar_form_gasto(self, idx: int):
        g = self._forms_gasto.get(idx)
        if g: g.setVisible(False); g.limpiar()

    # ---------- helpers UI ----------
    def _popular_tabla(self, tabla: QTableWidget, gastos):
        n = len(gastos)
        tabla.setRowCount(n)
        for r, g in enumerate(gastos):
            tabla.setItem(r, 0, QTableWidgetItem(g.get('tipo') or ""))
            tabla.setItem(r, 1, QTableWidgetItem(g.get('descripcion') or ""))
            tabla.setItem(r, 2, QTableWidgetItem(str(g.get('cantidad') or 0)))
            tabla.setItem(r, 3, QTableWidgetItem(g.get('unidad') or ""))
            tabla.setItem(r, 4, QTableWidgetItem(formatear_numero(g.get("precio") or 0)))
            tabla.setItem(r, 5, QTableWidgetItem(formatear_numero(g.get("total") or 0)))
            tabla.setItem(r, 6, QTableWidgetItem(g.get('fecha') or ""))

            # Guardamos ID del gasto en la fila
            tabla.item(r, 0).setData(Qt.UserRole, g["id"])

            self._agregar_botones_opciones(tabla, r)

    def _fit_table_height(self, tabla: QTableWidget, max_height=360):
        row_h = 60
        header_h = tabla.horizontalHeader().height() if tabla.horizontalHeader() else 24
        desired = header_h + (tabla.rowCount() * row_h) + 16
        tabla.verticalHeader().setDefaultSectionSize(row_h)
        tabla.setMinimumHeight(min(max(desired, 140), max_height))
        tabla.setMaximumHeight(max_height)

    # ---------- CRUD Etapas ----------
    def _crear_etapa_en_db(self, datos: dict):
        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO trabajos (obra_id, nombre, descripcion, fecha_inicio, fecha_fin)
                    VALUES (%s,%s,%s,%s,%s)
                    RETURNING id
                """, (self.id_obra, datos.get("nombre"), datos.get("descripcion"),
                      datos.get("fecha_inicio"), datos.get("fecha_fin")))
                new_id = cur.fetchone()[0]
                conn.commit()
        except Exception as e:
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return

        # Actualizar en memoria y UI
        self.trabajos.insert(0, {
            "id": new_id,
            "nombre": datos.get("nombre"),
            "descripcion": datos.get("descripcion"),
            "fecha_inicio": datos.get("fecha_inicio"),
            "fecha_fin": datos.get("fecha_fin"),
            "gastos": []
        })
        self.form_etapa.limpiar(); self._toggle_form_etapa(False)
        self._construir_secciones()

    def _actualizar_etapa_en_db(self, idx: int, datos: dict):
        etapa_id = self.trabajos[idx]["id"]
        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("""
                    UPDATE trabajos
                    SET nombre=%s, descripcion=%s, fecha_inicio=%s, fecha_fin=%s
                    WHERE id=%s
                """, (datos.get("nombre"), datos.get("descripcion"),
                      datos.get("fecha_inicio"), datos.get("fecha_fin"), etapa_id))
                conn.commit()
        except Exception as e:
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return

        t = self.trabajos[idx]
        t.update({
            "nombre": datos.get("nombre"),
            "descripcion": datos.get("descripcion"),
            "fecha_inicio": datos.get("fecha_inicio"),
            "fecha_fin": datos.get("fecha_fin"),
        })
        self._toggle_form_editar_etapa(idx, False)
        self._construir_secciones()

    def _eliminar_etapa(self, idx: int):
        etapa_id = self.trabajos[idx]["id"]
        if QMessageBox.question(self, "Eliminar etapa",
                                "¿Seguro que querés eliminar esta etapa? Se eliminarán sus gastos.",
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("DELETE FROM gastos WHERE trabajo_id=%s", (etapa_id,))
                cur.execute("DELETE FROM trabajos WHERE id=%s", (etapa_id,))
                conn.commit()
        except Exception as e:
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return

        del self.trabajos[idx]
        self._construir_secciones()

    def _editar_etapa(self, idx: int):
        self._toggle_form_editar_etapa(idx, True)

    # ---------- Insert gasto (incremental; sin recargar todo) ----------
    def _guardar_gasto(self, idx: int, datos: dict):
        trabajo_id = self.trabajos[idx]["id"]
        concepto = (datos.get("descripcion") or "").strip()
        tipo = (datos.get("tipo") or "").strip()
        unidad = (datos.get("unidad") or "").strip()
        cantidad = float(datos.get("cantidad") or 0)
        precio = float(datos.get("precio") or 0)
    
        # --- Normalización de fecha ---
        fecha_val = datos.get("fecha")
        if isinstance(fecha_val, QDate):
            fecha_val = fecha_val.toPython()
        if not isinstance(fecha_val, date):
            parsed = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    parsed = datetime.strptime(str(fecha_val), fmt).date()
                    break
                except Exception:
                    pass
            fecha_val = parsed or date.today()
    
        usa_producto = bool(datos.get("usa_producto"))
        id_producto = int(datos.get("id_producto")) if usa_producto and datos.get("id_producto") else None
    
        # --- Validación: si usa producto, chequeo de stock antes de insertar ---
        prod_nombre = None
        if usa_producto and not id_producto:
            QMessageBox.warning(self, "Falta producto", "Seleccioná un producto para el gasto de Material.")
            return
    
        if usa_producto:
            # Si no se indicó "tipo", lo forzamos a Material (como antes)
            if not tipo:
                tipo = "Material"
    
            # Intentamos chequear stock disponible (si existe la columna "stock").
            # Si la columna no existe en tu esquema, este bloque se ignora sin romper nada.
            try:
                with conexion() as conn, conn.cursor() as cur:
                    cur.execute("SELECT nombre, COALESCE(stock, 0) FROM productos WHERE id_producto=%s", (id_producto,))
                    row = cur.fetchone()
                    if row:
                        prod_nombre, disponible = row[0], float(row[1] or 0)
                        if cantidad > disponible:
                            # Mensaje claro de stock insuficiente y abortamos
                            QMessageBox.warning(
                                self,
                                "Stock insuficiente",
                                f"No hay stock suficiente para «{prod_nombre}».\n"
                                f"Disponible: {disponible:.0f}  •  Requerido: {cantidad:.0f}"
                            )
                            return
            except Exception:
                # Si falla (p.ej., no existe la columna stock), seguimos y dejamos que
                # la BD valide mediante triggers/funciones; abajo capturamos el error.
                pass
            
        # Si no hay concepto y es material + producto, lo completamos con el nombre del producto
        if not concepto:
            if usa_producto and id_producto:
                try:
                    if prod_nombre is None:
                        with conexion() as conn, conn.cursor() as cur:
                            cur.execute("SELECT nombre FROM productos WHERE id_producto=%s", (id_producto,))
                            row = cur.fetchone()
                            prod_nombre = row[0] if row else None
                    concepto = f"Material: {prod_nombre}" if prod_nombre else "Material"
                except Exception:
                    concepto = "Material"
            else:
                QMessageBox.warning(self, "Datos incompletos", "Ingresá una descripción para el gasto.")
                return
    
        # --- Insert en BD (con captura de errores por stock desde la BD) ---
        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gastos (trabajo_id, tipo, concepto, unidad, cantidad, costo_unitario, fecha, id_producto)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (trabajo_id, tipo, concepto, unidad, cantidad, precio, fecha_val, id_producto))
                new_id = cur.fetchone()[0]
                conn.commit()
        except Exception as e:
            # Si la BD lanzó un error de negocio (trigger/RAISE EXCEPTION), mostramos un mensaje amable
            emsg = (str(e) or "").lower()
            if ("stock" in emsg and ("insuf" in emsg or "no hay" in emsg)) or ("insuf" in emsg):
                # Mensaje claro al usuario
                base = prod_nombre or "el producto seleccionado"
                QMessageBox.warning(self, "Stock insuficiente", f"No hay stock suficiente para {base}.")
                return
            # Otros errores: mostramos el detalle técnico (como venía haciendo)
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"{e}")
            return
    
        # --- Actualización incremental en memoria + tabla (sin reconstruir toda la UI) ---
        g = {
            "id": new_id,
            "tipo": tipo or "",
            "descripcion": concepto or "",
            "cantidad": cantidad,
            "unidad": unidad or "",
            "precio": precio,
            "total": (cantidad * precio),
            "fecha": fecha_val.strftime("%d/%m/%Y"),
        }
        self.trabajos[idx]["gastos"].insert(0, g)  # Insertamos arriba (orden fecha desc)
        table = self._tablas.get(idx)
        if table:
            table.setUpdatesEnabled(False)
            table.insertRow(0)
            table.setItem(0, 0, QTableWidgetItem(g["tipo"]))
            table.setItem(0, 1, QTableWidgetItem(g["descripcion"]))
            table.setItem(0, 2, QTableWidgetItem(str(g["cantidad"])))
            table.setItem(0, 3, QTableWidgetItem(g["unidad"]))
            table.setItem(0, 4, QTableWidgetItem(formatear_numero(g["precio"])))
            table.setItem(0, 5, QTableWidgetItem(formatear_numero(g["total"])))
            table.setItem(0, 6, QTableWidgetItem(g["fecha"]))

            item_ref = QTableWidgetItem()
            item_ref.setData(Qt.UserRole, g)
            table.setItem(0, 7, item_ref)

            self._agregar_botones_opciones(table, 0)

            table.setUpdatesEnabled(True)
            self._fit_table_height(table, max_height=360)
    
        self._ocultar_form_gasto(idx)

    def _agregar_botones_opciones(self, tabla: QTableWidget, row: int):
        cont = QWidget()
        lay = QHBoxLayout(cont)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setSpacing(6)

        btn_edit = QToolButton()
        style_edit_button(btn_edit, "Editar gasto")

        btn_del = QToolButton()
        style_delete_button(btn_del, "Eliminar gasto")

        gasto_id = tabla.item(row, 0).data(Qt.UserRole)

        btn_edit.clicked.connect(
            lambda _, r=row, t=tabla: self._editar_gasto_desde_tabla(t, r)
        )
        btn_del.clicked.connect(
            lambda _, r=row, t=tabla: self._eliminar_gasto_desde_tabla(t, r)
        )

        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)

        tabla.setCellWidget(row, 7, cont)
    
    def _editar_gasto_desde_tabla(self, tabla: QTableWidget, row: int):
        gasto_id = tabla.item(row, 0).data(Qt.UserRole)
        if not gasto_id:
            return

        # Buscar el gasto en memoria y detectar su etapa
        for idx, etapa in enumerate(self.trabajos):
            for g in etapa["gastos"]:
                if g["id"] == gasto_id:
                    form = self._ensure_gasto_form(idx)

                    # --- Precargar datos en el formulario ---
                    form.input_desc.setText(g["descripcion"])
                    form.input_cantidad.setValue(float(g["cantidad"]))
                    form.input_precio.setValue(float(g["precio"]))
                    form.input_unidad.setCurrentText(g["unidad"])
                    form.input_tipo.setCurrentText(g["tipo"])
                    form.input_fecha.setDate(self._qdate(g["fecha"]))

                    # --- Redefinir submit: UPDATE en vez de INSERT ---
                    form.on_submit = (
                        lambda datos, i=idx, gid=gasto_id:
                        self._actualizar_gasto(i, gid, datos)
                    )

                    # --- Mostrar correctamente el formulario ---
                    self._toggle_form_gasto(idx)
                    return



    def _actualizar_gasto(self, idx: int, gasto_id: int, datos: dict):
        cantidad = float(datos.get("cantidad") or 0)
        precio = float(datos.get("precio") or 0)

        fecha_val = datos.get("fecha")
        if isinstance(fecha_val, QDate):
            fecha_val = fecha_val.toPython()

        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("""
                    UPDATE gastos
                    SET tipo=%s,
                        concepto=%s,
                        unidad=%s,
                        cantidad=%s,
                        costo_unitario=%s,
                        fecha=%s
                    WHERE id=%s
                """, (
                    datos.get("tipo"),
                    datos.get("descripcion"),
                    datos.get("unidad"),
                    cantidad,
                    precio,
                    fecha_val,
                    gasto_id
                ))
                conn.commit()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"{e}")
            return

        # actualizar memoria
        for g in self.trabajos[idx]["gastos"]:
            if g["id"] == gasto_id:
                g.update({
                    "tipo": datos.get("tipo"),
                    "descripcion": datos.get("descripcion"),
                    "unidad": datos.get("unidad"),
                    "cantidad": cantidad,
                    "precio": precio,
                    "total": cantidad * precio,
                    "fecha": fecha_val.strftime("%d/%m/%Y"),
                })
                break

        self._construir_secciones()
    

    def _eliminar_gasto_desde_tabla(self, tabla: QTableWidget, row: int):
        gasto_id = tabla.item(row, 0).data(Qt.UserRole)
    
        if QMessageBox.question(
            self,
            "Eliminar gasto",
            "¿Seguro que querés eliminar este gasto?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
    
        try:
            with conexion() as conn, conn.cursor() as cur:
                cur.execute("DELETE FROM gastos WHERE id=%s", (gasto_id,))
                conn.commit()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"{e}")
            return
    
        # eliminar de memoria
        for etapa in self.trabajos:
            etapa["gastos"] = [g for g in etapa["gastos"] if g["id"] != gasto_id]
    
        self._construir_secciones()

if __name__ == "__main__":
    obra_id = 1
    if len(sys.argv) > 1:
        try: obra_id = int(sys.argv[1])
        except Exception: pass
    app = QApplication(sys.argv)
    w = DetallesObraWidget(obra_id)
    w.show()
    sys.exit(app.exec())
