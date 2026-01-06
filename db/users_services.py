# db/users_service.py

from psycopg2 import errors
from db.conexion import get_conn


def crear_usuario(username: str, pass_hash: str, full_name: str, phone: str | None, role_name: str):
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:

                # 1. Crear usuario
                cur.execute(
                    """
                    INSERT INTO rodler_auth.users
                        (username, pass_hash, full_name, phone, is_active, must_change_pw)
                    VALUES (%s, %s, %s, %s, TRUE, TRUE)
                    RETURNING id
                    """,
                    (username, pass_hash, full_name, phone)
                )
                user_id = cur.fetchone()["id"]

                # 2. Obtener rol
                cur.execute(
                    "SELECT id FROM rodler_auth.roles WHERE code = %s",
                    (role_name,)
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError(f"Rol inexistente: {role_name}")
                role_id = row["id"]

                # 3. Asociar rol
                cur.execute(
                    """
                    INSERT INTO rodler_auth.user_roles (user_id, role_id)
                    VALUES (%s, %s)
                    """,
                    (user_id, role_id)
                )

        return user_id
    finally:
        conn.close()

