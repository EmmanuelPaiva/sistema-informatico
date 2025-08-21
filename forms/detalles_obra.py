import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QScrollArea, QFrame, QHBoxLayout, QSizePolicy, QHeaderView,
    QMessageBox, QLineEdit, QDateEdit, QTextEdit, QFormLayout, QAbstractScrollArea
)
import traceback
from datetime import date

from db.conexion import conexion
from forms.AgregarGasto import GastoFormWidget   # tu formulario inline para gastos


# -------- Formulario inline para crear/editar ETAPA (trabajo) ----------
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
            "fecha_inicio": self.inp_inicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.inp_fin.date().toString("yyyy-MM-dd"),
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
    """
    Usa:
      - public.obras     (id_obra, nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion)
      - public.trabajos  (id, obra_id, nombre, descripcion, fecha_inicio, fecha_fin, costo_total)
      - public.gastos    (id, trabajo_id, concepto, tipo, unidad, cantidad, costo_unitario, costo_total (STORED), fecha)
    """
    def __init__(self, id_obra, parent=None):
        super().__init__(parent)
        self.id_obra = id_obra
        self.setWindowTitle("Detalles de la Obra")
        self.resize(980, 720)
        self.setStyleSheet(self.estilos())

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # ===== Header (info general) =====
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            background-color: white;
            border-bottom: 2px solid #0097e6;
            padding: 15px;
        """)
        self.info_layout = QVBoxLayout(self.info_frame)
        self.info_layout.setContentsMargins(20, 10, 20, 10)

        # Labels del header
        self.lbl_titulo_obra = QLabel("")   # Nombre de la obra
        self.lbl_titulo_obra.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.lbl_linea2 = QLabel("")        # Estado | Fechas
        self.lbl_linea3 = QLabel("")        # Dirección
        self.lbl_linea4 = QLabel("")        # Metros | Presupuesto
        for lbl in (self.lbl_titulo_obra, self.lbl_linea2, self.lbl_linea3, self.lbl_linea4):
            lbl.setWordWrap(True)
            self.info_layout.addWidget(lbl)

        self.layout_principal.addWidget(self.info_frame)

        # ===== Scroll con etapas (trabajos) =====
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
        self.trabajos = []  # [{ "id": int, "nombre": str, "gastos": [...] }]
        self._tablas_por_trabajo = {}
        self._formularios_gasto_por_trabajo = {}

        # Formulario global (único) para crear etapa al tope del scroll
        self.form_etapa = EtapaFormWidget(on_submit=self._crear_etapa_en_db,
                                          on_cancel=lambda: self._toggle_form_etapa(False))
        self.form_etapa.setVisible(False)
        self.scroll_layout.addWidget(self.form_etapa)

        # Cargar DB y armar UI
        self._cargar_info_obra()          # <<<<<< CARGA INFO GENERAL
        self._cargar_trabajos_y_gastos()
        self._construir_secciones()

        # Acciones inferiores
        acciones = QHBoxLayout()
        acciones.setContentsMargins(15, 10, 15, 10)
        self.btn_agregar_etapa_global = QPushButton("Agregar etapa")
        self.btn_agregar_etapa_global.setStyleSheet("padding: 10px; background-color: #0097e6; color: white; border-radius: 6px;")
        self.btn_agregar_etapa_global.clicked.connect(lambda: self._toggle_form_etapa(True))
        acciones.addWidget(self.btn_agregar_etapa_global)
        acciones.addStretch()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("padding: 10px; background-color: #e84118; color: white; border-radius: 6px;")
        btn_cerrar.clicked.connect(self.close)
        acciones.addWidget(btn_cerrar)
        self.layout_principal.addLayout(acciones)

    # ===================== UTILIDADES =====================
    def _fmt_date(self, d):
        if isinstance(d, date):
            return d.strftime("%d/%m/%Y")
        return d or ""

    def _fmt_money(self, n):
        try:
            return f"{float(n):,.0f} Gs.".replace(",", ".")
        except Exception:
            return str(n) if n is not None else ""

    # ===================== CARGA INFO GENERAL =====================
    def _cargar_info_obra(self):
        """Carga y renderiza la cabecera con datos reales de public.obras."""
        try:
            conn = conexion()
            cur = conn.cursor()
            cur.execute("""
                SELECT nombre, direccion, fecha_inicio, fecha_fin, estado, metros_cuadrados, presupuesto_total, descripcion
                FROM public.obras
                WHERE id_obra = %s
            """, (self.id_obra,))
            row = cur.fetchone()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error de base de datos",
                                 f"No se pudo cargar la información general de la obra.\n\nDetalle: {e}")
            return
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

        if not row:
            # No existe la obra (o id incorrecto)
            self.lbl_titulo_obra.setText(f"Obra #{self.id_obra}")
            self.lbl_linea2.setText("No se encontró la obra en la base de datos.")
            self.lbl_linea3.setText("")
            self.lbl_linea4.setText("")
            return

        nombre, direccion, f_ini, f_fin, estado, m2, presupuesto, descripcion = row

        # Render del header
        self.lbl_titulo_obra.setText(nombre or f"Obra #{self.id_obra}")

        fechas_txt = f"Inicio: {self._fmt_date(f_ini)}"
        if f_fin:
            fechas_txt += f"  •  Fin: {self._fmt_date(f_fin)}"
        estado_txt = f"Estado: {estado}" if estado else ""
        self.lbl_linea2.setText("  •  ".join([t for t in (estado_txt, fechas_txt) if t]))

        self.lbl_linea3.setText(f"Dirección: {direccion}" if direccion else "Dirección: —")

        extra = []
        if m2 is not None:
            extra.append(f"{float(m2):,.0f} m²".replace(",", "."))
        if presupuesto is not None:
            extra.append(f"Presupuesto: {self._fmt_money(presupuesto)}")
        self.lbl_linea4.setText("  •  ".join(extra))

    # ===================== CARGA TRABAJOS + GASTOS =====================
    def _cargar_trabajos_y_gastos(self):
        try:
            conn = conexion()
            cur = conn.cursor()

            cur.execute("""
                SELECT id, nombre
                FROM public.trabajos
                WHERE obra_id = %s
                ORDER BY id ASC
            """, (self.id_obra,))
            trabajos_rows = cur.fetchall()

            trabajos = []
            for trabajo_id, nombre in trabajos_rows:
                cur.execute("""
                    SELECT tipo, concepto, cantidad, unidad, costo_unitario,
                           costo_total, TO_CHAR(fecha, 'DD/MM/YYYY') AS fecha
                    FROM public.gastos
                    WHERE trabajo_id = %s
                    ORDER BY fecha ASC, id ASC
                """, (trabajo_id,))
                gastos_rows = cur.fetchall()

                gastos = []
                for (tipo, concepto, cantidad, unidad, costo_unitario, costo_total, fecha_txt) in gastos_rows:
                    gastos.append({
                        "tipo": tipo,
                        "descripcion": concepto,
                        "cantidad": float(cantidad) if cantidad is not None else 0.0,
                        "unidad": unidad,
                        "precio": float(costo_unitario) if costo_unitario is not None else 0.0,
                        "total": float(costo_total) if costo_total is not None else 0.0,
                        "fecha": fecha_txt,
                    })
                trabajos.append({"id": trabajo_id, "nombre": nombre, "gastos": gastos})

            self.trabajos = trabajos

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error de base de datos",
                                 f"No se pudieron cargar etapas/gastos.\n\nDetalle: {e}")
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    # ===================== UI SECCIONES =====================
    def _clear_sections_keep_form(self):
        # Mantener self.form_etapa (índice 0 en el scroll)
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(1)
            w = item.widget()
            if w:
                w.deleteLater()

    def _construir_secciones(self):
        self._clear_sections_keep_form()
        self._tablas_por_trabajo.clear()
        self._formularios_gasto_por_trabajo.clear()

        if not self.trabajos:
            empty = QFrame()
            empty.setStyleSheet("background: white; border: 1px dashed #dcdde1; border-radius: 8px;")
            lay = QVBoxLayout(empty)
            lay.setContentsMargins(16, 16, 16, 16)
            msg = QLabel("Esta obra no tiene etapas aún.\nCreá la primera etapa para comenzar a registrar gastos.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #2f3640;")
            lay.addWidget(msg)

            btn_crear_primera = QPushButton("Crear primera etapa")
            btn_crear_primera.setCursor(Qt.PointingHandCursor)
            btn_crear_primera.setStyleSheet("padding: 10px; background-color: #0097e6; color: white; border-radius: 6px;")
            btn_crear_primera.clicked.connect(lambda: self._toggle_form_etapa(True))
            lay.addWidget(btn_crear_primera, alignment=Qt.AlignCenter)

            self.scroll_layout.addWidget(empty)
            return

        for idx, trabajo in enumerate(self.trabajos):
            contenedor = QWidget()
            vbox = QVBoxLayout(contenedor)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(8)

            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(8)

            titulo = QLabel(f"Etapa: {trabajo['nombre']}")
            titulo.setStyleSheet("font-size: 12pt; font-weight: bold;")
            header.addWidget(titulo)
            header.addStretch()

            btn_toggle_form = QPushButton("Agregar gasto")
            btn_toggle_form.setCursor(Qt.PointingHandCursor)
            btn_toggle_form.setStyleSheet("padding: 6px 10px; background-color: #0097e6; color: white; border-radius: 6px;")
            btn_toggle_form.clicked.connect(lambda _, i=idx: self._toggle_form_gasto(i))
            header.addWidget(btn_toggle_form)
            vbox.addLayout(header)

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
            self._popular_tabla(tabla, trabajo["gastos"])
            self._fit_table_height(tabla, max_height=320)
            vbox.addWidget(tabla)
            self._tablas_por_trabajo[idx] = tabla

            self.scroll_layout.addWidget(contenedor)

    # ======= toggle formularios =======
    def _toggle_form_etapa(self, visible: bool):
        self.form_etapa.setVisible(visible)
        if visible:
            self.form_etapa.inp_nombre.setFocus()

    def _toggle_form_gasto(self, idx_trabajo: int):
        form = self._formularios_gasto_por_trabajo.get(idx_trabajo)
        if not form:
            return
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

    # ===================== INSERTs =====================
    def _crear_etapa_en_db(self, datos: dict):
        try:
            conn = conexion()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO public.trabajos (obra_id, nombre, descripcion, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, nombre
            """, (self.id_obra, datos.get("nombre"), datos.get("descripcion"),
                  datos.get("fecha_inicio") or None, datos.get("fecha_fin") or None))
            _row = cur.fetchone()
            conn.commit()
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            traceback.print_exc()
            QMessageBox.critical(self, "Error al crear etapa", f"{e}")
            return
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

        # Ocultar/limpiar form y recargar UI
        self._toggle_form_etapa(False)
        self.form_etapa.limpiar()
        self._cargar_trabajos_y_gastos()
        self._construir_secciones()

    def _guardar_gasto(self, idx_trabajo: int, datos: dict):
        trabajo_id = self.trabajos[idx_trabajo]["id"]

        concepto = (datos.get("descripcion") or "").strip()
        tipo = (datos.get("tipo") or "").strip()
        unidad = (datos.get("unidad") or "").strip()
        cantidad = float(datos.get("cantidad") or 0)
        costo_unitario = float(datos.get("precio") or 0)
        fecha_str = datos.get("fecha") or ""  # "DD/MM/YYYY"

        if not concepto:
            QMessageBox.warning(self, "Datos incompletos", "La descripción (concepto) es obligatoria.")
            return

        try:
            conn = conexion()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO public.gastos
                    (trabajo_id, concepto, tipo, unidad, cantidad, costo_unitario, fecha)
                VALUES
                    (%s, %s, %s, %s, %s, %s, to_date(%s, 'DD/MM/YYYY'))
                RETURNING id, costo_total
            """, (trabajo_id, concepto, tipo, unidad, cantidad, costo_unitario, fecha_str))
            row = cur.fetchone()
            conn.commit()

            nuevo = {
                "tipo": tipo,
                "descripcion": concepto,
                "cantidad": cantidad,
                "unidad": unidad,
                "precio": costo_unitario,
                "total": float(row[1]) if row and row[1] is not None else round(cantidad * costo_unitario, 2),
                "fecha": fecha_str,
            }
            self.trabajos[idx_trabajo]["gastos"].append(nuevo)

            tabla = self._tablas_por_trabajo.get(idx_trabajo)
            if tabla:
                self._popular_tabla(tabla, self.trabajos[idx_trabajo]["gastos"])
                self._fit_table_height(tabla, max_height=320)

            self._ocultar_form_gasto(idx_trabajo)

        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            traceback.print_exc()
            QMessageBox.critical(self, "Error al guardar gasto", f"{e}")
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

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
