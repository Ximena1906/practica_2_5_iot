from contextlib import closing
import secrets
import hashlib


def crear_token_sesion():
    """Genera un token aleatorio para una sesión autorizada."""
    return secrets.token_urlsafe(32)


def obtener_hash_sesion(token):
    """Obtiene una huella SHA-256 del token para almacenarla."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


from datetime import datetime, timedelta, timezone

DURACION_SESION_DIAS = 30


def calcular_vencimiento():
    """Calcula cuándo debe caducar una sesión."""
    return datetime.now(timezone.utc) + timedelta(
        days=DURACION_SESION_DIAS
    )


def sesion_vigente(fecha_vencimiento):
    """Comprueba que una sesión no haya caducado."""
    return datetime.now(timezone.utc) < fecha_vencimiento


import sqlite3
from pathlib import Path

RUTA_BD = Path(__file__).resolve().parent / "sesiones.sqlite3"



def inicializar_base_sesiones():
    """Crea la tabla para almacenar sesiones autorizadas."""
    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS sesiones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_hash TEXT NOT NULL UNIQUE,
                    fecha_vencimiento TEXT NOT NULL,
                    revocada INTEGER NOT NULL DEFAULT 0
                )
            """)


def guardar_sesion(token):
    """Guarda una sesión autorizada en SQLite."""
    token_hash = obtener_hash_sesion(token)
    vencimiento = calcular_vencimiento().isoformat()

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            conexion.execute(
                """
                INSERT INTO sesiones (
                    token_hash,
                    fecha_vencimiento,
                    revocada
                )
                VALUES (?, ?, 0)
                """,
                (token_hash, vencimiento)
            )

    return True


def validar_sesion(token):
    """Comprueba si una sesión existe, está vigente y no fue revocada."""
    if not token:
        return False

    token_hash = obtener_hash_sesion(token)

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            resultado = conexion.execute(
                """
                SELECT fecha_vencimiento
                FROM sesiones
                WHERE token_hash = ?
                  AND revocada = 0
                """,
                (token_hash,)
            ).fetchone()

    if resultado is None:
        return False

    try:
        fecha_vencimiento = datetime.fromisoformat(resultado[0])
        return sesion_vigente(fecha_vencimiento)
    except (ValueError, TypeError):
        return False


def revocar_sesion(token):
    """Revoca una sesión autorizada."""
    if not token:
        return False

    token_hash = obtener_hash_sesion(token)

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            cursor = conexion.execute(
                """
                UPDATE sesiones
                SET revocada = 1
                WHERE token_hash = ?
                  AND revocada = 0
                """,
                (token_hash,)
            )

            revocada = cursor.rowcount > 0

    return revocada
