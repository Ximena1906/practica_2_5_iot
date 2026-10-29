
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel, Field

from app.autenticacion import vinculacion as v
from app.autenticacion.sesiones import revocar_sesion
from app.autenticacion.cookies import (
    NOMBRE_COOKIE_SESION,
    establecer_cookie_sesion,
    validar_cookie_sesion,
    eliminar_cookie_sesion
)
from app.autenticacion.origen import validar_origen


router = APIRouter(
    prefix="/api/vinculacion",
    tags=["Vinculación de dispositivos"]
)


# ========================================================
# MODELOS DE SOLICITUD
# ========================================================

class SolicitudVinculacion(BaseModel):
    codigo: str = Field(min_length=1, max_length=200)
    identificador: str = Field(min_length=1, max_length=200)


# ========================================================
# VINCULAR DISPOSITIVO
# ========================================================

@router.post("/")
def vincular_dispositivo(
    datos: SolicitudVinculacion,
    response: Response,
    request: Request
):
    # Verificar que la solicitud provenga del origen autorizado
    validar_origen(request)

    # Validar el código de vinculación
    token = v.vincular_dispositivo(
        datos.codigo,
        datos.identificador
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="No se pudo vincular el dispositivo. Verifica el código o los bloqueos."
        )

    # Guardar la sesión en una cookie segura
    establecer_cookie_sesion(response, token)

    return {
        "mensaje": "Dispositivo vinculado correctamente"
    }


# ========================================================
# VALIDAR SESIÓN DEL DISPOSITIVO
# ========================================================

@router.post("/validar")
def validar_dispositivo(request: Request):

    # Verificar el origen de la solicitud
    validar_origen(request)

    # Comprobar que la cookie corresponde a una sesión activa
    if not validar_cookie_sesion(request):
        raise HTTPException(
            status_code=401,
            detail="Sesión inválida, vencida o revocada"
        )

    return {
        "sesion_valida": True
    }


# ========================================================
# REVOCAR SESIÓN DEL DISPOSITIVO
# ========================================================

@router.post("/revocar")
def revocar_dispositivo(
    request: Request,
    response: Response
):
    # Verificar el origen de la solicitud
    validar_origen(request)

    # Obtener el token desde la cookie
    token = request.cookies.get(NOMBRE_COOKIE_SESION)

    # Revocar la sesión en SQLite
    if not token or not revocar_sesion(token):
        raise HTTPException(
            status_code=401,
            detail="Sesión inválida, vencida o revocada"
        )

    # Eliminar la cookie del navegador
    eliminar_cookie_sesion(response)

    return {
        "mensaje": "Sesión revocada correctamente"
    }
