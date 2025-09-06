from db.conexion import conexion

def test():
    with conexion() as c:
        with c.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            print("✅ Conectado a:", cur.fetchone())
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            tablas = [r[0] for r in cur.fetchall()]
            print("📂 Tablas:", tablas)

if __name__ == "__main__":
    test()
    
