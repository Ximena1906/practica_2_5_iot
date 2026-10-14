
from fastapi import APIRouter, HTTPException

from app.services.vehiculo_service import VehiculoService

from app.websocket.websocket_manager import websocket_manager

import asyncio




router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos IoT"]
)


# Control de ejecución de DEMOS por vehículo
demos_en_ejecucion = set()
bloqueo_demos = asyncio.Lock()


# Bloqueos individuales para coordinar los movimientos
# y DEMOS de cada vehículo
bloqueos_vehiculos = {}


def obtener_bloqueo_vehiculo(id_vehiculo: int):
    """
    Obtiene el bloqueo correspondiente a un vehículo.
    """
    if id_vehiculo not in bloqueos_vehiculos:
        bloqueos_vehiculos[id_vehiculo] = asyncio.Lock()

    return bloqueos_vehiculos[id_vehiculo]



@router.get("/")
def obtener_vehiculos():
    """
    Consulta los vehículos registrados
    en Amazon RDS.
    """

    try:
        servicio = VehiculoService()

        return servicio.listar_vehiculos()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar los vehículos"
        )

@router.get("/{id_vehiculo}")
def consultar_vehiculo(id_vehiculo: int):
    """
    Consulta un vehículo específico
    mediante su ID.
    """

    if id_vehiculo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El ID del vehículo debe ser mayor que cero"
        )

    try:
        servicio = VehiculoService()

        resultado = servicio.consultar_vehiculo(id_vehiculo)

        if not resultado["exito"]:
            raise HTTPException(
                status_code=404,
                detail="Vehículo no encontrado"
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar el vehículo"
        )

@router.get("/{id_vehiculo}/comandos")
def consultar_comandos_vehiculo(id_vehiculo: int):
    """
    Consulta los comandos disponibles
    para un vehículo específico.
    """

    if id_vehiculo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El ID del vehículo debe ser mayor que cero"
        )

    try:
        servicio = VehiculoService()

        resultado = servicio.listar_comandos_vehiculo(
            id_vehiculo
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=404,
                detail="Vehículo no encontrado"
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar los comandos del vehículo"
        )

@router.get("/{id_vehiculo}/estado")
def consultar_estado_vehiculo(id_vehiculo: int):
    """
    Consulta el estado actual de un vehículo
    mediante el procedimiento sp_obtener_estado.
    """

    if id_vehiculo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El ID del vehículo debe ser mayor que cero"
        )

    try:
        servicio = VehiculoService()

        resultado = servicio.consultar_estado_vehiculo(
            id_vehiculo
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=404,
                detail="Vehículo no encontrado"
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar el estado del vehículo"
        )


@router.post("/{id_vehiculo}/movimientos/{id_comando}")
async def ejecutar_movimiento_individual(
    id_vehiculo: int,
    id_comando: int
):
    """
    Ejecuta un movimiento individual.

    Actualiza el estado del vehículo,
    registra el movimiento en el historial
    y notifica mediante WebSocket.
    """

    if id_vehiculo <= 0 or id_comando <= 0:
        raise HTTPException(
            status_code=400,
            detail="Los identificadores deben ser mayores que cero"
        )


    try:
        servicio = VehiculoService()

        # Ejecutar el movimiento en Amazon RDS
        # sin bloquear el servidor WebSocket
        from fastapi.concurrency import run_in_threadpool

        
        # Coordinar movimientos del mismo vehículo
        bloqueo_vehiculo = obtener_bloqueo_vehiculo(id_vehiculo)

        async with bloqueo_vehiculo:

            # No permitir movimientos individuales
            # si el vehículo está ejecutando un DEMO
            if id_vehiculo in demos_en_ejecucion:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "No se puede ejecutar un movimiento individual "
                        "mientras el vehículo ejecuta un DEMO"
                    )
                )

            # Actualizar estado y registrar historial
            resultado = await run_in_threadpool(
                servicio.ejecutar_movimiento_individual,
                id_vehiculo,
                id_comando
            )


        if not resultado["exito"]:
            mensaje = resultado["mensaje"]

            if mensaje == "Vehículo no encontrado":
                codigo = 404
            else:
                codigo = 400

            raise HTTPException(
                status_code=codigo,
                detail=mensaje
            )

        # Notificar a los clientes conectados
        # después de guardar el movimiento
        await websocket_manager.enviar_vehiculo(
            id_vehiculo,
            {
                "tipo": "MOVIMIENTO_INDIVIDUAL",
                "id_vehiculo": id_vehiculo,
                "id_comando": id_comando,
                "mensaje": "Movimiento individual ejecutado"
            }
        )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al ejecutar el movimiento individual"
        )


