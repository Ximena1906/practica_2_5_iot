
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.websocket_manager import websocket_manager


router = APIRouter(tags=["WebSocket IoT"])


@router.websocket("/ws/vehiculos/{id_vehiculo}")
async def websocket_vehiculo(
    websocket: WebSocket,
    id_vehiculo: int
):
    """
    Establece una conexión WebSocket
    independiente para cada vehículo IoT.
    """

    if id_vehiculo <= 0:
        await websocket.close(code=1008)
        return

    await websocket_manager.conectar(websocket, id_vehiculo)

    try:
        # Confirmar la conexión
        await websocket.send_json({
            "tipo": "CONEXION",
            "mensaje": "Conexión WebSocket establecida",
            "id_vehiculo": id_vehiculo
        })

        # Mantener la conexión activa
        while True:
            mensaje = await websocket.receive_text()

            # Responder al cliente conectado
            await websocket.send_json({
                "tipo": "RESPUESTA",
                "id_vehiculo": id_vehiculo,
                "mensaje": mensaje
            })

    except WebSocketDisconnect:
        pass

    finally:
        websocket_manager.desconectar(
            websocket,
            id_vehiculo
        )
