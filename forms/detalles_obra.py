# detalles_obra_willow.py
import sys, os, platform, traceback
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

# ========== ICONOS (rodlerIcons en Desktop/sistema-informatico) ==========
def _desktop_dir() -> Path:
    home = Path.home()
    if platform.system().lower().startswith("win"):
        for env in ("ONEDRIVE", "OneDrive", "OneDriveConsumer"):
            od = os.environ.get(env)
            if od:
                d = Path(od) / "Desktop"
                if d.exists():
                    return d
        d = Path(os.environ.get("USERPROFILE", str(home))) / "Desktop"
        return d if d.exists() else home
    d = home / "Desktop"
    return d if d.exists() else home

ICON_DIR = _desktop_dir() / "sistema-informatico" / "rodlerIcons"
def icon(name: str) -> QIcon:
    p = ICON_DIR / f"{name}.svg"
    return QIcon(str(p)) if p.exists() else QIcon()


# ========== Estilos Willow ==========
QSS_WILLOW = """
* { font-family: "Segoe UI", Arial, sans-serif; color:#0F172A; font-size:13px; }
QWidget { background:#F5F7FB; }
QLabel { background:transparent; }

/* Cards */
#headerCard, .card, QTableWidget {
  background:#FFFFFF;
  border:1px solid #E8EEF6;
  border-radius:16px;
}

/* Título */
QLabel[role="pageTitle"] { font-size:18px; font-weight:800; color:#0F172A; }

/* Botón primario */
QPushButton[type="primary"] {
  background:#2979FF;
  border:1px solid #2979FF;
  color:#FFFFFF;
  border-radius:10px;
  padding:8px 12px;
}
QPushButton[type="primary"]:hover { background:#3b86ff; }

/* Botones icon-only (volver/editar/eliminar) */
QToolButton[type="icon"], QPushButton[type="icon"] {
  background:transparent;
  border:none;
  color:#64748B;
  padding:6px;
  border-radius:8px;
  qproperty-iconSize: 18px 18px;
}
QToolButton[type="icon"]:hover, QPushButton[type="icon"]:hover {
  background:rgba(41,121,255,.10); color:#0F172A;
}

/* Pills y texto secundario */
QLabel[pill="true"] {
  background:#F1F5F9;
  border:1px solid #E8EEF6;
  border-radius:9px;
  padding:3px 8px;
  font-weight:600;
  color:#334155;
}
QLabel[muted="true"] { color:#64748B; }

/* Tabla */
QHeaderView::section {
  background:#F8FAFF;
  color:#0F172A;
  padding:10px;
  border:none;
  border-right:1px solid #E8EEF6;
}
QTableWidget {
  selection-background-color:rgba(41,121,255,.15);
  selection-color:#0F172A;
}
"""


