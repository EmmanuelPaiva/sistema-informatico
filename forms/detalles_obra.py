import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QScrollArea, QFrame, QHBoxLayout, QSizePolicy, QHeaderView,
    QMessageBox, QLineEdit, QDateEdit, QTextEdit, QFormLayout, QAbstractScrollArea,
    QToolButton, QStyle
)
import traceback
from datetime import date, datetime

from db.conexion import conexion
from forms.AgregarGasto import GastoFormWidget


# -------- Formulario inline para crear/editar ETAPA ----------
class EtapaFormWidget(QWidget):
    def __init__(self, on_submit, on_cancel=None, parent=None):
        super().__init__(parent)
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        root = QFrame(self)
        root.setObjectName("EtapaFormFrame")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(root)

        form = QFormLayout(root)
        form.setContentsMargins(10, 10, 10, 6)
        form.setSpacing(10)

        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Ej.: Cimientos, Muros, Techo…")
        form.addRow("Nombre*:", self.inp_nombre)

        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Descripción (opcional)")
        self.inp_desc.setFixedHeight(70)
        form.addRow("Descripción:", self.inp_desc)

        self.inp_inicio = QDateEdit()
        self.inp_inicio.setCalendarPopup(True)
        self.inp_inicio.setDate(QDate.currentDate())
        form.addRow("Fecha inicio:", self.inp_inicio)

        self.inp_fin = QDateEdit()
        self.inp_fin.setCalendarPopup(True)
        self.inp_fin.setDate(QDate.currentDate())
        form.addRow("Fecha fin:", self.inp_fin)

        btns = QHBoxLayout()
        btns.addStretch()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar = QPushButton("Guardar etapa")
        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_guardar)
        lay.addLayout(btns)

        self.setStyleSheet("""
            #EtapaFormFrame {
                background: #ffffff;
                border: 1px solid #0097e6;
                border-radius: 10px;
            }
            QLineEdit, QDateEdit, QTextEdit {
                padding: 6px; border: 1px solid #dcdde1; border-radius: 6px; background: #ffffff;
            }
            QPushButton { padding: 8px 12px; border-radius: 6px; color: white; background-color: #0097e6; }
            QPushButton:hover { background-color: #00a8ff; }
        """)

        self.btn_guardar.clicked.connect(self._submit)
        self.btn_cancelar.clicked.connect(self._cancel)

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
        if callable(self.on_submit):
            self.on_submit(datos)

    def _cancel(self):
        if callable(self.on_cancel):
            self.on_cancel()

    def limpiar(self):
        self.inp_nombre.clear()
        self.inp_desc.clear()
        self.inp_inicio.setDate(QDate.currentDate())
        self.inp_fin.setDate(QDate.currentDate())