@router.get("/{id_vehiculo}/historial")
def consultar_historial_vehiculo(id_vehiculo: int):
    """
    Consulta el historial de movimientos
    registrados para un vehículo IoT.
    """

    if id_vehiculo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El ID del vehículo debe ser mayor que cero"
        )

    try:
        servicio = VehiculoService()

        resultado = servicio.consultar_historial_vehiculo(
            id_vehiculo
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=404,
                detail="Vehículo no encontrado"
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar el historial del vehículo"
        )

@router.get("/{id_vehiculo}/demos")
def consultar_demos_vehiculo(id_vehiculo: int):
    """
    Consulta los DEMOS registrados
    para un vehículo IoT.
    """

    if id_vehiculo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El ID del vehículo debe ser mayor que cero"
        )

    try:
        servicio = VehiculoService()

        resultado = servicio.listar_demos_vehiculo(
            id_vehiculo
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=404,
                detail="Vehículo no encontrado"
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar los DEMOS del vehículo"
        )

@router.get("/{id_vehiculo}/demos/{id_demo}/movimientos")
def consultar_movimientos_demo(
    id_vehiculo: int,
    id_demo: int
):
    """
    Consulta los movimientos programados
    de un DEMO perteneciente al vehículo.
    """

    if id_vehiculo <= 0 or id_demo <= 0:
        raise HTTPException(
            status_code=400,
            detail="Los identificadores deben ser mayores que cero"
        )

    try:
        servicio = VehiculoService()

        resultado = servicio.consultar_movimientos_demo(
            id_vehiculo,
            id_demo
        )

        if not resultado["exito"]:
            mensaje = resultado["mensaje"]

            if mensaje in (
                "Vehículo no encontrado",
                "DEMO no encontrado para este vehículo"
            ):
                codigo = 404
            else:
                codigo = 400

            raise HTTPException(
                status_code=codigo,
                detail=mensaje
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar los movimientos del DEMO"
        )


@router.post("/{id_vehiculo}/demos/{id_demo}/ejecutar")
async def ejecutar_demo_vehiculo(
    id_vehiculo: int,
    id_demo: int
):
    """
    Ejecuta un DEMO automáticamente.

    Evita ejecuciones simultáneas del mismo
    vehículo y notifica mediante WebSocket.

    No registra movimientos en el historial.
    """

    if id_vehiculo <= 0 or id_demo <= 0:
        raise HTTPException(
            status_code=400,
            detail="Los identificadores deben ser mayores que cero"
        )

    # Comprobar y reservar el vehículo
    async with bloqueo_demos:
        if id_vehiculo in demos_en_ejecucion:
            raise HTTPException(
                status_code=409,
                detail="Este vehículo ya está ejecutando un DEMO"
            )

        demos_en_ejecucion.add(id_vehiculo)

    try:
        servicio = VehiculoService()

        # Enviar eventos a los clientes del vehículo
        async def enviar_evento(evento):
            await websocket_manager.enviar_vehiculo(
                id_vehiculo,
                evento
            )

        
        # Coordinar el DEMO con los movimientos individuales
        bloqueo_vehiculo = obtener_bloqueo_vehiculo(id_vehiculo)

        async with bloqueo_vehiculo:

            # Ejecutar la secuencia completa del DEMO
            resultado = await servicio.ejecutar_demo(
                id_vehiculo,
                id_demo,
                enviar_evento
            )


        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        # Notificar que terminó correctamente
        await websocket_manager.enviar_vehiculo(
            id_vehiculo,
            {
                "tipo": "DEMO_FINALIZADO",
                "id_vehiculo": id_vehiculo,
                "id_demo": id_demo,
                "mensaje": "DEMO finalizado correctamente"
            }
        )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al ejecutar el DEMO"
        )

    finally:
        # Liberar el vehículo incluso si ocurre un error
        async with bloqueo_demos:
            demos_en_ejecucion.discard(id_vehiculo)
