# -*- coding: utf-8 -*-
import os, sys, secrets
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from PySide6.QtCore import (
    QCoreApplication, QMetaObject, QSize, Qt, QEvent, QTimer, QRect,
    QThread, Signal, Slot
)
from PySide6.QtGui import QColor, QIcon, QPixmap, QPalette, QPainter, QFont, QPen, QCloseEvent
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStackedWidget, QStatusBar, QToolButton,
    QVBoxLayout, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtSvg import QSvgRenderer

# ========= RUTAS ABSOLUTAS EXACTAS =========
ASSET_DIR = r"c:\Users\mauri\OneDrive\Desktop\SISTEMA-INFORMATICO\rodlerIcons"
IMG1 = os.path.join(ASSET_DIR, "img1.png")
IMG2 = os.path.join(ASSET_DIR, "img2.png")
IMG3 = os.path.join(ASSET_DIR, "img3.png")
EYE_ON = os.path.join(ASSET_DIR, "eye.svg")
EYE_OFF = os.path.join(ASSET_DIR, "eye-off.svg")

def _path_for_qss(p: str) -> str:
    return os.path.abspath(p).replace("\\", "/")

# ---- autenticación ----
authenticate = None
_import_error = None
try:
    from Rodler_auth import authenticate as _auth_fn2
    authenticate = _auth_fn2
    _import_error = None
except Exception as e2:
    _import_error = e2

# ---- importa MenuPrincipal (QWidget) ----
import importlib
from PySide6.QtWidgets import QWidget
MenuPrincipal = None
_mod_errs = []
for modname in ('MenuPrincipal', 'main.MenuPrincipal'):
    try:
        _mod = importlib.import_module(modname)
        MenuPrincipal = getattr(_mod, 'MenuPrincipal', None)
        if MenuPrincipal is None or not isinstance(MenuPrincipal, type) or not issubclass(MenuPrincipal, QWidget):
            _mod_errs.append(f"{modname} no expone QWidget 'MenuPrincipal'")
            MenuPrincipal = None
            continue
        break
    except Exception as _e:
        _mod_errs.append(f"{modname}: {_e}")
        MenuPrincipal = None

if MenuPrincipal is None:
    import traceback
    print("=== ERROR importando MenuPrincipal ===")
    for line in _mod_errs:
        print(" -", line)
    traceback.print_exc()
    print("======================================")

from db.conexion import get_conn

