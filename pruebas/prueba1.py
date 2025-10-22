import os
import requests

# === Directorio destino ===
dest_dir = os.path.join(os.path.dirname(__file__), "rodlerIcons")
os.makedirs(dest_dir, exist_ok=True)

# === URLs de los iconos Lucide ===
icons = {
    "eye.svg": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/eye.svg",
    "eye-off.svg": "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/eye-off.svg"
}

# === Descarga ===
for name, url in icons.items():
    path = os.path.join(dest_dir, name)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"✅ {name} descargado correctamente en {path}")
    except Exception as e:
        print(f"❌ Error al descargar {name}: {e}")

print("\nTodos los iconos fueron procesados.")
