
from fastapi import WebSocket


class WebSocketManager:
    """
    Administra las conexiones WebSocket
    de cada vehículo IoT.
    """

    def __init__(self):
        # Diccionario de conexiones por vehículo
        self.conexiones = {}

    async def conectar(self, websocket: WebSocket, id_vehiculo: int):
        """
        Acepta una conexión WebSocket y
        la asocia con un vehículo.
        """

        await websocket.accept()

        if id_vehiculo not in self.conexiones:
            self.conexiones[id_vehiculo] = []

        self.conexiones[id_vehiculo].append(websocket)

    def desconectar(self, websocket: WebSocket, id_vehiculo: int):
        """
        Elimina una conexión cuando
        el cliente se desconecta.
        """

        if id_vehiculo in self.conexiones:
            if websocket in self.conexiones[id_vehiculo]:
                self.conexiones[id_vehiculo].remove(websocket)

            if not self.conexiones[id_vehiculo]:
                del self.conexiones[id_vehiculo]

    async def enviar_vehiculo(self, id_vehiculo: int, mensaje: dict):
        """
        Envía un evento a los clientes
        conectados a un vehículo específico.
        """

        conexiones = self.conexiones.get(id_vehiculo, [])

        for websocket in conexiones.copy():
            try:
                await websocket.send_json(mensaje)
            except Exception:
                self.desconectar(websocket, id_vehiculo)


# Instancia compartida del administrador
websocket_manager = WebSocketManager()
