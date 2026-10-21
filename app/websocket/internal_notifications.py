
import os
import secrets

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.websocket.websocket_manager import websocket_manager


load_dotenv()

router = APIRouter(
    prefix="/interno",
    tags=["Comunicación interna"]
)


class NotificacionInterna(BaseModel):
    id_vehiculo: int = Field(gt=0)
    evento: dict


@router.post("/notificar", include_in_schema=False)
async def notificar(
    datos: NotificacionInterna,
    x_internal_key: str | None = Header(default=None)
):
    clave_esperada = os.getenv("INTERNAL_API_KEY")

    if not clave_esperada or len(clave_esperada) < 32:
        raise HTTPException(
            status_code=503,
            detail="Comunicación interna no configurada"
        )

    if not x_internal_key or not secrets.compare_digest(
        x_internal_key,
        clave_esperada
    ):
        raise HTTPException(
            status_code=401,
            detail="Clave interna inválida"
        )

    await websocket_manager.enviar_vehiculo(
        datos.id_vehiculo,
        datos.evento
    )

    return {
        "exito": True,
        "mensaje": "Notificación interna procesada"
    }
