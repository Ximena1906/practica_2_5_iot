
import os

from fastapi import WebSocket

from app.autenticacion.sesiones import validar_sesion
from app.autenticacion.cookies import NOMBRE_COOKIE_SESION


def validar_websocket_navegador(websocket: WebSocket) -> bool:
    """
    Valida el origen y la sesión del navegador
    antes de autorizar una conexión WebSocket.
    """

    origen = websocket.headers.get("origin", "")

    origen_permitido = os.getenv(
        "FRONTEND_ORIGIN", ""
    ).strip().rstrip("/")

    if not origen_permitido:
        return False

    if origen.rstrip("/") != origen_permitido:
        return False

    token = websocket.cookies.get(NOMBRE_COOKIE_SESION)

    if not token:
        return False

    return validar_sesion(token)