# ===================== Helpers DB =====================
def _db_get_user_by_username(username_lc: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, username, is_active, locked_until
            FROM rodler_auth.users
            WHERE LOWER(username) = LOWER(%s)
            LIMIT 1
        """, (username_lc,))
        row = cur.fetchone()
        if not row:
            return None

        def _get(r, key, idx):
            try:
                if hasattr(r, "keys"):
                    return r.get(key)
            except Exception:
                pass
            try:
                return r[idx]
            except Exception:
                return None

        return {
            "id": _get(row, "id", 0),
            "username": _get(row, "username", 1),
            "is_active": _get(row, "is_active", 2),
            "locked_until": _get(row, "locked_until", 3),
        }
    finally:
        conn.close()

def _db_record_login_success(user_id: int, ttl: str = '12 hours') -> str:
    token = secrets.token_hex(16)
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT rodler_auth.record_login_success(%s, %s, %s)", (user_id, token, ttl))
        conn.commit()
        return token
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def _db_record_login_failure(user_id: int, threshold: int = 5, lock_interval: str = '15 minutes'):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT rodler_auth.record_login_failure(%s, %s, %s)", (user_id, threshold, lock_interval))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# ============================== UI helpers ==============================
def _svg_to_icon(svg_path: str, w: int = 22, h: int = 22) -> QIcon:
    try:
        if not svg_path or not os.path.exists(svg_path):
            return QIcon()
        renderer = QSvgRenderer(svg_path)
        pm = QPixmap(w, h)
        pm.fill(Qt.transparent)
        painter = QPainter(pm)
        renderer.render(painter)
        painter.end()
        return QIcon(pm)
    except Exception:
        return QIcon()

def _icon(path_or_name: str) -> QIcon:
    p = path_or_name
    if p and p.lower().endswith(".svg") and os.path.exists(p):
        return _svg_to_icon(p, 22, 22)
    return QIcon(p) if p and os.path.exists(p) else QIcon()

def _is_dark_theme(app: QApplication) -> bool:
    for key in ("rodler.dark", "dark", "theme", "rodler.theme"):
        val = app.property(key)
        if isinstance(val, bool):
            return val
        if isinstance(val, str) and val.lower() in ("dark", "oscuro", "darkmode", "night"):
            return True
    col = app.palette().color(QPalette.Window)
    luma = 0.2126 * col.redF() + 0.7152 * col.greenF() + 0.0722 * col.blueF()
    return luma < 0.5

# ============================== Overlay con spinner ==============================
class BusyOverlay(QWidget):
    def __init__(self, parent=None, bg_alpha=160, pen_width=6, arc_span_deg=110, fps=60):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self._bg_alpha = int(bg_alpha)
        self._pen_w = pen_width
        self._span = arc_span_deg
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.setInterval(int(1000 / max(1, fps)))
        self._timer.timeout.connect(self._tick)
        self.hide()

    def start(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show(); self.raise_(); self._timer.start()

    def stop(self):
        self._timer.stop(); self.hide()

    def _tick(self):
        self._angle = (self._angle + 6) % 360
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        p.fillRect(self.rect(), QColor(0, 0, 0, self._bg_alpha))
        r = min(self.width(), self.height()) // 10
        r = max(24, min(r, 64))
        cx, cy = self.width() // 2, self.height() // 2
        rect = QRect(cx - r, cy - r, 2 * r, 2 * r)
        pen = QPen(QColor(255, 255, 255, 220)); pen.setWidth(self._pen_w); pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        start = int(self._angle * 16); span = int(self._span * 16)
        p.drawArc(rect, -start, -span)

# ============================== NUEVA UI ==============================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setMinimumSize(QSize(1200, 720))

        self.centralwidget = QWidget(MainWindow)
        self.centralLayout = QVBoxLayout(self.centralwidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.setSpacing(0)

        self.stack = QStackedWidget(self.centralwidget)
        self.centralLayout.addWidget(self.stack)
        MainWindow.setCentralWidget(self.centralwidget)

        # ========== PAGE LOGIN ==========
        self.pageLogin = QWidget()
        self.pageLogin.setObjectName("pageLogin")
        self.stack.addWidget(self.pageLogin)

        # Capas absolutas en pageLogin
        self.bg = QLabel(self.pageLogin)
        self.bg.setObjectName("bg"); self.bg.setAlignment(Qt.AlignCenter)

        self.overlay = QLabel(self.pageLogin)
        self.overlay.setObjectName("overlay")

        # Contenido centrado (título + card)
        self.content = QWidget(self.pageLogin)
        self.content.setObjectName("content")
        layout_outer = QVBoxLayout(self.content)
        layout_outer.setContentsMargins(60, 40, 60, 40)
        layout_outer.setSpacing(20)

        self.lblLogoText = QLabel("RODLERE", self.content)
        self.lblLogoText.setObjectName("title")
        self.lblLogoText.setAlignment(Qt.AlignCenter)
        self.lblLogoText.setContentsMargins(0, 0, 0, 0)
        layout_outer.addWidget(self.lblLogoText)

        layout_outer.addSpacing(120)

        # ---- Card login ----
        self.cardLogin = QFrame(self.content)
        self.cardLogin.setObjectName("cardLogin")
        self.cardLogin.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.cardLogin.setMinimumWidth(360)
        self.cardLogin.setMaximumWidth(640)
        card_layout = QVBoxLayout(self.cardLogin)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(10)

        # Usuario
        self.lblEmail = QLabel("Usuario", self.cardLogin)
        self.lineIdent = QLineEdit(self.cardLogin)
        self.lineIdent.setPlaceholderText("usuario")

        # Contraseña + botón ojo
        self.lblPass = QLabel("Contraseña", self.cardLogin)
        hlPass = QHBoxLayout()
        self.linePass = QLineEdit(self.cardLogin)
        self.linePass.setPlaceholderText("••••••••")
        self.linePass.setEchoMode(QLineEdit.Password)
        self.btnTogglePass = QToolButton(self.cardLogin)
        self.btnTogglePass.setObjectName("btnTogglePass")
        self.btnTogglePass.setCheckable(True)
        self.btnTogglePass.setCursor(Qt.PointingHandCursor)
        if os.path.exists(EYE_ON):
            self.btnTogglePass.setIcon(_icon(EYE_ON))
        hlPass.addWidget(self.linePass)
        hlPass.addWidget(self.btnTogglePass)

        # Mensaje de error (inline, debajo del input)
        self.lblError = QLabel("", self.cardLogin)
        self.lblError.setObjectName("errorLabel")
        self.lblError.setWordWrap(True)
        self.lblError.setVisible(False)

        # Botón ingresar (CREAR ANTES DE AGREGAR)
        self.btnLogin = QPushButton("Ingresar", self.cardLogin)
        self.btnLogin.setObjectName("btnLogin")
        self.btnLogin.setCursor(Qt.PointingHandCursor)

        # Agregar widgets al layout del card
        card_layout.addWidget(self.lblEmail)
        card_layout.addWidget(self.lineIdent)
        card_layout.addWidget(self.lblPass)
        card_layout.addLayout(hlPass)
        card_layout.addWidget(self.lblError)
        card_layout.addWidget(self.btnLogin)

        layout_outer.addWidget(self.cardLogin, alignment=Qt.AlignHCenter)
        layout_outer.addStretch()

        shadow = QGraphicsDropShadowEffect(self.cardLogin)
        shadow.setBlurRadius(28); shadow.setOffset(0, 14); shadow.setColor(QColor(0,0,0,90))
        self.cardLogin.setGraphicsEffect(shadow)

        self.menuBar = QMenuBar(MainWindow); MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow); MainWindow.setStatusBar(self.statusBar)

        # ========== PAGE APP ==========
        self.pageApp = QWidget()
        self.vlApp = QVBoxLayout(self.pageApp)
        self.lblAppPlaceholder = QLabel(self.pageApp); self.lblAppPlaceholder.setAlignment(Qt.AlignCenter)
        self.lblAppPlaceholder.setText("Contenido principal (no usado aún)")
        self.vlApp.addWidget(self.lblAppPlaceholder)
        self.stack.addWidget(self.pageApp)

        self.stack.setCurrentWidget(self.pageLogin)
        self.btnLogin.setDefault(True)

        self.lblEmail.setBuddy(self.lineIdent)
        self.lblPass.setBuddy(self.linePass)
        QWidget.setTabOrder(self.lineIdent, self.linePass)
        QWidget.setTabOrder(self.linePass, self.btnLogin)

        self.btnTogglePass.toggled.connect(MainWindow._toggle_password)
        self.btnLogin.clicked.connect(MainWindow._on_login_clicked)

        MainWindow._apply_theme_decor()

        self.pageLogin.installEventFilter(MainWindow)
        self.stack.currentChanged.connect(MainWindow._on_stack_changed)

        

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Rodler — Sistema", None))
        self.lblEmail.setText(QCoreApplication.translate("MainWindow", u"Usuario", None))
        self.lineIdent.setPlaceholderText(QCoreApplication.translate("MainWindow", u"usuario", None))
        self.lblPass.setText(QCoreApplication.translate("MainWindow", u"Contraseña", None))
        self.linePass.setPlaceholderText(QCoreApplication.translate("MainWindow", u"••••••••", None))
        self.btnTogglePass.setToolTip(QCoreApplication.translate("MainWindow", u"Mostrar/Ocultar", None))
        self.btnLogin.setText(QCoreApplication.translate("MainWindow", u"Ingresar", None))

# ============================== Worker: flujo completo ==============================
class LoginFlowWorker(QThread):
    done = Signal(object, object, object, object)  # ok, payload, error, message

    def __init__(self, usuario_norm: str, clave: str, parent=None):
        super().__init__(parent)
        self.usuario_norm = usuario_norm
        self.clave = clave

    def run(self):
        try:
            ok, payload = authenticate(self.usuario_norm, self.clave)
        except Exception as e:
            self.done.emit(None, None, e, str(e))
            return

        if not isinstance(payload, dict):
            payload = {"message": str(payload)}

        if not ok:
            reason = payload.get("message") if isinstance(payload, dict) else str(payload)
            try:
                u = _db_get_user_by_username(self.usuario_norm)
                if u and u.get("id") is not None:
                    _db_record_login_failure(u["id"], threshold=5, lock_interval='15 minutes')
            except Exception as e:
                reason = f"{reason}\n(Nota: no se pudo registrar el fallo: {e})"
            self.done.emit(False, payload, None, reason or "Usuario o contraseña inválidos")
            return

        try:
            user_obj = payload.get("user") if isinstance(payload, dict) else None
            user_id = None
            username_payload = None
            if user_obj:
                user_id = user_obj.get("id")
                username_payload = user_obj.get("username")

            if user_id is None:
                user_row = _db_get_user_by_username(self.usuario_norm)
                if user_row is None:
                    self.done.emit(False, payload, None, "Autenticado, pero el usuario no existe en BD.")
                    return
                user_id = user_row["id"]
                if username_payload is None:
                    username_payload = user_row["username"]

            token = _db_record_login_success(user_id, ttl='12 hours')

            if "session" not in payload or not isinstance(payload.get("session"), dict):
                payload["session"] = {}
            payload["session"]["token"] = token
            payload["user"] = payload.get("user", {"id": user_id, "username": username_payload or self.usuario_norm})

            self.done.emit(True, payload, None, None)
        except Exception as e:
            self.done.emit(False, payload, e, f"Login verificado pero NO se pudo registrar la sesión en BD: {e}")

# ============================== Ventana principal ==============================
class LoginMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._pix = [QPixmap(p) for p in (IMG1, IMG2, IMG3) if os.path.exists(p)]
        self._pix = [pm for pm in self._pix if not pm.isNull()]
        self._idx = 0

        app = QApplication.instance()
        self._app_styles_backup = app.styleSheet()
        self._palette_backup = app.palette()

        self.loading = BusyOverlay(self, bg_alpha=170)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.login_payload = None
        self.appWidget = None

        self._timer = QTimer(self)
        self._timer.setInterval(6000)
        self._timer.timeout.connect(self._next)
        self._timer.start()

        self._login_thread: LoginFlowWorker | None = None

        if authenticate is None:
            pass

        self._install_login_styles()
        self._sync_login_layers()

    # ---------- Estilos blindados para el login ----------
    def _install_login_styles(self):
        css = """
        QWidget#pageLogin, QWidget#content { background: transparent; border: none; }
        QLabel#bg { background: transparent; border: none; border-image: none; }
        QLabel#overlay { border: none; border-image: none; }
        QLabel#title { margin: 0px; padding: 0px; }
        """
        self.ui.pageLogin.setStyleSheet(css)
        self.ui.bg.setAttribute(Qt.WA_StyledBackground, True)
        self.ui.overlay.setAttribute(Qt.WA_StyledBackground, True)
        self.ui.content.setAttribute(Qt.WA_StyledBackground, False)

    # ---------- UTILIDAD ----------
    def _sync_login_layers(self):
        if self.ui.stack.currentWidget() != self.ui.pageLogin:
            return
        r = self.ui.pageLogin.rect()
        for w in (self.ui.bg, self.ui.overlay, self.ui.content):
            w.setGeometry(r)
        self._apply_cover()
        self._scale_title()
        if self.loading.isVisible():
            self.loading.setGeometry(self.rect())
            self.loading.raise_()

    # ---------- Eventos ----------
    def eventFilter(self, obj, ev):
        if obj is self.ui.pageLogin and ev.type() in (QEvent.Show, QEvent.Resize):
            self._sync_login_layers()
        return super().eventFilter(obj, ev)

    def _on_stack_changed(self, idx: int):
        if self.ui.stack.widget(idx) == self.ui.pageLogin:
            self._clear_errors()
            self._sync_login_layers()
            self._timer.start()
        else:
            self._timer.stop()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._sync_login_layers()

    def closeEvent(self, event: QCloseEvent):
        try: self._timer.stop()
        except Exception: pass
        try:
            if self._login_thread and self._login_thread.isRunning():
                self._login_thread.done.disconnect()
                self._login_thread.requestInterruption()
                self._login_thread.quit()
                self._login_thread.wait(1000)
        except Exception: pass
        try: self.loading.stop()
        except Exception: pass
        return super().closeEvent(event)

    # Tema + estilos + overlay
    def _apply_theme_decor(self):
        is_dark = _is_dark_theme(QApplication.instance())
        card_bg = "#111318" if is_dark else "#FFFFFF"
        text_color = "#EDEFF3" if is_dark else "#0d1b2a"
        border_col = "#2A2F3A" if is_dark else "rgba(0,0,0,0.12)"
        primary = "#3ea8f5"

        self.ui.overlay.setStyleSheet("background: rgba(0,0,0,128); border:none;")
        self.ui.content.setStyleSheet(f"""
#title {{
  color: #FFFFFF; font-weight: 900; letter-spacing: 8px;
  font-size: 160px; margin: 0px; padding: 0px;
}}
#cardLogin {{
  background:{card_bg};
  border:1px solid {border_col};
  border-radius:16px;
}}
QLabel {{
  color:{text_color};
  font-size:18px; font-weight:600;
}}
QLineEdit {{
  border:1px solid {border_col};
  border-radius:10px;
  padding:14px 14px;
  background:{card_bg};
  color:{text_color};
  font-size:17px;
}}
QLineEdit:focus {{ border:1px solid {primary}; }}
QToolButton#btnTogglePass {{
  border:1px solid {border_col}; border-left:none; border-radius:10px;
  padding:8px 10px; background:rgba(0,0,0,0.05);
}}
QToolButton#btnTogglePass:checked {{ background:rgba(0,0,0,0.10); }}
QPushButton#btnLogin {{
  background:{primary}; color:#0d1b2a; border:none; border-radius:10px;
  padding:16px 20px; font-weight:700; font-size:20px;
}}
#errorLabel {{
  color: #b00020;      /* rojo legible */
  font-size: 15px;     /* “no muy chico, no muy grande” */
  margin-top: 6px;     /* pequeño margen con respecto al input */
}}
""")

        self.ui.btnTogglePass.setIcon(_icon(EYE_ON) if os.path.exists(EYE_ON) else QIcon())
        self.ui.btnTogglePass.setIconSize(QSize(22, 22))

        self.ui.bg.raise_(); self.ui.overlay.raise_(); self.ui.content.raise_()
        if self.loading.isVisible():
            self.loading.raise_()

        self._sync_login_layers()

    # Escala título + responsive
    def _scale_title(self):
        w, h = self.width(), self.height()
        font: QFont = self.ui.lblLogoText.font()
        size = int(w * 0.20)
        size = min(size, int(h * 0.22))
        size = max(72, min(size, 280))
        font.setPointSize(size)
        self.ui.lblLogoText.setFont(font)

        max_w = min(640, int(w * 0.9))
        min_w = min(420, max(320, int(w * 0.5)))
        self.ui.cardLogin.setMaximumWidth(max_w)
        self.ui.cardLogin.setMinimumWidth(min_w)

        outer: QVBoxLayout = self.ui.content.layout()
        if h < 700:
            outer.setContentsMargins(24, 16, 24, 16); outer.setSpacing(12)
        else:
            outer.setContentsMargins(60, 40, 60, 40); outer.setSpacing(20)

    # Carrusel
    def _next(self):
        if not self._pix:
            return
        self._idx = (self._idx + 1) % len(self._pix)
        if self.ui.stack.currentWidget() == self.ui.pageLogin:
            self._apply_cover()

    # Cover al QLabel de fondo
    def _apply_cover(self):
        if not getattr(self, "_pix", None):
            return
        rect = self.ui.bg.contentsRect()
        tw, th = rect.width(), rect.height()
        if tw < 10 or th < 10:
            return
        pm = self._pix[self._idx]
        srcw, srch = pm.width(), pm.height()
        scale = max(tw / srcw, th / srch)
        sw, sh = int(srcw * scale + 0.5), int(srch * scale + 0.5)
        scaled = pm.scaled(sw, sh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        x = max(0, (scaled.width() - tw) // 2)
        y = max(0, (scaled.height() - th) // 2)
        final = scaled.copy(x, y, tw, th)
        self.ui.bg.setPixmap(final)
        self.ui.bg.raise_(); self.ui.overlay.raise_(); self.ui.content.raise_()
        if self.loading.isVisible():
            self.loading.raise_()

    def _clear_errors(self):
        try:
            self.ui.lblError.setVisible(False)
            self.ui.lblError.setText("")
            self.ui.linePass.setStyleSheet("")
            self.ui.lineIdent.setStyleSheet("")
        except Exception:
            pass

    def _show_invalid(self, message: str):
        self.ui.linePass.setStyleSheet("border:1px solid #b00020;")
        self.ui.lblError.setText(message or "Credenciales inválidas")
        self.ui.lblError.setVisible(True)

    # ---- UI helpers (lógica de mostrar/ocultar contraseña) ----
    def _toggle_password(self, checked: bool):
        self.ui.linePass.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        path = EYE_OFF if checked else EYE_ON
        self.ui.btnTogglePass.setIcon(_icon(path) if os.path.exists(path) else QIcon())

    # ========== handler de logout ==========
    def _on_logout(self):
        # Detener hilos/overlays y limpiar
        try: self.loading.stop()
        except Exception: pass

        if self.appWidget is not None:
            try: self.appWidget.logoutRequested.disconnect(self._on_logout)
            except Exception: pass
            self.appWidget.setParent(None); self.appWidget.deleteLater(); self.appWidget = None

        # Restaurar estilos globales por si MenuPrincipal los cambió
        app = QApplication.instance()
        app.setStyleSheet(self._app_styles_backup)
        app.setPalette(self._palette_backup)

        # Volver al login limpio
        self.ui.stack.setCurrentWidget(self.ui.pageLogin)
        self.ui.linePass.clear(); self.ui.lineIdent.clear()
        self._clear_errors()
        self.ui.lineIdent.setFocus()
        self._install_login_styles()
        self._apply_theme_decor()
        self._timer.start()
        self._sync_login_layers()

    # ---- MenuPrincipal en pageApp ----
    def _show_app(self, session: dict):
        if MenuPrincipal is None:
            self._show_invalid("No se pudo cargar la aplicación principal (MenuPrincipal).")
            return

        layout = self.ui.pageApp.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.pageApp); layout.setContentsMargins(0, 0, 0, 0)

        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None); w.deleteLater()

        self.appWidget = MenuPrincipal(session=session, parent=self.ui.pageApp)
        try: self.appWidget.logoutRequested.connect(self._on_logout)
        except Exception: pass

        layout.addWidget(self.appWidget)
        self.ui.stack.setCurrentWidget(self.ui.pageApp)
        self._timer.stop()

    # -------- Click de login (100% asíncrono) --------
    def _on_login_clicked(self):
        usuario = (self.ui.lineIdent.text() or "").strip()
        clave   = (self.ui.linePass.text()  or "").strip()

        self._clear_errors()  # no mostrar nada al clickear, solo limpiar

        if not usuario or not clave:
            self._show_invalid("Completá usuario y contraseña.")
            return

        if authenticate is None:
            self._show_invalid(f"Falta 'Rodler_auth.authenticate' o falló la importación: {_import_error}")
            return

        # Arranca overlay
        self.loading.start()
        self.ui.btnLogin.setEnabled(False)

        # Asegurar que no quede un hilo anterior
        if self._login_thread and self._login_thread.isRunning():
            try: self._login_thread.done.disconnect(self._on_auth_done)
            except Exception: pass
            self._login_thread.requestInterruption(); self._login_thread.quit(); self._login_thread.wait(500)

        usuario_norm = usuario.lower()
        self._login_thread = LoginFlowWorker(usuario_norm, clave, parent=self)
        self._login_thread.done.connect(self._on_auth_done)
        self._login_thread.start()

    @Slot(object, object, object, object)
    def _on_auth_done(self, ok, payload, error, message):
        try: self.ui.btnLogin.setEnabled(True)
        except Exception: pass

        try:
            if error is not None or not ok:
                # Mostrar solo error visual, sin textos intermedios
                self._show_invalid(message or (payload.get("message") if isinstance(payload, dict) else "Credenciales inválidas"))
                return

            # Éxito: payload ya viene completo (con token y user) desde el worker
            self.login_payload = payload

            # Detener overlay ANTES de construir la app para que no “congele” al crear widgets pesados
            try: self.loading.stop()
            except Exception: pass

            self._show_app(payload)
        finally:
            # Asegurar overlay apagado pase lo que pase
            try: self.loading.stop()
            except Exception: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setProperty("rodler.dark", True)  # opcional: tema oscuro
    win = LoginMainWindow()
    win.show()
    sys.exit(app.exec())
  