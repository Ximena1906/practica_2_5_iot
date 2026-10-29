from contextlib import closing
import secrets
import hashlib


def generar_codigo_vinculacion():
    """Genera un código de vinculación aleatorio y seguro."""
    return secrets.token_urlsafe(24)


def obtener_hash_codigo(codigo):
    """Obtiene la huella SHA-256 del código."""
    return hashlib.sha256(
        codigo.encode("utf-8")
    ).hexdigest()

from datetime import datetime, timedelta, timezone

DURACION_CODIGO_MINUTOS = 10


def calcular_vencimiento_codigo():
    """Calcula cuándo caduca el código de vinculación."""
    return datetime.now(timezone.utc) + timedelta(
        minutes=DURACION_CODIGO_MINUTOS
    )


def codigo_vigente(fecha_vencimiento):
    """Comprueba si el código todavía está vigente."""
    return datetime.now(timezone.utc) < fecha_vencimiento

import sqlite3

from app.autenticacion.sesiones import RUTA_BD


def inicializar_tabla_vinculacion():
    """Prepara el almacenamiento de códigos de vinculación."""
    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS codigos_vinculacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_hash TEXT NOT NULL UNIQUE,
                    fecha_vencimiento TEXT NOT NULL,
                    utilizado INTEGER NOT NULL DEFAULT 0,
                    intentos INTEGER NOT NULL DEFAULT 0,
                    creado_en TEXT NOT NULL
                )
            """)
        conexion.commit()

def guardar_codigo_vinculacion(codigo):
    """Guarda la huella del código y su vencimiento."""
    if not codigo:
        return False

    codigo_hash = obtener_hash_codigo(codigo)
    vencimiento = calcular_vencimiento_codigo().isoformat()
    creado_en = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            conexion.execute(
                """
                INSERT INTO codigos_vinculacion (
                    codigo_hash,
                    fecha_vencimiento,
                    utilizado,
                    intentos,
                    creado_en
                )
                VALUES (?, ?, 0, 0, ?)
                """,
                (codigo_hash, vencimiento, creado_en)
            )
            conexion.commit()

    return True



def consumir_codigo_vinculacion(codigo):
    """Valida y consume un código una sola vez."""
    if not codigo:
        return False

    codigo_hash = obtener_hash_codigo(codigo)
    ahora = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(RUTA_BD, timeout=10)) as conexion:
        with conexion:

            # Comprobar el bloqueo global dentro de la transacción
            registro_global = conexion.execute(
                """
                SELECT bloqueado_hasta
                FROM limite_global_vinculacion
                WHERE id = 1
                """
            ).fetchone()

            if registro_global and registro_global[0]:
                bloqueo_global = datetime.fromisoformat(
                    registro_global[0]
                )

                if bloqueo_global > datetime.now(timezone.utc):
                    return None

            cursor = conexion.execute(
                """
                UPDATE codigos_vinculacion
                SET utilizado = 1
                WHERE codigo_hash = ?
                  AND utilizado = 0
                  AND fecha_vencimiento > ?
                """,
                (codigo_hash, ahora)
            )

            consumido = cursor.rowcount == 1

    return consumido


def inicializar_tabla_intentos():
    """Crea la tabla para controlar intentos de vinculación."""
    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS intentos_vinculacion (
                    identificador TEXT PRIMARY KEY,
                    intentos INTEGER NOT NULL DEFAULT 0,
                    bloqueado_hasta TEXT,
                    actualizado_en TEXT NOT NULL
                )
            """)

MAX_INTENTOS = 5
DURACION_BLOQUEO_MINUTOS = 15
VENTANA_INTENTOS_INDIVIDUALES_MINUTOS = 15



def identificador_bloqueado(identificador):
    """Comprueba si existe un bloqueo temporal activo."""
    if not identificador:
        return True

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            resultado = conexion.execute(
                """
                SELECT bloqueado_hasta
                FROM intentos_vinculacion
                WHERE identificador = ?
                """,
                (identificador,)
            ).fetchone()

    if resultado is None or resultado[0] is None:
        return False

    try:
        vencimiento = datetime.fromisoformat(resultado[0])
        return datetime.now(timezone.utc) < vencimiento
    except (ValueError, TypeError):
        return True


def registrar_intento_fallido(identificador):
    """Registra un fallo y bloquea temporalmente al alcanzar el límite."""
    if not identificador:
        return False

    ahora = datetime.now(timezone.utc)
    ahora_texto = ahora.isoformat()

    with closing(sqlite3.connect(RUTA_BD, timeout=10)) as conexion:
        with conexion:
            conexion.execute("BEGIN IMMEDIATE")

            resultado = conexion.execute(
                """
                SELECT intentos, bloqueado_hasta
                FROM intentos_vinculacion
                WHERE identificador = ?
                """,
                (identificador,)
            ).fetchone()

            intentos = 0

            if resultado:
                intentos = resultado[0]

                if resultado[1]:
                    bloqueo = datetime.fromisoformat(resultado[1])

                    if ahora < bloqueo:
                        return True

                    intentos = 0

            intentos += 1
            bloqueado_hasta = None

            if intentos >= MAX_INTENTOS:
                bloqueado_hasta = (
                    ahora + timedelta(
                        minutes=DURACION_BLOQUEO_MINUTOS
                    )
                ).isoformat()

            conexion.execute(
                """
                INSERT INTO intentos_vinculacion (
                    identificador,
                    intentos,
                    bloqueado_hasta,
                    actualizado_en
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(identificador)
                DO UPDATE SET
                    intentos = excluded.intentos,
                    bloqueado_hasta = excluded.bloqueado_hasta,
                    actualizado_en = excluded.actualizado_en
                """,
                (
                    identificador,
                    intentos,
                    bloqueado_hasta,
                    ahora_texto
                )
            )

    return bloqueado_hasta is not None


