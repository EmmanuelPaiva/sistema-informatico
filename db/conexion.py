import psycopg2

def conexion():
        try:
            conexion = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password="48884368"
            )
            return conexion
            print("Conexión exitosa a la base de datos")
        except psycopg2.Error as e:
            print("Error al conectar a la base de datos:", e)
            conexion = None
    



