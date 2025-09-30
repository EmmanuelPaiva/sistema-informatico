# forms/weather_panel.py
import os
from datetime import datetime
from typing import Optional, Tuple, List

from PySide6.QtCore import Qt, QThread, Signal, QObject, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from services.weather import geocode_city, bundle, icon_url

# ---------------------- Networking para íconos ----------------------
class IconLoader(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nam = QNetworkAccessManager(parent)
        self._pending = {}  # reply -> (label, size)

    def set_icon(self, label: QLabel, url: str, size: int = 40):
        if not url:
            label.clear()
            return
        reply = self.nam.get(QNetworkRequest(QUrl(url)))
        self._pending[reply] = (label, size)
        reply.finished.connect(lambda r=reply: self._on_finished(r))

    def _on_finished(self, reply):
        label, size = self._pending.pop(reply, (None, 0))
        if not label:
            reply.deleteLater(); return
        data = reply.readAll()
        pix = QPixmap()
        if pix.loadFromData(bytes(data)):
            label.setPixmap(pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            label.clear()
        reply.deleteLater()


# ---------------------- Worker de clima ----------------------
class WeatherWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, *, city_name: Optional[str] = None,
                 coords: Optional[Tuple[float, float]] = None,
                 display_hint: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.city_name = city_name
        self.coords = coords
        self.display_hint = display_hint

    def run(self):
        try:
            if self.coords:
                lat, lon = self.coords
                display = self.display_hint or ""
            else:
                if not self.city_name:
                    raise ValueError("No se indicó ciudad ni coordenadas.")
                lat, lon, display = geocode_city(self.city_name)

            data = bundle(lat, lon, days=5, hours=12)
            cur = data.get("current", {})
            daily = data.get("daily", [])
            hourly = data.get("hourly", [])

            payload = {
                "city": display or cur.get("city") or (self.city_name or ""),
                "cielo": cur.get("cielo") or (cur.get("description") or "").capitalize(),
                "temp": cur.get("temp"),
                "icon_now": icon_url(cur.get("icon")) if cur.get("icon") else "",
                "wind": " ".join(
                    [f"{cur['wind_kmh']} km/h" if cur.get("wind_kmh") is not None else "",
                     cur.get("wind_dir") or ""]
                ).strip() or "—",
                "daily": [{
                    "date": d.get("date",""),
                    "tmin": d.get("temp_min"),
                    "tmax": d.get("temp_max"),
                    "icon": icon_url(d.get("icon")) if d.get("icon") else "",
                } for d in daily[:5]],
                "hourly": [{
                    "time": h.get("time",""),
                    "temp": h.get("temp"),
                    "icon": icon_url(h.get("icon")) if h.get("icon") else "",
                    "wind": (f"{h.get('wind_kmh')} km/h {h.get('wind_dir') or ''}").strip()
                            if h.get("wind_kmh") is not None else "—"
                } for h in hourly[:6]]
            }
            self.finished.emit(payload)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------- Helpers ----------------------
def _day_short_es(date_str: str) -> str:
    dias = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    try:
        y,m,d = map(int, date_str.split("-"))
        return dias[datetime(y,m,d).weekday()]
    except Exception:
        return "—"

def _time_hh00(txt: str) -> str:
    if not txt or ":" not in txt:
        return txt or "--:--"
    hh = txt.split(":")[0]
    return f"{hh}:00"

def _theme_for_cielo(cielo: str) -> str:
    """
    Devuelve un QSS con gradiente y colores según el cielo.
    - soleado: azules vivos
    - nuboso: teal/azul
    - nublado: grises
    """
    c = (cielo or "").lower()
    if "soleado" in c or "despejado" in c or "clear" in c:
        bg = "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4facfe, stop:1 #00f2fe);"
    elif "nuboso" in c or "cloud" in c:
        bg = "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #43cea2, stop:1 #185a9d);"
    else:  # nublado / lluvia / etc.
        bg = "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #bdc3c7, stop:1 #2c3e50);"
    return f"""
    #weatherPanel {{
        background: {bg}
        border: none;
        border-radius: 16px;
        color: #FFFFFF;
    }}
    #hourTime, #hourTemp, #cityLbl, #descLbl, #windLbl, #dayName, #dayTemp {{ color:#FFFFFF; }}
    #iconBubble {{
        background: rgba(255,255,255,0.28);
        border-radius: 999px;
    }}
    #dayCard {{
        background: rgba(255,255,255,0.18);
        border: none;
        border-radius: 12px;
    }}
    """

# ---------------------- Weather Panel (look app clima) ----------------------
class DashboardWeatherPanel(QFrame):
    """
    Clima actual + próximas horas (hora, icono redondo, temp) + próximos días (cards).
    Inline, sin marcos duplicados, con gradiente y altura contenida.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("weatherPanel")
        self.setFixedHeight(120)                 # evita alargar la ventana
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.loader = IconLoader(self)
        self._thread: Optional[WeatherWorker] = None

        root = QHBoxLayout(self)
        root.setContentsMargins(16,10,16,10)
        root.setSpacing(14)

        # ===== ACTUAL =====
        left = QHBoxLayout(); left.setSpacing(10)

        self.icon_now_bubble = QFrame(); self.icon_now_bubble.setObjectName("iconBubble")
        bubble_l = QHBoxLayout(self.icon_now_bubble); bubble_l.setContentsMargins(8,8,8,8)
        self.icon_now = QLabel(); self.icon_now.setFixedSize(32,32)
        bubble_l.addWidget(self.icon_now)

        info_col = QVBoxLayout(); info_col.setSpacing(0)
        self.city = QLabel("—"); self.city.setObjectName("cityLbl")
        self.city.setStyleSheet("font-size:15px; font-weight:700;")
        row_meta = QHBoxLayout(); row_meta.setSpacing(8)
        self.temp = QLabel("—°C"); self.temp.setObjectName("hourTemp")
        self.temp.setStyleSheet("font-size:24px; font-weight:800;")
        self.desc = QLabel("—"); self.desc.setObjectName("descLbl")
        self.wind = QLabel("—"); self.wind.setObjectName("windLbl")
        row_meta.addWidget(self.temp); row_meta.addWidget(self.desc); row_meta.addWidget(self.wind)
        info_col.addWidget(self.city); info_col.addLayout(row_meta)

        left.addWidget(self.icon_now_bubble)
        left.addLayout(info_col)
        left_box = QFrame(); left_box.setLayout(left)
        left_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        left_box.setStyleSheet("background: transparent;")  # sin marco

        root.addWidget(left_box)

        # separador visual (delgado y claro)
        sep1 = QFrame(); sep1.setFrameShape(QFrame.VLine); sep1.setStyleSheet("color: rgba(255,255,255,0.25);")
        root.addWidget(sep1)

        # ===== HORAS (sin marco: “al aire”) =====
        self.hours: List[Tuple[QLabel, QLabel, QLabel]] = []
        hours_wrap = QHBoxLayout(); hours_wrap.setSpacing(10)

        def make_hour_chip():
            col = QVBoxLayout(); col.setContentsMargins(0,0,0,0); col.setSpacing(0)
            t = QLabel("--:--"); t.setObjectName("hourTime")
            t.setAlignment(Qt.AlignCenter); t.setStyleSheet("font-size:11px;")
            bubble = QFrame(); bubble.setObjectName("iconBubble")
            bl = QHBoxLayout(bubble); bl.setContentsMargins(6,6,6,6)
            i = QLabel(); i.setFixedSize(22,22)
            bl.addWidget(i)
            v = QLabel("—°"); v.setObjectName("hourTemp")
            v.setAlignment(Qt.AlignCenter); v.setStyleSheet("font-weight:700; font-size:12px;")
            col.addWidget(t, 0, Qt.AlignHCenter); col.addWidget(bubble, 0, Qt.AlignHCenter); col.addWidget(v, 0, Qt.AlignHCenter)
            holder = QFrame(); holder.setLayout(col); holder.setStyleSheet("background: transparent;")
            holder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            return holder, t, i, v

        for _ in range(6):
            chip, t, i, v = make_hour_chip()
            hours_wrap.addWidget(chip)
            self.hours.append((t, i, v))

        hours_holder = QFrame(); hours_holder.setLayout(hours_wrap)
        hours_holder.setStyleSheet("background: transparent;")
        hours_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(hours_holder, 1)

        # separador
        sep2 = QFrame(); sep2.setFrameShape(QFrame.VLine); sep2.setStyleSheet("color: rgba(255,255,255,0.25);")
        root.addWidget(sep2)

        # ===== DÍAS (cards limpias, SIN marcos dobles) =====
        self.days: List[Tuple[QLabel, QLabel, QLabel]] = []
        days_wrap = QHBoxLayout(); days_wrap.setSpacing(8)

        def make_day_card():
            card = QFrame(); card.setObjectName("dayCard")
            lay = QVBoxLayout(card); lay.setContentsMargins(8,6,8,6); lay.setSpacing(2)
            d = QLabel("—"); d.setObjectName("dayName")
            d.setAlignment(Qt.AlignCenter); d.setStyleSheet("font-size:11px;")
            bubble = QFrame(); bubble.setObjectName("iconBubble")
            bl = QHBoxLayout(bubble); bl.setContentsMargins(6,6,6,6)
            i = QLabel(); i.setFixedSize(24,24)
            bl.addWidget(i)
            t = QLabel("—/—°"); t.setObjectName("dayTemp")
            t.setAlignment(Qt.AlignCenter); t.setStyleSheet("font-weight:600;")
            lay.addWidget(d); lay.addWidget(bubble); lay.addWidget(t)
            card.setFixedWidth(74)
            return card, d, i, t

        for _ in range(5):
            card, d, i, t = make_day_card()
            days_wrap.addWidget(card)
            self.days.append((d, i, t))

        days_holder = QFrame(); days_holder.setLayout(days_wrap)
        days_holder.setStyleSheet("background: transparent;")
        days_holder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        root.addWidget(days_holder)

        # Tema inicial (hasta que llegue la data)
        self.setStyleSheet(_theme_for_cielo("nuboso"))

    # ---------- API pública ----------
    def refresh_default_city(self):
        city = os.getenv("RODLER_WEATHER_CITY", "Caazapá, PY")
        self.refresh_city(city)

    def refresh_city(self, city_name: str):
        self._start_worker(city_name=city_name)

    def refresh_coords(self, lat: float, lon: float, display_hint: str = ""):
        self._start_worker(coords=(lat, lon), display_hint=display_hint)

    # ---------- Interno: worker ----------
    def _start_worker(self, *, city_name: Optional[str] = None,
                      coords: Optional[Tuple[float, float]] = None,
                      display_hint: Optional[str] = None):
        if getattr(self, "_thread", None) and self._thread.isRunning():
            return
        self._thread = WeatherWorker(city_name=city_name, coords=coords, display_hint=display_hint)
        self._thread.finished.connect(self._on_weather_ready)
        self._thread.error.connect(self._on_weather_error)
        self._thread.start()

    # ---------- Pintado ----------
    def _apply_theme(self, cielo: str):
        self.setStyleSheet(_theme_for_cielo(cielo))

    def _on_weather_ready(self, payload: dict):
        # Tema por cielo
        self._apply_theme(payload.get('cielo', ''))

        # Actual
        self.city.setText(str(payload.get('city','—')))
        tcur = payload.get('temp')
        self.temp.setText(f"{int(round(tcur))}°C" if tcur is not None else "—°C")
        self.desc.setText(str(payload.get('cielo','—')))
        self.wind.setText(str(payload.get('wind','—')))
        self.loader.set_icon(self.icon_now, payload.get('icon_now',''), 32)

        # Horas (hora, icono redondo, temp) — SIN marco
        hourly = payload.get('hourly', [])
        for idx, (t,i,v) in enumerate(self.hours):
            if idx < len(hourly):
                h = hourly[idx]
                t.setText(_time_hh00(h.get('time','--:--')))
                v.setText(f"{h.get('temp','-')}°")
                tip = h.get('wind','')
                t.setToolTip(tip); v.setToolTip(tip)
                self.loader.set_icon(i, h.get('icon',''), 22)
            else:
                t.setText("--:--"); v.setText("—°"); i.clear(); t.setToolTip(""); v.setToolTip("")

        # Días (cards limpias)
        daily = payload.get('daily', [])
        for k,(d,i,t) in enumerate(self.days):
            if k < len(daily):
                d.setText(_day_short_es(daily[k].get('date','')))
                t.setText(f"{daily[k].get('tmin','-')}/{daily[k].get('tmax','-')}°")
                self.loader.set_icon(i, daily[k].get('icon',''), 24)
            else:
                d.setText("—"); t.setText("—/—°"); i.clear()

    def _on_weather_error(self, msg: str):
        self._apply_theme("nublado")
        self.city.setText("Clima no disponible")
        self.temp.setText("—°C")
        self.desc.setText(msg)
        self.wind.setText("—")
        self.icon_now.clear()
        for t,i,v in self.hours:
            t.setText("--:--"); v.setText("—°"); i.clear(); t.setToolTip(""); v.setToolTip("")
        for d,i,t in self.days:
            d.setText("—"); t.setText("—/—°"); i.clear()