def reiniciar_intentos(identificador):
    """Limpia los intentos después de una vinculación exitosa."""
    if not identificador:
        return False

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            cursor = conexion.execute(
                """
                DELETE FROM intentos_vinculacion
                WHERE identificador = ?
                  AND (
                      bloqueado_hasta IS NULL
                      OR bloqueado_hasta <= ?
                  )
                """,
                (
                    identificador,
                    datetime.now(timezone.utc).isoformat()
                )
            )

            eliminado = cursor.rowcount > 0

    return eliminado

from app.autenticacion.sesiones import (
    crear_token_sesion,
    obtener_hash_sesion,
    calcular_vencimiento
)



def vincular_dispositivo(codigo, identificador):
    """Vincula un dispositivo mediante una transacción SQLite."""
    if not codigo or not identificador:
        return None

    if identificador_bloqueado(identificador):
        return None
    if vinculacion_global_bloqueada():
        return None

    codigo_hash = obtener_hash_codigo(codigo)
    token_sesion = crear_token_sesion()
    token_hash = obtener_hash_sesion(token_sesion)

    ahora = datetime.now(timezone.utc).isoformat()
    vencimiento_sesion = calcular_vencimiento().isoformat()

    codigo_invalido = False

    with closing(sqlite3.connect(RUTA_BD, timeout=10)) as conexion:
        with conexion:
            conexion.execute("BEGIN IMMEDIATE")

            # Comprobar el bloqueo dentro de la transacción
            registro = conexion.execute(
                """
                SELECT bloqueado_hasta
                FROM intentos_vinculacion
                WHERE identificador = ?
                """,
                (identificador,)
            ).fetchone()

            if registro and registro[0]:
                bloqueo = datetime.fromisoformat(registro[0])
                if bloqueo > datetime.now(timezone.utc):
                    return None

            # Consumir el código una sola vez
            cursor = conexion.execute(
                """
                UPDATE codigos_vinculacion
                SET utilizado = 1
                WHERE codigo_hash = ?
                  AND utilizado = 0
                  AND fecha_vencimiento > ?
                """,
                (codigo_hash, ahora)
            )



            if cursor.rowcount != 1:
                codigo_invalido = True
                momento_fallo = datetime.now(timezone.utc)

                registrar_intento_global_en_transaccion(
                    conexion,
                    momento_fallo
                )

                registrar_intento_individual_en_transaccion(
                    conexion,
                    identificador,
                    momento_fallo
                )
            else:


                # Crear la sesión en la misma transacción
                conexion.execute(
                    """
                    INSERT INTO sesiones (
                        token_hash,
                        fecha_vencimiento,
                        revocada
                    )
                    VALUES (?, ?, 0)
                    """,
                    (token_hash, vencimiento_sesion)
                )

    # Registrar intentos después de cerrar la conexión

    if codigo_invalido:
        return None

    reiniciar_intentos(identificador)

    return token_sesion

