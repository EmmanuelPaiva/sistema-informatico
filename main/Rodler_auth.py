# auth.py
# Autenticación con Argon2id para el sistema Rodler
# Requisitos: pip install argon2-cffi psycopg2-binary python-dotenv

from typing import Tuple, Dict, Any, Optional, List
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db.conexion import get_conn

ph = PasswordHasher()

# ───────── helpers de hash ─────────
def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        return False

# ───────── acceso a datos (rodler_auth.*) ─────────
def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Devuelve: {id, username, password_hash, is_active, last_login_at} o None
    Búsqueda case-insensitive.
    """
    sql = """
        SELECT id, username, password_hash, is_active, last_login_at
        FROM rodler_auth.usuarios
        WHERE LOWER(username) = LOWER(%s)
        LIMIT 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (username,))
        return cur.fetchone()

def get_roles_for_user(user_id: str) -> List[str]:
    """
    user_id = UUID de rodler_auth.usuarios.id
    Retorna lista de códigos de rol (p.ej. ['admin','usuario'])
    """
    sql = """
        SELECT r.codigo
        FROM rodler_auth.usuario_roles ur
        JOIN rodler_auth.roles r ON r.id = ur.rol_id
        WHERE ur.usuario_id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall() or []
        try:
            return [r["codigo"] for r in rows]
        except Exception:
            return [r[0] for r in rows]

# ───────── API principal ─────────
def authenticate(username: str, password: str) -> Tuple[bool, Any]:
    """
    Retorna:
      (True, {"user": {...}, "roles": [...]})  si OK
      (False, "mensaje de error")              si falla
    """
    user = get_user_by_username(username)
    if not user:
        return False, "Usuario o contraseña inválidos"

    # soporta dict o tupla (si algún día cambiás el cursor)
    def _get(k, i):
        return user.get(k) if isinstance(user, dict) else user[i]

    u_id            = _get("id", 0)
    u_username      = _get("username", 1)
    u_password_hash = _get("password_hash", 2)
    u_is_active     = _get("is_active", 3)

    if not u_is_active:
        return False, "Cuenta inactiva. Contacte al administrador"

    if not verify_password(password, u_password_hash):
        return False, "Usuario o contraseña inválidos"

    # actualizar último acceso
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE rodler_auth.usuarios SET last_login_at = NOW() WHERE id = %s;",
            (u_id,),
        )
        conn.commit()

    roles = get_roles_for_user(u_id)
    safe_user = {
        "id": u_id,
        "username": u_username,
        "is_active": u_is_active,
        "last_login_at": _get("last_login_at", 4),
    }
    return True, {"user": safe_user, "roles": roles}

# ───────── utilidades admin ─────────
def create_user(username: str, plain_password: str, is_active: bool = True) -> Dict[str, Any]:
    """
    Crea usuario (UUID por default en la tabla).
    Devuelve: {"id": uuid, "username": ..., "created_at": ts}
    """
    pwd_hash = hash_password(plain_password)
    sql = """
        INSERT INTO rodler_auth.usuarios (username, password_hash, is_active)
        VALUES (%s, %s, %s)
        RETURNING id, username, created_at;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (username, pwd_hash, is_active))
        row = cur.fetchone()
        conn.commit()
        if isinstance(row, dict):
            return {"id": row["id"], "username": row["username"], "created_at": row["created_at"]}
        return {"id": row[0], "username": row[1], "created_at": row[2]}

def assign_role_by_code(user_id: str, role_code: str) -> bool:
    """
    Asigna rol por su 'codigo' al usuario (UUID).
    Retorna True si insertó; False si no existe rol o ya estaba asignado.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM rodler_auth.roles WHERE codigo = %s LIMIT 1;", (role_code,))
        row = cur.fetchone()
        if not row:
            return False
        role_id = row["id"] if isinstance(row, dict) else row[0]

        cur.execute("""
            INSERT INTO rodler_auth.usuario_roles (usuario_id, rol_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (user_id, role_id))
        inserted = (cur.rowcount == 1)
        conn.commit()
        return inserted

def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Cambia contraseña verificando la actual.
    """
    user = get_user_by_username(username)
    if not user:
        return False, "Usuario no existe"

    current_hash = user["password_hash"] if isinstance(user, dict) else user[2]
    if not verify_password(old_password, current_hash):
        return False, "Contraseña actual incorrecta"

    new_hash = hash_password(new_password)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE rodler_auth.usuarios SET password_hash = %s WHERE id = %s;",
            (new_hash, user["id"] if isinstance(user, dict) else user[0]),
        )
        conn.commit()
    return True, "Contraseña actualizada"
