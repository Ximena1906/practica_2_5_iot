
import os

from fastapi import HTTPException, Request


def validar_origen(request: Request) -> None:
    """
    Comprueba que la solicitud provenga
    del origen autorizado de la interfaz.
    """

    origen = request.headers.get("origin")

    origen_permitido = os.getenv(
        "FRONTEND_ORIGIN",
        ""
    ).strip().rstrip("/")

    if not origen_permitido:
        raise HTTPException(
            status_code=503,
            detail="Origen autorizado no configurado"
        )

    if not origen or origen.rstrip("/") != origen_permitido:
        raise HTTPException(
            status_code=403,
            detail="Origen de solicitud no autorizado"
        )