def inicializar_tabla_limite_global():
    """Crea la tabla para controlar los intentos globales de vinculación."""
    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS limite_global_vinculacion (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    intentos INTEGER NOT NULL DEFAULT 0,
                    ventana_inicio TEXT NOT NULL,
                    bloqueado_hasta TEXT
                )
            """)
# Protección global contra intentos de vinculación
MAX_INTENTOS_GLOBALES = 10
VENTANA_GLOBAL_MINUTOS = 10
DURACION_BLOQUEO_GLOBAL_MINUTOS = 15


def vinculacion_global_bloqueada():
    """Comprueba si existe un bloqueo global activo."""
    ahora = datetime.now(timezone.utc)

    with closing(sqlite3.connect(RUTA_BD)) as conexion:
        resultado = conexion.execute(
            """
            SELECT bloqueado_hasta
            FROM limite_global_vinculacion
            WHERE id = 1
            """
        ).fetchone()

    if resultado is None or resultado[0] is None:
        return False

    try:
        bloqueo = datetime.fromisoformat(resultado[0])
        return ahora < bloqueo
    except (ValueError, TypeError):
        return True

def registrar_intento_global_fallido():
    """Registra un intento fallido y aplica el límite global."""
    ahora = datetime.now(timezone.utc)

    with closing(sqlite3.connect(RUTA_BD, timeout=10)) as conexion:
        with conexion:
            conexion.execute("BEGIN IMMEDIATE")

            registro = conexion.execute(
                """
                SELECT intentos, ventana_inicio, bloqueado_hasta
                FROM limite_global_vinculacion
                WHERE id = 1
                """
            ).fetchone()

            if registro:
                intentos, inicio_texto, bloqueo_texto = registro

                if bloqueo_texto:
                    bloqueo = datetime.fromisoformat(bloqueo_texto)

                    if ahora < bloqueo:
                        return True

                inicio = datetime.fromisoformat(inicio_texto)

                if ahora >= inicio + timedelta(
                    minutes=VENTANA_GLOBAL_MINUTOS
                ):
                    intentos = 0

            else:
                intentos = 0

            intentos += 1

            if registro and ahora < inicio + timedelta(
                minutes=VENTANA_GLOBAL_MINUTOS
            ):
                ventana_inicio = inicio
            else:
                ventana_inicio = ahora

            bloqueado_hasta = None

            if intentos >= MAX_INTENTOS_GLOBALES:
                bloqueado_hasta = ahora + timedelta(
                    minutes=DURACION_BLOQUEO_GLOBAL_MINUTOS
                )

            conexion.execute(
                """
                INSERT INTO limite_global_vinculacion (
                    id, intentos, ventana_inicio, bloqueado_hasta
                )
                VALUES (1, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    intentos = excluded.intentos,
                    ventana_inicio = excluded.ventana_inicio,
                    bloqueado_hasta = excluded.bloqueado_hasta
                """,
                (
                    intentos,
                    ventana_inicio.isoformat(),
                    bloqueado_hasta.isoformat()
                    if bloqueado_hasta else None
                )
            )

            return bloqueado_hasta is not None

def registrar_intento_global_en_transaccion(conexion, ahora):
    """Registra un fallo global usando una transacción existente."""
    registro = conexion.execute(
        """
        SELECT intentos, ventana_inicio, bloqueado_hasta
        FROM limite_global_vinculacion
        WHERE id = 1
        """
    ).fetchone()

    intentos = 0
    ventana_inicio = ahora

    if registro:
        intentos_actuales, inicio_texto, bloqueo_texto = registro

        if bloqueo_texto:
            bloqueo = datetime.fromisoformat(bloqueo_texto)

            if ahora < bloqueo:
                return True

        inicio = datetime.fromisoformat(inicio_texto)

        if ahora < inicio + timedelta(minutes=VENTANA_GLOBAL_MINUTOS):
            intentos = intentos_actuales
            ventana_inicio = inicio

    intentos += 1

    bloqueado_hasta = None

    if intentos >= MAX_INTENTOS_GLOBALES:
        bloqueado_hasta = ahora + timedelta(
            minutes=DURACION_BLOQUEO_GLOBAL_MINUTOS
        )

    conexion.execute(
        """
        INSERT INTO limite_global_vinculacion (
            id, intentos, ventana_inicio, bloqueado_hasta
        )
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id)
        DO UPDATE SET
            intentos = excluded.intentos,
            ventana_inicio = excluded.ventana_inicio,
            bloqueado_hasta = excluded.bloqueado_hasta
        """,
        (
            intentos,
            ventana_inicio.isoformat(),
            bloqueado_hasta.isoformat() if bloqueado_hasta else None
        )
    )

    return bloqueado_hasta is not None

def registrar_intento_individual_en_transaccion(
    conexion, identificador, ahora
):
    """Registra un intento fallido individual en una transacción existente."""

    registro = conexion.execute(
        """
        SELECT intentos, bloqueado_hasta, actualizado_en
        FROM intentos_vinculacion
        WHERE identificador = ?
        """,
        (identificador,)
    ).fetchone()

    intentos = 0


    if registro:
        intentos, bloqueo_texto, actualizado_texto = registro

        if bloqueo_texto:
            bloqueo = datetime.fromisoformat(bloqueo_texto)

            if ahora < bloqueo:
                return True

            intentos = 0

        else:
            ultima_actualizacion = datetime.fromisoformat(
                actualizado_texto
            )

            if ahora >= ultima_actualizacion + timedelta(
                minutes=VENTANA_INTENTOS_INDIVIDUALES_MINUTOS
            ):
                intentos = 0

    intentos += 1
    bloqueado_hasta = None

    if intentos >= MAX_INTENTOS:
        bloqueado_hasta = ahora + timedelta(
            minutes=DURACION_BLOQUEO_MINUTOS
        )

    conexion.execute(
        """
        INSERT INTO intentos_vinculacion (
            identificador, intentos, bloqueado_hasta, actualizado_en
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(identificador)
        DO UPDATE SET
            intentos = excluded.intentos,
            bloqueado_hasta = excluded.bloqueado_hasta,
            actualizado_en = excluded.actualizado_en
        """,
        (
            identificador,
            intentos,
            bloqueado_hasta.isoformat()
            if bloqueado_hasta else None,
            ahora.isoformat()
        )
    )

    return bloqueado_hasta is not None
