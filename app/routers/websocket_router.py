
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.websocket_manager import websocket_manager

router = APIRouter(tags=["WebSocket IoT"])

COMANDOS_VALIDOS = {
    "W", "S", "A", "D",
    "1", "2", "3", "4",
    "5", "6", "7", "8",
    "Q"
}


@router.websocket("/ws/vehiculos/{id_vehiculo}")
async def websocket_vehiculo(
    websocket: WebSocket,
    id_vehiculo: int
):
    if id_vehiculo <= 0:
        await websocket.close(code=1008)
        return

    await websocket_manager.conectar(websocket, id_vehiculo)

    try:
        await websocket.send_json({
            "tipo": "CONEXION",
            "mensaje": "Conexión WebSocket establecida",
            "id_vehiculo": id_vehiculo
        })

        while True:
            mensaje = await websocket.receive_text()
            comando = mensaje.strip().upper()

            if comando not in COMANDOS_VALIDOS:
                await websocket.send_json({
                    "tipo": "ERROR",
                    "mensaje": "Comando no válido"
                })
                continue

            await websocket_manager.enviar_vehiculo(
                id_vehiculo,
                {
                    "tipo": "COMANDO",
                    "id_vehiculo": id_vehiculo,
                    "comando": comando
                }
            )

    except WebSocketDisconnect:
        pass

    finally:
        websocket_manager.desconectar(
            websocket,
            id_vehiculo
        )