# --------------------------- DETALLES OBRA ----------------------------
class DetallesObraWidget(QWidget):
    def __init__(self, id_obra, parent=None):
        super().__init__(parent)
        self.id_obra = id_obra
        self.setWindowTitle("Detalles de la Obra")
        self.resize(980, 720)
        self.setStyleSheet(self.estilos())

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # ===== Header =====
        self.info_frame = QFrame()
        self.info_frame.setFixedHeight(100)
        self.info_frame.setStyleSheet("""
            background-color: white;
            border-bottom: 2px solid #0097e6;
            padding: 10px 15px;
        """)
        self.info_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.info_hbox = QHBoxLayout(self.info_frame)
        self.info_hbox.setContentsMargins(20, 6, 20, 6)
        self.info_hbox.setSpacing(24)

        self.col_izq = QVBoxLayout()
        self.col_izq.setSpacing(6)

        self.lbl_titulo_obra = QLabel("—")
        self.lbl_titulo_obra.setStyleSheet(
            "font-size: 16pt; font-weight: 700; color: #2f3640; border:none; background:transparent; padding:0;"
        )
        self.lbl_titulo_obra.setWordWrap(False)
        self.lbl_titulo_obra.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lbl_titulo_obra.setMinimumHeight(24)

        self.lbl_direccion = QLabel("—")
        self.lbl_direccion.setStyleSheet(
            "font-size: 11pt; color: #273043; border:none; background:transparent; padding:0;"
        )
        self.lbl_direccion.setWordWrap(False)
        self.lbl_direccion.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lbl_direccion.setMinimumHeight(20)

        self.col_izq.addWidget(self.lbl_titulo_obra)
        self.col_izq.addWidget(self.lbl_direccion)

        self.col_der = QVBoxLayout()
        self.col_der.setSpacing(6)

        self.lbl_linea2 = QLabel("—")   # Estado • Inicio • Fin
        self.lbl_linea4 = QLabel("—")   # m² • Presupuesto

        self.col_der.addWidget(self.lbl_linea2)
        self.col_der.addWidget(self.lbl_linea4)

        self.info_hbox.addLayout(self.col_izq, 1)
        self.info_hbox.addLayout(self.col_der, 1)
        self.layout_principal.addWidget(self.info_frame)

        # ===== Scroll con etapas =====
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(20)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout_principal.addWidget(self.scroll_area)

        # Estructuras internas
        self.trabajos = []  # etapas
        self._tablas_por_trabajo = {}
        self._formularios_gasto_por_trabajo = {}
        self._formularios_editar_etapa = {}

        # Form crear etapa
        self.form_etapa = EtapaFormWidget(on_submit=self._crear_etapa_en_db,
                                          on_cancel=lambda: self._toggle_form_etapa(False))
        self.form_etapa.setVisible(False)
        self.scroll_layout.addWidget(self.form_etapa)

        # Barra inferior
        self.acciones_widget = QWidget()
        self.acciones_layout = QHBoxLayout(self.acciones_widget)
        self.acciones_layout.setContentsMargins(15, 10, 15, 10)
        self.btn_agregar_etapa_global = QPushButton("Agregar etapa")
        self.btn_agregar_etapa_global.setStyleSheet("padding: 10px; background-color: #0097e6; color: white; border-radius: 6px;")
        self.btn_agregar_etapa_global.clicked.connect(lambda: self._toggle_form_etapa(True))
        self.acciones_layout.addWidget(self.btn_agregar_etapa_global)
        self.acciones_layout.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("padding: 10px; background-color: #e84118; color: white; border-radius: 6px;")
        btn_cerrar.clicked.connect(self.close)
        self.acciones_layout.addWidget(btn_cerrar)
        self.layout_principal.addWidget(self.acciones_widget)

        # Carga inicial
        self._cargar_info_obra()
        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    # ===================== UTIL =====================
    def _fmt_date(self, d):
        if isinstance(d, date):
            return d.strftime("%d/%m/%Y")
        return d or ""

    def _fmt_money(self, n):
        try:
            return f"{float(n):,.0f} Gs.".replace(",", ".")
        except Exception:
            return str(n) if n is not None else ""

    def _parse_to_qdate(self, v):
        if isinstance(v, (date, datetime)):
            return QDate(v.year, v.month, v.day)
        if isinstance(v, str):
            qd = QDate.fromString(v, "yyyy-MM-dd")
            if qd.isValid():
                return qd
            qd = QDate.fromString(v, "dd/MM/yyyy")
            if qd.isValid():
                return qd
        return QDate.currentDate()

    # ===================== INFO OBRA =====================
    def _cargar_info_obra(self):
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion
                FROM obras
                WHERE id_obra = %s
            """, (self.id_obra,))
            row = cur.fetchone()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error de base de datos",
                                 f"No se pudo cargar la información general de la obra.\n\nDetalle: {e}")
            return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        if not row:
            self.lbl_titulo_obra.setText(f"Obra #{self.id_obra}")
            self.lbl_linea2.setText("No se encontró la obra en la base de datos.")
            self.lbl_direccion.setText("—")
            self.lbl_linea4.setText("—")
            return

        nombre, direccion, f_ini, f_fin, estado, m2, presupuesto, _ = row
        self.lbl_titulo_obra.setText(nombre or f"Obra #{self.id_obra}")
        self.lbl_direccion.setText(f"Dirección: {direccion}" if direccion else "Dirección: —")

        partes2 = []
        if estado: partes2.append(f"Estado: {estado}")
        if f_ini:  partes2.append(f"Inicio: {self._fmt_date(f_ini)}")
        if f_fin:  partes2.append(f"Fin: {self._fmt_date(f_fin)}")
        self.lbl_linea2.setText("  •  ".join(partes2) if partes2 else "—")

        extra = []
        if m2 is not None: extra.append(f"{float(m2):,.0f} m²".replace(",", "."))
        if presupuesto is not None: extra.append(f"Presupuesto: {self._fmt_money(presupuesto)}")
        self.lbl_linea4.setText("  •  ".join(extra) if extra else "—")

    # ===================== CARGA ETAPAS + GASTOS =====================
    def _cargar_etapas_y_gastos(self):
        try:
            conn = conexion(); cur = conn.cursor()

            # Etapas (tabla: trabajos)
            cur.execute("""
                SELECT id, nombre, descripcion, fecha_inicio, fecha_fin
                FROM trabajos
                WHERE obra_id = %s
                ORDER BY id ASC
            """, (self.id_obra,))
            filas = cur.fetchall()

            etapas = []
            for trabajo_id, nombre, desc, f_ini, f_fin in filas:
                # Gastos (tabla: gastos)
                cur.execute("""
                    SELECT id, tipo, concepto, cantidad, unidad, costo_unitario,
                           COALESCE(costo_total, cantidad * costo_unitario) AS costo_total,
                           to_char(fecha, 'DD/MM/YYYY') AS fecha
                    FROM gastos
                    WHERE trabajo_id = %s
                    ORDER BY fecha ASC, id ASC
                """, (trabajo_id,))
                gs = cur.fetchall()

                gastos = []
                for (g_id, tipo, concepto, cantidad, unidad, costo_unitario, costo_total, fecha_txt) in gs:
                    gastos.append({
                        "id": g_id,
                        "tipo": tipo or "",
                        "descripcion": concepto or "",
                        "cantidad": float(cantidad or 0),
                        "unidad": unidad or "",
                        "precio": float(costo_unitario or 0),
                        "total": float(costo_total or 0),
                        "fecha": fecha_txt or "",
                    })

                etapas.append({
                    "id": trabajo_id, "nombre": nombre, "descripcion": desc,
                    "fecha_inicio": f_ini, "fecha_fin": f_fin,
                    "gastos": gastos
                })

            self.trabajos = etapas

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error de base de datos",
                                 f"No se pudieron cargar etapas/consumos/gastos.\n\nDetalle: {e}")
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

    # ===================== UI SECCIONES =====================
    def _clear_sections_keep_form(self):
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(1)
            w = item.widget()
            if w: w.deleteLater()

    def _construir_secciones(self):
        self._clear_sections_keep_form()
        self._tablas_por_trabajo.clear()
        self._formularios_gasto_por_trabajo.clear()
        self._formularios_editar_etapa.clear()

        if not self.trabajos:
            self.form_etapa.setVisible(False)
            empty = QFrame()
            empty.setStyleSheet("background: white; border: 1px dashed #dcdde1; border-radius: 8px;")
            lay = QVBoxLayout(empty)
            lay.setContentsMargins(24, 24, 24, 24)

            lbl_msg = QLabel("Aún no hay etapas registradas en esta obra.")
            lbl_msg.setAlignment(Qt.AlignCenter)
            lbl_msg.setStyleSheet("color: #2f3640; font-size: 11.5pt; border:none; background:transparent; padding:0;")

            btn_crear_primera = QPushButton("Crear primera etapa")
            btn_crear_primera.setCursor(Qt.PointingHandCursor)
            btn_crear_primera.setStyleSheet("padding: 12px 16px; background-color: #0097e6; color: white; border-radius: 8px; font-weight: 600;")
            btn_crear_primera.clicked.connect(lambda: self._toggle_form_etapa(True))

            lay.addStretch()
            lay.addWidget(lbl_msg, alignment=Qt.AlignCenter)
            lay.addSpacing(8)
            lay.addWidget(btn_crear_primera, alignment=Qt.AlignCenter)
            lay.addStretch()

            self.scroll_layout.addWidget(empty)
            self.acciones_widget.setVisible(False)
            return
        else:
            self.acciones_widget.setVisible(True)

        for idx, etapa in enumerate(self.trabajos):
            contenedor = QWidget()
            vbox = QVBoxLayout(contenedor)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(8)

            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(8)

            titulo = QLabel(f"Etapa: {etapa['nombre']}")
            titulo.setStyleSheet("font-size: 12pt; font-weight: bold; border:none; background:transparent; padding:0;")
            header.addWidget(titulo)
            header.addStretch()

            btn_editar_etapa = QToolButton()
            btn_editar_etapa.setText("✎")
            btn_editar_etapa.setToolTip("Editar etapa")
            btn_editar_etapa.setCursor(Qt.PointingHandCursor)
            btn_editar_etapa.setStyleSheet("""
                QToolButton { font-size: 14pt; padding: 4px 8px; color: white; background: #f39c12; border-radius: 6px; }
                QToolButton:hover { background: #f1aa2f; }
            """)
            btn_editar_etapa.clicked.connect(lambda _, i=idx: self._editar_etapa(i))
            header.addWidget(btn_editar_etapa)

            btn_eliminar_etapa = QToolButton()
            btn_eliminar_etapa.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            btn_eliminar_etapa.setToolTip("Eliminar etapa")
            btn_eliminar_etapa.setCursor(Qt.PointingHandCursor)
            btn_eliminar_etapa.setStyleSheet("""
                QToolButton { padding: 6px 10px; color: white; background: #e84118; border-radius: 6px; }
                QToolButton:hover { background: #ee5735; }
            """)
            btn_eliminar_etapa.clicked.connect(lambda _, i=idx: self._eliminar_etapa(i))
            header.addWidget(btn_eliminar_etapa)

            btn_toggle_form = QPushButton("Agregar gasto")
            btn_toggle_form.setCursor(Qt.PointingHandCursor)
            btn_toggle_form.setStyleSheet("padding: 6px 10px; background-color: #0097e6; color: white; border-radius: 6px;")
            btn_toggle_form.clicked.connect(lambda _, i=idx: self._toggle_form_gasto(i))
            header.addWidget(btn_toggle_form)

            vbox.addLayout(header)

            form_edit = EtapaFormWidget(
                on_submit=lambda datos, i=idx: self._actualizar_etapa_en_db(i, datos),
                on_cancel=lambda i=idx: self._toggle_form_editar_etapa(i, False),
            )
            form_edit.setVisible(False)
            self._formularios_editar_etapa[idx] = form_edit
            vbox.addWidget(form_edit)

            form_gasto = GastoFormWidget(
                on_submit=lambda datos, i=idx: self._guardar_gasto(i, datos),
                on_cancel=lambda i=idx: self._ocultar_form_gasto(i),
            )
            form_gasto.setVisible(False)
            vbox.addWidget(form_gasto)
            self._formularios_gasto_por_trabajo[idx] = form_gasto

            tabla = QTableWidget()
            tabla.setColumnCount(7)
            tabla.setHorizontalHeaderLabels(["Tipo", "Descripción", "Cantidad", "Unidad", "Costo Unitario", "Total", "Fecha"])
            tabla.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            tabla.setMinimumHeight(120)
            tabla.horizontalHeader().setStretchLastSection(True)
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tabla.verticalHeader().setVisible(False)
            tabla.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            tabla.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #0097e6;
                    gridline-color: #0097e6;
                    font-size: 10pt;
                    color: black;
                }
                QHeaderView::section {
                    background-color: #0097e6;
                    color: white;
                    padding: 6px;
                    font-weight: bold;
                    border: none;
                }
                QTableWidget::item { padding: 6px; }
            """)
            self._popular_tabla(tabla, etapa["gastos"])
            self._fit_table_height(tabla, max_height=320)
            vbox.addWidget(tabla)
            self._tablas_por_trabajo[idx] = tabla

            self.scroll_layout.addWidget(contenedor)

    # ======= toggles =======
    def _toggle_form_etapa(self, visible: bool):
        self.form_etapa.setVisible(visible)
        if visible:
            self.form_etapa.inp_nombre.setFocus()

    def _toggle_form_editar_etapa(self, idx_trabajo: int, visible: bool):
        form = self._formularios_editar_etapa.get(idx_trabajo)
        if not form:
            return
        if visible:
            t = self.trabajos[idx_trabajo]
            form.inp_nombre.setText(t.get("nombre") or "")
            form.inp_desc.setPlainText(t.get("descripcion") or "")
            form.inp_inicio.setDate(self._parse_to_qdate(t.get("fecha_inicio")))
            form.inp_fin.setDate(self._parse_to_qdate(t.get("fecha_fin")))
            gform = self._formularios_gasto_por_trabajo.get(idx_trabajo)
            if gform and gform.isVisible():
                gform.setVisible(False)
        form.setVisible(visible)
        if visible:
            form.inp_nombre.setFocus()

    def _toggle_form_gasto(self, idx_trabajo: int):
        form = self._formularios_gasto_por_trabajo.get(idx_trabajo)
        if not form:
            return
        eform = self._formularios_editar_etapa.get(idx_trabajo)
        if eform and eform.isVisible():
            eform.setVisible(False)
        form.setVisible(not form.isVisible())
        if form.isVisible():
            form.input_desc.setFocus()

    def _ocultar_form_gasto(self, idx_trabajo: int):
        form = self._formularios_gasto_por_trabajo.get(idx_trabajo)
        if form:
            form.setVisible(False)
            form.limpiar()

    # ===================== helpers UI =====================
    def _popular_tabla(self, tabla, gastos):
        tabla.setRowCount(len(gastos))
        for fila, g in enumerate(gastos):
            tabla.setItem(fila, 0, QTableWidgetItem(g.get('tipo') or ""))
            tabla.setItem(fila, 1, QTableWidgetItem(g.get('descripcion') or ""))
            tabla.setItem(fila, 2, QTableWidgetItem(str(g.get('cantidad') or 0)))
            tabla.setItem(fila, 3, QTableWidgetItem(g.get('unidad') or ""))
            tabla.setItem(fila, 4, QTableWidgetItem(f"{float(g.get('precio') or 0):.2f}"))
            tabla.setItem(fila, 5, QTableWidgetItem(f"{float(g.get('total') or 0):.2f}"))
            tabla.setItem(fila, 6, QTableWidgetItem(g.get('fecha') or ""))
        tabla.resizeColumnsToContents()
        tabla.resizeRowsToContents()

    def _fit_table_height(self, tabla: QTableWidget, max_height=320):
        header_h = tabla.horizontalHeader().height() if tabla.horizontalHeader() else 24
        rows_h = sum([tabla.rowHeight(r) for r in range(tabla.rowCount())])
        frame = tabla.frameWidth() * 2
        padding = 12
        desired = header_h + rows_h + frame + padding
        tabla.setFixedHeight(min(max(desired, 120), max_height))

    # ===================== CRUD Etapas =====================
    def _crear_etapa_en_db(self, datos: dict):
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO trabajos (obra_id, nombre, descripcion, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, nombre
            """, (self.id_obra,
                  datos.get("nombre"),
                  datos.get("descripcion"),
                  datos.get("fecha_inicio"),
                  datos.get("fecha_fin")))
            cur.fetchone()
            conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc()
            QMessageBox.critical(self, "Error al crear etapa", f"{e}")
            return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        self._toggle_form_etapa(False)
        self.form_etapa.limpiar()
        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    def _actualizar_etapa_en_db(self, idx_trabajo: int, datos: dict):
        etapa_id = self.trabajos[idx_trabajo]["id"]
        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("""
                UPDATE trabajos
                SET nombre = %s,
                    descripcion = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s
                WHERE id = %s
            """, (datos.get("nombre"),
                  datos.get("descripcion"),
                  datos.get("fecha_inicio"),
                  datos.get("fecha_fin"),
                  etapa_id))
            conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc()
            QMessageBox.critical(self, "Error al actualizar etapa", f"{e}")
            return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        self._toggle_form_editar_etapa(idx_trabajo, False)
        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    def _eliminar_etapa(self, idx_trabajo: int):
        etapa_id = self.trabajos[idx_trabajo]["id"]
        ok = QMessageBox.question(self, "Eliminar etapa",
                                  "¿Seguro que querés eliminar esta etapa? Se eliminarán sus gastos.",
                                  QMessageBox.Yes | QMessageBox.No)
        if ok != QMessageBox.Yes:
            return

        try:
            conn = conexion(); cur = conn.cursor()
            cur.execute("DELETE FROM gastos WHERE trabajo_id = %s", (etapa_id,))
            cur.execute("DELETE FROM trabajos WHERE id = %s", (etapa_id,))
            conn.commit()
        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc()
            QMessageBox.critical(self, "Error al eliminar etapa", f"{e}")
            return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    def _editar_etapa(self, idx_trabajo: int):
        form = self._formularios_editar_etapa.get(idx_trabajo)
        if not form:
            return
        self._toggle_form_editar_etapa(idx_trabajo, not form.isVisible())

    # ===================== INSERT gasto =====================
    def _guardar_gasto(self, idx_trabajo: int, datos: dict):
        trabajo_id = self.trabajos[idx_trabajo]["id"]

        concepto = (datos.get("descripcion") or "").strip()
        tipo = (datos.get("tipo") or "").strip()
        unidad = (datos.get("unidad") or "").strip()
        cantidad = float(datos.get("cantidad") or 0)
        costo_unitario = float(datos.get("precio") or 0)

        # 'fecha' puede venir como QDate, date o string
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

        # Datos del consumo de stock (si aplica)
        usa_producto = bool(datos.get("usa_producto"))
        id_producto = datos.get("id_producto") if usa_producto else None

        if not concepto and not (usa_producto and id_producto):
            QMessageBox.warning(self, "Datos incompletos", "La descripción (concepto) es obligatoria.")
            return

        try:
            conn = conexion(); cur = conn.cursor()

            # 1) Insertar gasto contable
            if usa_producto and id_producto and not concepto:
                cur.execute("SELECT nombre FROM productos WHERE id_producto = %s", (id_producto,))
                row = cur.fetchone()
                if row:
                    concepto = f"Material: {row[0]}"

            cur.execute("""
                INSERT INTO gastos (trabajo_id, tipo, concepto, unidad, cantidad, costo_unitario, fecha)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (trabajo_id, tipo if tipo else ("Material" if usa_producto else ""),
                  concepto, unidad, cantidad, costo_unitario, fecha_val))
            cur.fetchone()

            # 2) Descontar stock si corresponde (CAST explícito para coincidir con la firma)
            if usa_producto and id_producto and cantidad > 0:
                cur.execute(
                    """
                    SELECT fn_mov(
                        %s::bigint,     -- id_producto
                        %s::smallint,   -- signo (-1 salida)
                        %s::numeric,    -- cantidad
                        %s::text,       -- origen
                        %s::bigint,     -- referencia_id (id_obra)
                        %s::text        -- nota
                    );
                    """,
                    (int(id_producto), -1, cantidad, 'obra', int(self.id_obra), 'Consumo en obra')
                )

            conn.commit()

        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            traceback.print_exc()
            QMessageBox.critical(self, "Error al guardar gasto", f"{e}")
            return
        finally:
            try: cur.close(); conn.close()
            except Exception: pass

        # Refrescar UI
        self._ocultar_form_gasto(idx_trabajo)
        self._cargar_etapas_y_gastos()
        self._construir_secciones()

    # ===================== estilos =====================
    def estilos(self):
        return """
        QWidget { font-family: 'Segoe UI'; font-size: 10.5pt; background-color: #f5f6fa; }
        QLabel  { color: #2f3640; }
        QPushButton { border: none; }
        """

if __name__ == "__main__":
    obra_id_arg = 1
    if len(sys.argv) >= 2:
        try:
            obra_id_arg = int(sys.argv[1])
        except Exception:
            pass

    app = QApplication(sys.argv)
    ui = DetallesObraWidget(id_obra=obra_id_arg)
    ui.show()
    sys.exit(app.exec())
