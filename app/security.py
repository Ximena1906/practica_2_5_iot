
import os
import secrets

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader


load_dotenv()

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def verificar_admin(
    api_key: str | None = Security(api_key_header)
):
    """
    Verifica la clave de administración
    enviada en el encabezado X-API-Key.
    """

    clave_esperada = os.getenv("ADMIN_API_KEY")

    if not clave_esperada or len(clave_esperada) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La seguridad administrativa no está configurada"
        )

    if not api_key or not secrets.compare_digest(
        api_key,
        clave_esperada
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de administración inválida"
        )

    return True
