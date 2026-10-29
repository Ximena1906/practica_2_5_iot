
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.autenticacion.auth import validar_token
from app.autenticacion.websocket_auth import validar_websocket_navegador
from app.autenticacion.sesiones import validar_sesion
from app.autenticacion.cookies import NOMBRE_COOKIE_SESION
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

    tipo_cliente = websocket.headers.get(
        "x-tipo-cliente", ""
    ).strip().lower()

    token = websocket.headers.get(
        "x-auth-token", ""
    )

    # Autenticación del ESP32 o del control por encabezados
    if tipo_cliente in {"esp32", "control"}:
        if not validar_token(token, tipo_cliente):
            await websocket.close(code=1008)
            return

        # Un navegador no debe utilizar este mecanismo.
        # Los clientes con encabezados deben ser clientes no web.
        cliente_autorizado = tipo_cliente

    else:
        # Autenticación del navegador mediante cookie y Origin
        if not validar_websocket_navegador(websocket):
            await websocket.close(code=1008)
            return

        tipo_cliente = "navegador"
        cliente_autorizado = "navegador"

    await websocket_manager.conectar(
        websocket,
        id_vehiculo
    )

    try:
        await websocket.send_json({
            "tipo": "CONEXION",
            "mensaje": "Conexión WebSocket autorizada",
            "id_vehiculo": id_vehiculo,
            "cliente": cliente_autorizado
        })

        while True:
            mensaje = await websocket.receive_text()

            # Comprobar nuevamente la sesión del navegador
            if tipo_cliente == "navegador":
                token_sesion = websocket.cookies.get(
                    NOMBRE_COOKIE_SESION
                )

                if not token_sesion or not validar_sesion(token_sesion):
                    await websocket.close(code=1008)
                    return

            # El ESP32 no puede emitir comandos
            if tipo_cliente == "esp32":
                await websocket.send_json({
                    "tipo": "ERROR",
                    "mensaje": "Cliente sin permiso para enviar comandos"
                })
                continue

            comando = mensaje.strip().upper()

            if comando not in COMANDOS_VALIDOS:
                await websocket.send_json({
                    "tipo": "ERROR",
                    "mensaje": "Comando no válido"
                })
                continue

            # SOLO SIMULACIÓN: NO ACTIVAR MOTORES
            await websocket.send_json({
                "tipo": "SIMULACION",
                "comando": comando,
                "mensaje": "Comando validado sin activar salidas"
            })

    except WebSocketDisconnect:
        pass

    finally:
        websocket_manager.desconectar(
            websocket,
            id_vehiculo
        )
