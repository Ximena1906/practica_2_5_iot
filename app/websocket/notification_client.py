
import os
import asyncio
import logging

import httpx
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)

URL_INTERNA = "http://127.0.0.1:8765/interno/notificar"


async def enviar_notificacion_interna(id_vehiculo: int, evento: dict):
    """
    Envía una notificación desde la API del puerto 8000
    hacia el servidor WebSocket del puerto 8765.
    """

    clave = os.getenv("INTERNAL_API_KEY")

    if not clave or len(clave) < 32:
        logger.error("La clave interna no está configurada")
        return False

    try:
        async with httpx.AsyncClient(timeout=5.0) as cliente:
            respuesta = await cliente.post(
                URL_INTERNA,
                headers={
                    "X-Internal-Key": clave
                },
                json={
                    "id_vehiculo": id_vehiculo,
                    "evento": evento
                }
            )

            respuesta.raise_for_status()
            return True

    except httpx.HTTPError:
        logger.exception("Error al enviar la notificación interna")
        return False
