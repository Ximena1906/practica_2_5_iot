
from fastapi import Response

NOMBRE_COOKIE_SESION = "excavadora_sesion"
DURACION_COOKIE_SEGUNDOS = 30 * 24 * 60 * 60


def establecer_cookie_sesion(
    response: Response,
    token: str
):
    """Configura una cookie segura para la sesión del celular."""

    response.set_cookie(
        key=NOMBRE_COOKIE_SESION,
        value=token,
        max_age=DURACION_COOKIE_SEGUNDOS,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/"
    )
from fastapi import Request

from app.autenticacion.sesiones import validar_sesion


def validar_cookie_sesion(request: Request) -> bool:
    """
    Comprueba si la solicitud contiene una cookie
    correspondiente a una sesión activa.
    """

    token = request.cookies.get(NOMBRE_COOKIE_SESION)

    if not token:
        return False

    return validar_sesion(token)
def eliminar_cookie_sesion(response: Response):
    """
    Elimina la cookie de sesión del navegador.
    """

    response.delete_cookie(
        key=NOMBRE_COOKIE_SESION,
        path="/",
        secure=True,
        httponly=True,
        samesite="strict"
    )