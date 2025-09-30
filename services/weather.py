# services/weather.py
from __future__ import annotations
import os, time
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter
import requests
from dotenv import load_dotenv

# === Config ===
load_dotenv()  # Carga variables del .env
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
CACHE_TTL = 600  # 10 minutos

# === Cachés simples en memoria ===
_current_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_forecast_cache: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}

def _get_api_key() -> str:
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        raise RuntimeError("Falta OPENWEATHER_API_KEY en .env")
    return key

def _cache_get(cache: dict, key: str):
    item = cache.get(key)
    if not item:
        return None
    expires_at, data = item
    if time.time() > expires_at:
        cache.pop(key, None)
        return None
    return data

def _cache_set(cache: dict, key: str, data, ttl: int = CACHE_TTL):
    cache[key] = (time.time() + ttl, data)

# ----------------------------
# Helpers de viento y "cielo"
# ----------------------------
def wind_to_kmh(mps: Optional[float]) -> Optional[float]:
    """Convierte m/s a km/h con 1 decimal."""
    if mps is None:
        return None
    return round(mps * 3.6, 1)

def deg_to_compass(deg: Optional[float]) -> Optional[str]:
    """Convierte grados (0..360) a punto cardinal (N, NE, E, ...)."""
    if deg is None:
        return None
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    i = int((deg/22.5) + 0.5) % 16
    return dirs[i]

def cielo_categoria(main: Optional[str], cloud_pct: Optional[float]) -> str:
    """
    Normaliza el estado del cielo a: 'soleado', 'nuboso' o 'nublado'.
    Usa 'main' (Clear/Clouds/Rain/...) y porcentaje de nubes si está disponible.
    """
    m = (main or "").lower()
    c = cloud_pct if cloud_pct is not None else -1

    if m == "clear":
        return "soleado"

    if m == "clouds":
        if 0 <= c <= 40:
            return "nuboso"
        return "nublado"

    if m in ("rain", "drizzle", "thunderstorm", "snow", "mist", "fog", "haze", "smoke"):
        return "nublado"

    return "nuboso"

