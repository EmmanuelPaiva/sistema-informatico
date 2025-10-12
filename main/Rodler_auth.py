from typing import Tuple, Dict, Any, Optional, List
from datetime import datetime, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db.conexion import get_conn

ph = PasswordHasher()

def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def _get(row, key, idx):
    return row.get(key) if isinstance(row, dict) else row[idx]

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT id, username, pass_hash, is_active, locked_until
        FROM rodler_auth.users
        WHERE lower(username) = lower(%s)
        LIMIT 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (username,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": _get(row, "id", 0),
            "username": _get(row, "username", 1),
            "pass_hash": _get(row, "pass_hash", 2),
            "is_active": _get(row, "is_active", 3),
            "locked_until": _get(row, "locked_until", 4),
        }

def get_roles_for_user(user_id: int) -> List[str]:
    sql = """
        SELECT r.code
        FROM rodler_auth.user_roles ur
        JOIN rodler_auth.roles r ON r.id = ur.role_id
        WHERE ur.user_id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall() or []
        try:
            return [r["code"] for r in rows]
        except Exception:
            return [r[0] for r in rows]

def get_perms_for_user(user_id: int) -> List[str]:
    sql = """
        SELECT DISTINCT p.code
        FROM rodler_auth.user_roles ur
        JOIN rodler_auth.role_permissions rp ON rp.role_id = ur.role_id
        JOIN rodler_auth.permissions p      ON p.id = rp.perm_id
        WHERE ur.user_id = %s
        ORDER BY p.code;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_id,))
        rows = cur.fetchall() or []
        try:
            return [r["code"] for r in rows]
        except Exception:
            return [r[0] for r in rows]

def authenticate(username: str, password: str) -> Tuple[bool, Any]:
    user = get_user_by_username(username)
    if not user:
        return False, "Usuario o contraseña inválidos"

    if not user["is_active"]:
        return False, "Cuenta inactiva. Contacte al administrador"

    lu = user.get("locked_until")
    if lu:
        now = datetime.now(timezone.utc)
        lu_aware = lu if getattr(lu, "tzinfo", None) else lu.replace(tzinfo=timezone.utc)
        if lu_aware > now:
            return False, "Cuenta temporalmente bloqueada. Intente más tarde."

    if not verify_password(password, user["pass_hash"]):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("SELECT rodler_auth.login_failed(%s);", (user["id"],))
                conn.commit()
        except Exception:
            pass
        return False, "Usuario o contraseña inválidos"

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT rodler_auth.login_success(%s);", (user["id"],))
            conn.commit()
    except Exception:
        pass

    roles = list(dict.fromkeys(get_roles_for_user(user["id"])))  # unique, mantiene orden
    perms = list(dict.fromkeys(get_perms_for_user(user["id"])))  # unique, mantiene orden
    safe_user = {"id": user["id"], "username": user["username"], "is_active": user["is_active"]}

    return True, {"user": safe_user, "roles": roles, "perms": perms}

# ───────── utilidades admin ─────────
def create_user(username: str, plain_password: str, is_active: bool = True) -> Dict[str, Any]:
    """
    Crea usuario y devuelve {"id": id, "username": ..., "created_at": ts}
    """
    pwd_hash = hash_password(plain_password)
    sql = """
        INSERT INTO rodler_auth.users (username, pass_hash, is_active)
        VALUES (lower(%s), %s, %s)
        RETURNING id, username, created_at;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (username, pwd_hash, is_active))
        row = cur.fetchone()
        conn.commit()
        if isinstance(row, dict):
            return {"id": row["id"], "username": row["username"], "created_at": row["created_at"]}
        return {"id": row[0], "username": row[1], "created_at": row[2]}

def assign_role_by_code(user_id: int, role_code: str) -> bool:
    """
    Asigna rol por su 'code' al usuario.
    Retorna True si insertó; False si no existe rol o ya estaba asignado.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM rodler_auth.roles WHERE code = %s LIMIT 1;", (role_code,))
        row = cur.fetchone()
        if not row:
            return False
        role_id = row["id"] if isinstance(row, dict) else row[0]

        # más portable que ON CONFLICT DO NOTHING si no hay UNIQUE(user_id, role_id)
        cur.execute("""
            INSERT INTO rodler_auth.user_roles (user_id, role_id)
            SELECT %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM rodler_auth.user_roles WHERE user_id = %s AND role_id = %s
            );
        """, (user_id, role_id, user_id, role_id))
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

    if not verify_password(old_password, user["pass_hash"]):
        return False, "Contraseña actual incorrecta"

    new_hash = hash_password(new_password)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE rodler_auth.users SET pass_hash = %s WHERE id = %s;",
            (new_hash, user["id"]),
        )
        conn.commit()
    return True, "Contraseña actualizada"
