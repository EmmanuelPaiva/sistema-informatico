# db/conexion.py
import os
import sys
import configparser
import psycopg2
from psycopg2.extras import RealDictCursor


def _get_base_dir() -> str:
    """
    Devuelve la carpeta base desde donde se deben leer los archivos de datos.

    - En desarrollo: raíz del proyecto (sistema-informatico).
    - En ejecutable (.exe): carpeta interna de PyInstaller (sys._MEIPASS),
      donde se extraen los 'datas' como config.ini.
    """
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS")
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _get_base_dir()
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")


def _load_database_url() -> str:
    """
    Lee la URL de la base desde config.ini.
    Sección: [database], clave: url.
    """

    # DEBUG: registrar qué ve el programa
    debug_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else BASE_DIR
    debug_path = os.path.join(debug_dir, "db_debug.txt")

    try:
        with open(debug_path, "w", encoding="utf-8") as dbg:
            dbg.write(f"BASE_DIR = {BASE_DIR}\n")
            dbg.write(f"CONFIG_PATH = {CONFIG_PATH}\n")
            dbg.write("Contenido de BASE_DIR:\n")
            try:
                for name in os.listdir(BASE_DIR):
                    dbg.write(f"  - {name}\n")
            except Exception as e_ls:
                dbg.write(f"  (Error listando BASE_DIR: {e_ls})\n")
    except Exception:
        # si falla el log, no rompemos
        pass

    if not os.path.exists(CONFIG_PATH):
        raise RuntimeError(f"No se encontró el archivo de configuración: {CONFIG_PATH}")

    config = configparser.ConfigParser()
    try:
        # Usamos open explícito para ver cualquier error de E/S
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config.read_file(f)
    except Exception as e:
        raise RuntimeError(f"Error leyendo archivo de configuración {CONFIG_PATH}: {e}")

    if not config.has_section("database"):
        raise RuntimeError("El archivo config.ini no tiene la sección [database]")

    if not config.has_option("database", "url"):
        raise RuntimeError("El archivo config.ini no tiene la clave 'url' en [database]")

    url = config.get("database", "url")

    if not url:
        raise RuntimeError("La clave 'url' en [database] está vacía en config.ini")

    # Supabase requiere sslmode=require
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    # Log extra de la URL leída
    try:
        with open(debug_path, "a", encoding="utf-8") as dbg:
            dbg.write(f"\nDATABASE_URL = {url}\n")
    except Exception:
        pass

    return url


DATABASE_URL = _load_database_url()


def conexion():
    return psycopg2.connect(DATABASE_URL)


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