# ---------- Formulario de etapa (inline) ----------
class EtapaFormWidget(QWidget):
    def __init__(self, on_submit, on_cancel=None, parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        root = QFrame(self)
        root.setObjectName("card")
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(root)

        form = QFormLayout(root)
        form.setContentsMargins(16, 16, 16, 10)
        form.setSpacing(10)

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


# --------------------------- DETALLES OBRA (WILLOW) ----------------------------
class DetallesObraWidget(QWidget):
    backRequested = Signal()  # ← señal para volver

    def __init__(self, id_obra, parent=None):
        super().__init__(parent)
        self.id_obra = id_obra

        # ====== raíz
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ====== Header (con icono "volver")
        self.headerCard = QFrame(self); self.headerCard.setObjectName("headerCard")
        hl = QHBoxLayout(self.headerCard); hl.setContentsMargins(16, 12, 16, 12); hl.setSpacing(12)

        self.btnBack = QToolButton(self.headerCard)
        self.btnBack.setProperty("type", "icon")
        self.btnBack.setIcon(icon("chevron-left") or icon("arrow-left"))
        self.btnBack.setToolTip("Volver")
        self.btnBack.clicked.connect(self.backRequested.emit)
        hl.addWidget(self.btnBack)

        titleBlock = QVBoxLayout(); titleBlock.setSpacing(4); titleBlock.setContentsMargins(0,0,0,0)
        self.lbl_titulo_obra = QLabel("Obra"); self.lbl_titulo_obra.setProperty("role","pageTitle")
        self.lbl_meta = QLabel("—"); self.lbl_meta.setProperty("muted","true")
        titleBlock.addWidget(self.lbl_titulo_obra); titleBlock.addWidget(self.lbl_meta)
        hl.addLayout(titleBlock, 1)

        hl.addStretch(1)

        self.btnNuevaEtapa = QPushButton("Agregar etapa")
        self.btnNuevaEtapa.setProperty("type","primary")
        self.btnNuevaEtapa.setIcon(icon("plus"))
        self.btnNuevaEtapa.clicked.connect(lambda: self._toggle_form_etapa(True))
        hl.addWidget(self.btnNuevaEtapa)

        root.addWidget(self.headerCard)

        # ====== Scroll principal
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_w = QWidget()
        self.v = QVBoxLayout(self.scroll_w); self.v.setContentsMargins(0,0,0,0); self.v.setSpacing(12)
        self.scroll.setWidget(self.scroll_w)
        root.addWidget(self.scroll, 1)

        # Form etapa (oculto al inicio)
        self.form_etapa = EtapaFormWidget(on_submit=self._crear_etapa_en_db,
                                          on_cancel=lambda: self._toggle_form_etapa(False))
        self.form_etapa.setVisible(False)
        self.v.addWidget(self.form_etapa)

        # contenedor de secciones
        self.sections = QVBoxLayout(); self.sections.setContentsMargins(0,0,0,0); self.sections.setSpacing(12)
        self.v.addLayout(self.sections)

        # estructuras
        self.trabajos = []
        self._tablas = {}
        self._forms_gasto = {}
        self._forms_editar = {}

        # estilos
        self.setStyleSheet(QSS_WILLOW)

        # datos
        self._cargar_info_obra()
        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    # ===================== Helpers formato =====================
    def _fmt_date(self, d):
        if isinstance(d, date): return d.strftime("%d/%m/%Y")
        return d or ""

    def _fmt_money(self, n):
        try: return f"{float(n):,.0f} Gs.".replace(",", ".")
        except Exception: return str(n) if n is not None else ""

    def _qdate(self, v):
        if isinstance(v, (date, datetime)): return QDate(v.year, v.month, v.day)
        if isinstance(v, str):
            qd = QDate.fromString(v, "yyyy-MM-dd");  qd = qd if qd.isValid() else QDate.fromString(v, "dd/MM/yyyy")
            if qd.isValid(): return qd
        return QDate.currentDate()

    # ===================== Carga info obra =====================
    def _cargar_info_obra(self):
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total
                FROM obras WHERE id_obra=%s
            """, (self.id_obra,))
            row = cur.fetchone()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo leer la obra.\n{e}")
            return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        if not row:
            self.lbl_titulo_obra.setText(f"Obra #{self.id_obra}")
            self.lbl_meta.setText("—")
            return

        nombre, direccion, f_ini, f_fin, estado, m2, presupuesto = row
        self.lbl_titulo_obra.setText(nombre or f"Obra #{self.id_obra}")

        meta_bits = []
        if estado: meta_bits.append(f"Estado: {estado}")
        if f_ini:  meta_bits.append(f"Inicio: {self._fmt_date(f_ini)}")
        if f_fin:  meta_bits.append(f"Fin: {self._fmt_date(f_fin)}")
        if direccion: meta_bits.append(f"Dirección: {direccion}")
        if m2 is not None: meta_bits.append(f"{float(m2):,.0f} m²".replace(",", "."))
        if presupuesto is not None: meta_bits.append(f"Presupuesto: {self._fmt_money(presupuesto)}")
        self.lbl_meta.setText("  •  ".join(meta_bits))

    # ===================== Carga etapas + gastos =====================
    def _cargar_etapas_y_gastos(self):
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""SELECT id, nombre, descripcion, fecha_inicio, fecha_fin
                           FROM trabajos WHERE obra_id=%s ORDER BY id ASC""", (self.id_obra,))
            filas = cur.fetchall()
            etapas = []
            for trabajo_id, nombre, desc, f_ini, f_fin in filas:
                cur.execute("""
                    SELECT id, tipo, concepto, cantidad, unidad, costo_unitario,
                           COALESCE(costo_total, cantidad*costo_unitario) total,
                           to_char(fecha,'DD/MM/YYYY') fecha
                    FROM gastos WHERE trabajo_id=%s ORDER BY fecha ASC, id ASC
                """, (trabajo_id,))
                gs = [{
                    "id": g_id, "tipo": tipo or "", "descripcion": conc or "",
                    "cantidad": float(cant or 0), "unidad": unidad or "",
                    "precio": float(pu or 0), "total": float(tot or 0),
                    "fecha": fecha_txt or ""
                } for (g_id, tipo, conc, cant, unidad, pu, tot, fecha_txt) in cur.fetchall()]

                etapas.append({
                    "id": trabajo_id, "nombre": nombre, "descripcion": desc,
                    "fecha_inicio": f_ini, "fecha_fin": f_fin, "gastos": gs
                })
            self.trabajos = etapas
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudieron cargar etapas/gastos.\n{e}")
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

    # ===================== UI Secciones =====================
    def _clear_sections(self):
        while self.sections.count():
            it = self.sections.takeAt(0); w = it.widget()
            if w: w.deleteLater()
        self._tablas.clear(); self._forms_gasto.clear(); self._forms_editar.clear()

    def _construir_secciones(self):
        self._clear_sections()
        if not self.trabajos:
            empty = QFrame(); empty.setObjectName("card")
            el = QVBoxLayout(empty); el.setContentsMargins(24,24,24,24)
            lbl = QLabel("Aún no hay etapas registradas."); lbl.setAlignment(Qt.AlignCenter)
            el.addWidget(lbl)
            self.sections.addWidget(empty)
            return

        for idx, etapa in enumerate(self.trabajos):
            card = QFrame(); card.setObjectName("card")
            cv = QVBoxLayout(card); cv.setContentsMargins(16,16,16,16); cv.setSpacing(10)

            # ===== Header de la etapa
            h = QHBoxLayout(); h.setContentsMargins(0,0,0,0); h.setSpacing(8)
            title = QLabel(etapa["nombre"]); title.setStyleSheet("font-size:14px; font-weight:700;")
            pill = QLabel(f"{self._fmt_date(etapa['fecha_inicio'])} → {self._fmt_date(etapa['fecha_fin'])}"); pill.setProperty("pill","true")
            h.addWidget(title); h.addSpacing(6); h.addWidget(pill); h.addStretch(1)

            btnEdit = QToolButton(); btnEdit.setProperty("type","icon"); btnEdit.setIcon(icon("edit")); btnEdit.setToolTip("Editar etapa")
            btnDel  = QToolButton(); btnDel.setProperty("type","icon"); btnDel.setIcon(icon("trash")); btnDel.setToolTip("Eliminar etapa")
            btnAddG = QPushButton("Agregar gasto"); btnAddG.setProperty("type","primary"); btnAddG.setIcon(icon("plus"))

            btnEdit.clicked.connect(lambda _, i=idx: self._editar_etapa(i))
            btnDel.clicked.connect(lambda _, i=idx: self._eliminar_etapa(i))
            btnAddG.clicked.connect(lambda _, i=idx: self._toggle_form_gasto(i))

            h.addWidget(btnEdit); h.addWidget(btnDel); h.addWidget(btnAddG)
            cv.addLayout(h)

            # ===== Form editar etapa (inline, oculto)
            form_edit = EtapaFormWidget(
                on_submit=lambda datos, i=idx: self._actualizar_etapa_en_db(i, datos),
                on_cancel=lambda i=idx: self._toggle_form_editar_etapa(i, False),
            )
            form_edit.setVisible(False)
            self._forms_editar[idx] = form_edit
            cv.addWidget(form_edit)

            # ===== Form gasto (inline, oculto)
            form_gasto = GastoFormWidget(
                on_submit=lambda datos, i=idx: self._guardar_gasto(i, datos),
                on_cancel=lambda i=idx: self._ocultar_form_gasto(i),
            )
            form_gasto.setVisible(False)
            self._forms_gasto[idx] = form_gasto
            cv.addWidget(form_gasto)

            # ===== Tabla de gastos
            table = QTableWidget(); table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            table.setMinimumHeight(140)
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["Tipo", "Descripción", "Cantidad", "Unidad", "Costo Unitario", "Total", "Fecha"])
            th = table.horizontalHeader()
            th.setStretchLastSection(True)
            for c in range(7): th.setSectionResizeMode(c, QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setWordWrap(False)
            table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            self._popular_tabla(table, etapa["gastos"])
            self._fit_table_height(table, max_height=360)
            cv.addWidget(table)
            self._tablas[idx] = table

            self.sections.addWidget(card)

    # ======= toggles =======
    def _toggle_form_etapa(self, visible: bool):
        self.form_etapa.setVisible(visible)
        if visible: self.form_etapa.inp_nombre.setFocus()

    def _toggle_form_editar_etapa(self, idx: int, visible: bool):
        form = self._forms_editar.get(idx)
        if not form: return
        if visible:
            t = self.trabajos[idx]
            form.inp_nombre.setText(t.get("nombre") or "")
            form.inp_desc.setPlainText(t.get("descripcion") or "")
            form.inp_inicio.setDate(self._qdate(t.get("fecha_inicio")))
            form.inp_fin.setDate(self._qdate(t.get("fecha_fin")))
            g = self._forms_gasto.get(idx)
            if g and g.isVisible(): g.setVisible(False)
        form.setVisible(visible)
        if visible: form.inp_nombre.setFocus()

    def _toggle_form_gasto(self, idx: int):
        g = self._forms_gasto.get(idx)
        if not g: return
        e = self._forms_editar.get(idx)
        if e and e.isVisible(): e.setVisible(False)
        g.setVisible(not g.isVisible())
        if g.isVisible(): g.input_desc.setFocus()

    def _ocultar_form_gasto(self, idx: int):
        g = self._forms_gasto.get(idx)
        if g: g.setVisible(False); g.limpiar()

    # ===================== helpers UI =====================
    def _popular_tabla(self, tabla, gastos):
        tabla.setRowCount(len(gastos))
        for r, g in enumerate(gastos):
            tabla.setItem(r, 0, QTableWidgetItem(g.get('tipo') or ""))
            tabla.setItem(r, 1, QTableWidgetItem(g.get('descripcion') or ""))
            tabla.setItem(r, 2, QTableWidgetItem(str(g.get('cantidad') or 0)))
            tabla.setItem(r, 3, QTableWidgetItem(g.get('unidad') or ""))
            tabla.setItem(r, 4, QTableWidgetItem(f"{float(g.get('precio') or 0):.2f}"))
            tabla.setItem(r, 5, QTableWidgetItem(f"{float(g.get('total') or 0):.2f}"))
            tabla.setItem(r, 6, QTableWidgetItem(g.get('fecha') or ""))
        tabla.resizeColumnsToContents(); tabla.resizeRowsToContents()

    def _fit_table_height(self, tabla: QTableWidget, max_height=360):
        header_h = tabla.horizontalHeader().height() if tabla.horizontalHeader() else 24
        rows_h = sum(tabla.rowHeight(r) for r in range(tabla.rowCount()))
        frame = tabla.frameWidth() * 2
        padding = 16
        desired = header_h + rows_h + frame + padding
        tabla.setFixedHeight(min(max(desired, 140), max_height))

    # ===================== CRUD Etapas =====================
    def _crear_etapa_en_db(self, datos: dict):
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO trabajos (obra_id, nombre, descripcion, fecha_inicio, fecha_fin)
                VALUES (%s,%s,%s,%s,%s) RETURNING id
            """, (self.id_obra, datos.get("nombre"), datos.get("descripcion"),
                  datos.get("fecha_inicio"), datos.get("fecha_fin")))
            cur.fetchone(); conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass
        self._toggle_form_etapa(False); self.form_etapa.limpiar()
        self._cargar_etapas_y_gastos(); self._construir_secciones()

    def _actualizar_etapa_en_db(self, idx: int, datos: dict):
        etapa_id = self.trabajos[idx]["id"]
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                UPDATE trabajos SET nombre=%s, descripcion=%s, fecha_inicio=%s, fecha_fin=%s WHERE id=%s
            """, (datos.get("nombre"), datos.get("descripcion"),
                  datos.get("fecha_inicio"), datos.get("fecha_fin"), etapa_id))
            conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass
        self._toggle_form_editar_etapa(idx, False)
        self._cargar_etapas_y_gastos(); self._construir_secciones()

    def _eliminar_etapa(self, idx: int):
        etapa_id = self.trabajos[idx]["id"]
        if QMessageBox.question(self, "Eliminar etapa",
                                "¿Seguro que querés eliminar esta etapa? Se eliminarán sus gastos.",
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("DELETE FROM gastos WHERE trabajo_id=%s", (etapa_id,))
            cur.execute("DELETE FROM trabajos WHERE id=%s", (etapa_id,))
            conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass
        self._cargar_etapas_y_gastos(); self._construir_secciones()

    def _editar_etapa(self, idx: int):
        form = self._forms_editar.get(idx)
        if not form: return
        self._toggle_form_editar_etapa(idx, not form.isVisible())

    # ===================== Insert gasto =====================
    def _guardar_gasto(self, idx: int, datos: dict):
        trabajo_id = self.trabajos[idx]["id"]
        concepto = (datos.get("descripcion") or "").strip()
        tipo = (datos.get("tipo") or "").strip()
        unidad = (datos.get("unidad") or "").strip()
        cantidad = float(datos.get("cantidad") or 0)
        precio = float(datos.get("precio") or 0)

        fecha_val = datos.get("fecha")
        if isinstance(fecha_val, QDate): fecha_val = fecha_val.toPython()
        if not isinstance(fecha_val, date):
            parsed = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try: parsed = datetime.strptime(str(fecha_val), fmt).date(); break
                except Exception: pass
            fecha_val = parsed or date.today()

        usa_producto = bool(datos.get("usa_producto"))
        id_producto = int(datos.get("id_producto")) if usa_producto and datos.get("id_producto") else None

        if usa_producto and not id_producto:
            QMessageBox.warning(self, "Falta producto", "Seleccioná un producto para el gasto de Material.")
            return
        if usa_producto and not tipo:
            tipo = "Material"
        if not concepto:
            if usa_producto and id_producto:
                try:
                    conn = conexion(); cur = conn.cursor()
                    cur.execute("SELECT nombre FROM productos WHERE id_producto=%s", (id_producto,))
                    row = cur.fetchone(); concepto = f"Material: {row[0]}" if row else "Material"
                except Exception: pass
                finally:
                    try: cur.close(); conn.close()
                    except Exception: pass
            else:
                QMessageBox.warning(self, "Datos incompletos", "Ingresá una descripción para el gasto.")
                return

        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO gastos (trabajo_id, tipo, concepto, unidad, cantidad, costo_unitario, fecha, id_producto)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (trabajo_id, tipo, concepto, unidad, cantidad, precio, fecha_val, id_producto))
            cur.fetchone(); conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc(); QMessageBox.critical(self, "Error", f"{e}"); return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        self._ocultar_form_gasto(idx)
        self._cargar_etapas_y_gastos(); self._construir_secciones()


if __name__ == "__main__":
    obra_id = 1
    if len(sys.argv) > 1:
        try: obra_id = int(sys.argv[1])
        except Exception: pass
    app = QApplication(sys.argv)
    w = DetallesObraWidget(obra_id)
    w.show()
    sys.exit(app.exec())
