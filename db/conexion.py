# db/conexion.py
import os
import psycopg2
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

def conexion():
    url = os.getenv("DATABASE_URL")
    if url is None:
        raise ValueError("No se encontró DATABASE_URL en el .env")
    
    # Supabase requiere sslmode=require
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    return psycopg2.connect(url)



