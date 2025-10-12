import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget, QStatusBar, QToolButton,
    QVBoxLayout, QWidget, QGraphicsDropShadowEffect
)

# ---- importa tu autenticación (Argon2) ----
authenticate = None
_import_error = None
e1 = None 
try:
    # fallback: paquete/carpeta rodler_auth con __init__.py que expone authenticate
    from Rodler_auth import authenticate as _auth_fn2
    authenticate = _auth_fn2
    _import_error = None
except Exception as e2:
    _import_error = (e1, e2)

# ---- importa tu MenuPrincipal (como QWidget) ----
MenuPrincipal = None
try:
    from MenuPrincipal import MenuPrincipal as _MP
    MenuPrincipal = _MP
except Exception as e:
    import traceback
    print("\n=== ERROR importando MenuPrincipal ===")
    print(e)
    traceback.print_exc()
    print("======================================\n")


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setMinimumSize(QSize(980, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralLayout = QVBoxLayout(self.centralwidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget(self.centralwidget)
        self.pageLogin = QWidget()
        self.hlRoot = QHBoxLayout(self.pageLogin)
        self.hlRoot.setSpacing(0)
        self.hlRoot.setContentsMargins(0, 0, 0, 0)

        # ========== PANEL IZQUIERDO ==========
        self.panelBrand = QFrame(self.pageLogin)
        self.panelBrand.setObjectName("panelBrand")
        self.panelBrand.setMinimumSize(QSize(420, 0))
        self.panelBrand.setStyleSheet(u"""
#panelBrand{
  background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #3ea8f5, stop:1 #2f9bee);
}
#brandTitle{ font-size:36px; font-weight:800; color:#ffffff; }
#brandText{ font-size:13px; color:rgba(255,255,255,0.90); }
#lblLogoText{ color:#ffffff; font-weight:800; font-size:20px; }
#lblLogoIcon{ color:#ffffff; font-size:24px; }
        """)
        self.vlBrand = QVBoxLayout(self.panelBrand)
        self.vlBrand.setContentsMargins(36, 36, 36, 36)

        self.hlLogo = QHBoxLayout()
        self.lblLogoIcon = QLabel(self.panelBrand); self.lblLogoIcon.setObjectName(u"lblLogoIcon")
        self.lblLogoText = QLabel(self.panelBrand); self.lblLogoText.setObjectName(u"lblLogoText")
        self.hlLogo.addWidget(self.lblLogoIcon); self.hlLogo.addWidget(self.lblLogoText)
        self.hlLogo.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.vlBrand.addLayout(self.hlLogo)

        self.brandTitle = QLabel(self.panelBrand); self.brandTitle.setObjectName(u"brandTitle")
        self.brandTitle.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.vlBrand.addWidget(self.brandTitle)

        self.brandText = QLabel(self.panelBrand); self.brandText.setObjectName(u"brandText")
        self.brandText.setWordWrap(True); self.brandText.setMaximumWidth(340)
        self.vlBrand.addWidget(self.brandText)
        self.vlBrand.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.hlRoot.addWidget(self.panelBrand)

        # ========== LADO DERECHO / CARD LOGIN ==========
        self.rightArea = QWidget(self.pageLogin)
        self.vlRight = QVBoxLayout(self.rightArea); self.vlRight.setContentsMargins(48, 48, 48, 48)
        self.vlRight.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.hlCardCenter = QHBoxLayout()
        self.hlCardCenter.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.cardLogin = QFrame(self.rightArea); self.cardLogin.setObjectName(u"cardLogin")
        self.cardLogin.setMinimumSize(QSize(460, 0)); self.cardLogin.setMaximumSize(QSize(520, 16777215))
        self.cardLogin.setFrameShape(QFrame.StyledPanel)
        self.cardLogin.setStyleSheet(u"""
#cardLogin{
  background-color:#ffffff; border:1px solid #dfe7f5; border-radius:16px;
}
QLabel#lblEmail, QLabel#lblPass{ color:#0d1b2a; font-weight:600; }
QLineEdit{
  border:1px solid #dfe7f5; border-radius:10px; padding:8px 10px; background:#ffffff;
  selection-background-color:#3ea8f5; selection-color:#0d1b2a;
}
QLineEdit:focus{ border:1px solid #3ea8f5; }
QToolButton#btnTogglePass{
  border:1px solid #dfe7f5; border-left:none; border-radius:10px; padding:6px 10px; background:#f7fbff;
}
QToolButton#btnTogglePass:checked{ background:#eef7ff; }
QPushButton#btnLogin{
  background-color:#3ea8f5; color:#0d1b2a; border:none; padding:12px 18px; border-radius:10px; font-weight:700;
}
QPushButton#btnLogin:hover{ background-color:#3798dc; }
QPushButton#btnLogin:pressed{ background-color:#2f86c4; }
QFrame#barEstado{
  background-color:#fff6e0; border:1px solid #f1d097; border-radius:10px; color:#5c3b00; padding:6px;
}
        """)
        shadow = QGraphicsDropShadowEffect(self.cardLogin)
        shadow.setBlurRadius(24); shadow.setOffset(0, 8); shadow.setColor(QColor(0, 0, 0, 35))
        self.cardLogin.setGraphicsEffect(shadow)

        self.vlCard = QVBoxLayout(self.cardLogin); self.vlCard.setContentsMargins(24, 24, 24, 24); self.vlCard.setSpacing(10)

        self.lblEmail = QLabel(self.cardLogin); self.lblEmail.setObjectName(u"lblEmail")
        self.vlCard.addWidget(self.lblEmail)
        self.lineIdent = QLineEdit(self.cardLogin); self.lineIdent.setObjectName(u"lineIdent"); self.lineIdent.setClearButtonEnabled(True)
        self.vlCard.addWidget(self.lineIdent)

        self.lblPass = QLabel(self.cardLogin); self.lblPass.setObjectName(u"lblPass")
        self.vlCard.addWidget(self.lblPass)
        self.hlPass = QHBoxLayout()
        self.linePass = QLineEdit(self.cardLogin); self.linePass.setObjectName(u"linePass"); self.linePass.setEchoMode(QLineEdit.Password)
        self.hlPass.addWidget(self.linePass)
        self.btnTogglePass = QToolButton(self.cardLogin); self.btnTogglePass.setObjectName(u"btnTogglePass")
        self.btnTogglePass.setCheckable(True); self.btnTogglePass.setCursor(Qt.PointingHandCursor)
        self.hlPass.addWidget(self.btnTogglePass)
        self.vlCard.addLayout(self.hlPass)

        # Estado
        self.barEstado = QFrame(self.cardLogin); self.barEstado.setObjectName(u"barEstado"); self.barEstado.setVisible(False)
        self.hlEstado = QHBoxLayout(self.barEstado); self.hlEstado.setContentsMargins(8, 6, 8, 6)
        self.iconEstado = QLabel(self.barEstado); self.iconEstado.setObjectName(u"iconEstado")
        self.lblEstado = QLabel(self.barEstado); self.lblEstado.setObjectName(u"lblEstado")
        self.hlEstado.addWidget(self.iconEstado); self.hlEstado.addWidget(self.lblEstado)
        self.vlCard.addWidget(self.barEstado)

        self.btnLogin = QPushButton(self.cardLogin); self.btnLogin.setObjectName(u"btnLogin")
        self.btnLogin.setCursor(Qt.PointingHandCursor)
        self.vlCard.addWidget(self.btnLogin)

        self.hlCardCenter.addWidget(self.cardLogin)
        self.hlCardCenter.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.vlRight.addLayout(self.hlCardCenter)
        self.vlRight.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.hlRoot.addWidget(self.rightArea)
        self.stack.addWidget(self.pageLogin)

        # ========== PAGE APP ==========
        self.pageApp = QWidget()
        self.vlApp = QVBoxLayout(self.pageApp)
        self.lblAppPlaceholder = QLabel(self.pageApp); self.lblAppPlaceholder.setAlignment(Qt.AlignCenter)
        self.lblAppPlaceholder.setStyleSheet(u"color:#6b7a89;")
        self.vlApp.addWidget(self.lblAppPlaceholder)
        self.stack.addWidget(self.pageApp)

        self.centralLayout.addWidget(self.stack)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow); MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow); MainWindow.setStatusBar(self.statusBar)

        self.lblEmail.setBuddy(self.lineIdent)
        self.lblPass.setBuddy(self.linePass)
        QWidget.setTabOrder(self.lineIdent, self.linePass)
        QWidget.setTabOrder(self.linePass, self.btnLogin)

        self.retranslateUi(MainWindow)
        self.stack.setCurrentIndex(0)
        self.btnLogin.setDefault(True)

        # Conexiones a métodos del MainWindow (lógica)
        self.btnTogglePass.toggled.connect(MainWindow._toggle_password)
        self.btnLogin.clicked.connect(MainWindow._on_login_clicked)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Rodler — Sistema", None))
        self.lblLogoIcon.setText(QCoreApplication.translate("MainWindow", u"\u25cf", None))
        self.lblLogoText.setText(QCoreApplication.translate("MainWindow", u"RODLER", None))
        self.brandTitle.setText(QCoreApplication.translate("MainWindow", u"Bienvenido", None))
        self.brandText.setText(QCoreApplication.translate("MainWindow", u"Accede con tus credenciales para ingresar al sistema.", None))
        self.lblEmail.setText(QCoreApplication.translate("MainWindow", u"Usuario", None))
        self.lineIdent.setPlaceholderText(QCoreApplication.translate("MainWindow", u"usuario", None))
        self.lblPass.setText(QCoreApplication.translate("MainWindow", u"Contraseña", None))
        self.linePass.setPlaceholderText(QCoreApplication.translate("MainWindow", u"••••••••", None))
        self.btnTogglePass.setToolTip(QCoreApplication.translate("MainWindow", u"Mostrar/Ocultar", None))
        self.btnTogglePass.setText(QCoreApplication.translate("MainWindow", u"Mostrar", None))
        self.iconEstado.setText(QCoreApplication.translate("MainWindow", u"\u26a0", None))
        self.lblEstado.setText(QCoreApplication.translate("MainWindow", u"Mensaje de estado…", None))
        self.btnLogin.setText(QCoreApplication.translate("MainWindow", u"Ingresar", None))
        self.lblAppPlaceholder.setText(QCoreApplication.translate("MainWindow", u"Contenido principal (no usado aún)", None))


class LoginMainWindow(QMainWindow):
    """Ventana con login como página; al validar embebe MenuPrincipal en pageApp."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.login_payload = None
        self.appWidget = None  # referencia al MenuPrincipal embebido

        # Si no se pudo importar authenticate, muestro aviso temprano
        if authenticate is None:
            self._set_status(
                "No se encontró la función de autenticación.\n"
                "Asegúrate de tener 'auth.py' con 'authenticate(usuario, clave)'.",
                ok=False, visible=True
            )

    # ---- UI helpers ----
    def _toggle_password(self, checked: bool):
        self.ui.linePass.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.ui.btnTogglePass.setText("Ocultar" if checked else "Mostrar")

    def _set_status(self, msg: str, ok: bool = False, visible: bool = True):
        self.ui.barEstado.setVisible(visible)
        if not visible:
            return
        self.ui.lblEstado.setText(msg)
        if ok:
            self.ui.barEstado.setStyleSheet("""
            #barEstado{ background-color:#e9f8ef; border:1px solid #8ed1a6; border-radius:10px; color:#0b4d2b; padding:6px; }
            """)
            self.ui.iconEstado.setText("✓")
        else:
            self.ui.barEstado.setStyleSheet("""
            #barEstado{ background-color:#fff6e0; border:1px solid #f1d097; border-radius:10px; color:#5c3b00; padding:6px; }
            """)
            self.ui.iconEstado.setText("⚠")

    # ========== NUEVO: handler de logout ==========
    def _on_logout(self):
        """Vuelve a la pantalla de login y limpia el contenedor de la app."""
        if self.appWidget is not None:
            try:
                self.appWidget.logoutRequested.disconnect(self._on_logout)
            except Exception:
                pass
            self.appWidget.setParent(None)
            self.appWidget.deleteLater()
            self.appWidget = None

        self.ui.stack.setCurrentWidget(self.ui.pageLogin)
        self.ui.linePass.clear()
        self.ui.lineIdent.setFocus()
        self._set_status("Sesión finalizada.", ok=True, visible=True)

    # ---- Monta MenuPrincipal en pageApp y navega ----
    def _show_app(self, session: dict):
        if MenuPrincipal is None:
            self._set_status("No se pudo cargar la aplicación principal (MenuPrincipal).", ok=False, visible=True)
            return

        layout = self.ui.pageApp.layout()
        if layout is None:
            layout = QVBoxLayout(self.ui.pageApp)
            layout.setContentsMargins(0, 0, 0, 0)

        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        self.appWidget = MenuPrincipal(session=session, parent=self.ui.pageApp)
        try:
            self.appWidget.logoutRequested.connect(self._on_logout)
        except Exception:
            pass

        layout.addWidget(self.appWidget)
        self.ui.stack.setCurrentWidget(self.ui.pageApp)

    # ---- Lógica de login ----
    def _on_login_clicked(self):
        usuario = (self.ui.lineIdent.text() or "").strip()
        clave   = (self.ui.linePass.text()  or "").strip()

        if not usuario or not clave:
            self._set_status("Completá usuario y contraseña.", ok=False, visible=True)
            return

        if authenticate is None:
            # si falló la importación, muestro el detalle
            self._set_status(f"Falta auth.py (authenticate) o falló la importación: {_import_error}", ok=False, visible=True)
            return

        self.ui.btnLogin.setEnabled(False)
        self._set_status("Validando credenciales…", ok=False, visible=True)
        QApplication.processEvents()

        # Normaliza username a lowercase (acorde al trigger normalize_username)
        usuario_norm = usuario.lower()

        try:
            ok, payload = authenticate(usuario_norm, clave)
        except Exception as e:
            # Mensaje amigable si el SQL interno usa 'rodler_auth.usuarios'
            msg = str(e)
            if "rodler_auth.usuarios" in msg or "relation \"rodler_auth.usuarios\"" in msg:
                msg += "\n\nSugerencia: en tu authenticate(), cambia 'rodler_auth.usuarios' por 'rodler_auth.users'."
            self.ui.btnLogin.setEnabled(True)
            self._set_status(f"Error de conexión/autenticación: {msg}", ok=False, visible=True)
            return

        self.ui.btnLogin.setEnabled(True)

        if not ok:
            # payload suele traer el texto del motivo
            self._set_status(str(payload), ok=False, visible=True)  
            return

        self.login_payload = payload
        u = payload.get("user", {}).get("username", usuario_norm)
        roles = payload.get("roles", [])
        self._set_status(f"Bienvenido, {u}. Roles: {', '.join(roles) if roles else '—'}", ok=True, visible=True)
        self._show_app(payload)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginMainWindow()
    win.show()
    sys.exit(app.exec())