# ----------------------------
# Geocoding (ciudad -> lat/lon)
# ----------------------------
def geocode_city(nombre_ciudad: str, *, limit: int = 1) -> Tuple[float, float, str]:
    """
    Devuelve (lat, lon, nombre_normalizado). Lanza excepción si no encuentra.
    """
    params = {"q": nombre_ciudad, "limit": limit, "appid": _get_api_key()}
    r = requests.get(GEO_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError(f"No se encontraron coordenadas para: {nombre_ciudad}")
    item = data[0]
    lat = float(item["lat"])
    lon = float(item["lon"])
    name = item.get("name") or nombre_ciudad
    country = item.get("country") or ""
    state = item.get("state")
    display = f"{name}, {country}" + (f" ({state})" if state else "")
    return lat, lon, display

# ----------------------------
# Clima actual
# ----------------------------
def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Clima actual normalizado.
    Campos:
      - temp, feels_like, humidity
      - wind_speed (m/s), wind_kmh, wind_dir
      - cloud_pct
      - description (texto), icon
      - cielo (soleado/nuboso/nublado)
      - dt, city
    """
    key = f"{lat:.4f},{lon:.4f}"
    cached = _cache_get(_current_cache, key)
    if cached:
        return cached

    params = {"lat": lat, "lon": lon, "units": "metric", "lang": "es", "appid": _get_api_key()}
    r = requests.get(CURRENT_URL, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()

    weather = (j.get("weather") or [{}])[0]
    main = j.get("main", {})
    wind = j.get("wind", {})
    city = j.get("name", "")
    clouds_pct = j.get("clouds", {}).get("all")

    data = {
        "temp": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "wind_speed": wind.get("speed"),
        "wind_kmh": wind_to_kmh(wind.get("speed")),
        "wind_dir": deg_to_compass(wind.get("deg")),
        "cloud_pct": clouds_pct,
        "description": weather.get("description"),
        "icon": weather.get("icon"),
        "cielo": cielo_categoria(weather.get("main"), clouds_pct),
        "dt": j.get("dt"),
        "city": city,
    }
    _cache_set(_current_cache, key, data)
    return data

# ----------------------------
# Forecast (crudo y resúmenes)
# ----------------------------
def _fetch_forecast_items(lat: float, lon: float) -> List[Dict[str, Any]]:
    """
    Devuelve la lista cruda de items del endpoint /forecast (cada 3 horas).
    """
    key = f"{lat:.4f},{lon:.4f}"
    cached = _cache_get(_forecast_cache, key)
    if cached:
        return cached

    params = {"lat": lat, "lon": lon, "units": "metric", "lang": "es", "appid": _get_api_key()}
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    items = j.get("list", [])
    _cache_set(_forecast_cache, key, items)
    return items

def summarize_daily(forecast_items: List[Dict[str, Any]], days: int = 5) -> List[Dict[str, Any]]:
    """
    Agrupa por día y calcula min/max reales del día, cielo representativo e icono cercano a 12:00.
    Devuelve lista con dicts:
      { date: 'YYYY-MM-DD', temp_min: float, temp_max: float, cielo: str, icon: str }
    """
    por_dia = defaultdict(list)
    for it in forecast_items:
        dt_txt = it.get("dt_txt")  # 'YYYY-MM-DD HH:MM:SS'
        if not dt_txt:
            continue
        day = dt_txt.split(" ")[0]
        por_dia[day].append(it)

    out: List[Dict[str, Any]] = []
    for day in sorted(por_dia.keys())[:days]:
        bloque = por_dia[day]
        mins: List[float] = []
        maxs: List[float] = []
        categorias: List[str] = []
        cerca_mediodia: List[Tuple[int, Optional[str]]] = []

        for it in bloque:
            main = it.get("main", {})
            weather = (it.get("weather") or [{}])[0]
            clouds = it.get("clouds", {}).get("all")
            if "temp_min" in main:
                mins.append(main["temp_min"])
            if "temp_max" in main:
                maxs.append(main["temp_max"])
            categorias.append(cielo_categoria(weather.get("main"), clouds))

            dt_txt = it.get("dt_txt")
            if dt_txt:
                hour = int(dt_txt.split(" ")[1][:2])
                score = abs(12 - hour)
                cerca_mediodia.append((score, weather.get("icon")))

        temp_min = round(min(mins), 1) if mins else None
        temp_max = round(max(maxs), 1) if maxs else None
        cat = Counter(categorias).most_common(1)[0][0] if categorias else "nuboso"
        icon = sorted(cerca_mediodia)[0][1] if cerca_mediodia else None

        out.append({
            "date": day,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "cielo": cat,
            "icon": icon,
        })
    return out

def summarize_hourly(forecast_items: List[Dict[str, Any]], hours: int = 12) -> List[Dict[str, Any]]:
    """
    Muestra las próximas 'hours' horas (en bloques de 3h).
    Devuelve lista con dicts:
      { time: 'HH:MM', temp: float, cielo: str, icon: str, wind_kmh: float, wind_dir: str }
    """
    n = max(1, hours // 3)
    slice_items = forecast_items[:n]

    out: List[Dict[str, Any]] = []
    for it in slice_items:
        dt_txt = it.get("dt_txt")  # 'YYYY-MM-DD HH:MM:SS'
        main = it.get("main", {})
        weather = (it.get("weather") or [{}])[0]
        clouds = it.get("clouds", {}).get("all")
        wind = it.get("wind", {})
        hora = dt_txt.split(" ")[1][:5] if dt_txt else ""

        out.append({
            "time": hora,
            "temp": round(main.get("temp"), 1) if main.get("temp") is not None else None,
            "cielo": cielo_categoria(weather.get("main"), clouds),
            "icon": weather.get("icon"),
            "wind_kmh": wind_to_kmh(wind.get("speed")),
            "wind_dir": deg_to_compass(wind.get("deg")),
        })
    return out

def get_forecast(lat: float, lon: float, *, days: int = 5) -> List[Dict[str, Any]]:
    """
    Pronóstico diario (min/max reales) para 'days' próximos días.
    Formato: [{date, temp_min, temp_max, cielo, icon}, ...]
    """
    items = _fetch_forecast_items(lat, lon)
    return summarize_daily(items, days=days)

def get_hourly(lat: float, lon: float, *, hours: int = 12) -> List[Dict[str, Any]]:
    """
    Pronóstico por horas (en bloques de 3h) para las próximas 'hours' horas.
    Formato: [{time, temp, cielo, icon, wind_kmh, wind_dir}, ...]
    """
    items = _fetch_forecast_items(lat, lon)
    return summarize_hourly(items, hours=hours)

def bundle(lat: float, lon: float, *, days: int = 5, hours: int = 12) -> Dict[str, Any]:
    """
    Conveniencia: trae todo lo que necesita la UI de un golpe.
    Devuelve:
      {"current": {...}, "daily": [...], "hourly": [...]}
    """
    cur = get_current_weather(lat, lon)
    items = _fetch_forecast_items(lat, lon)
    daily = summarize_daily(items, days=days)
    hourly = summarize_hourly(items, hours=hours)
    return {"current": cur, "daily": daily, "hourly": hourly}

# ----------------------------
# Íconos
# ----------------------------
def icon_url(icon_code: str, size: str = "@2x") -> str:
    return f"https://openweathermap.org/img/wn/{icon_code}{size}.png"
