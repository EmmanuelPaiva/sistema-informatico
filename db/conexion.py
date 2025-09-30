# db/conexion.py
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Cargar .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def conexion():
    url = os.getenv("DATABASE_URL")
    if url is None:
        raise ValueError("No se encontró DATABASE_URL en el .env")
    
    # Supabase requiere sslmode=require
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    return psycopg2.connect(url)

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("Falta DATABASE_URL en .env")
    url = DATABASE_URL
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

