# scripts/test_weather.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.weather import geocode_city, get_current_weather, get_forecast, icon_url

if __name__ == "__main__":
    lat, lon, name = geocode_city("Caazapá, PY")
    print("Ubicación:", name, lat, lon)

    cur = get_current_weather(lat, lon)
    print("Actual:", cur["temp"], "°C -", cur["description"], "-", icon_url(cur["icon"]))

    fc = get_forecast(lat, lon)[:4]
    for d in fc:
        print(d["date"], f"{d['temp_min']}–{d['temp_max']} °C", "-", d["description"], "-", icon_url(d["icon"]))
