
from fastapi import APIRouter, HTTPException, Depends

from app.services.vehiculo_service import VehiculoService
from app.security import verificar_admin

from app.websocket.notification_client import enviar_notificacion_interna

import asyncio

from pydantic import BaseModel, Field



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

class VehiculoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    modelo: str = Field(min_length=1, max_length=80)
    descripcion: str = Field(default="", max_length=255)
    microcontrolador: str = Field(min_length=1, max_length=50)

class VehiculoActualizar(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    modelo: str = Field(min_length=1, max_length=80)
    descripcion: str = Field(default="", max_length=255)
    microcontrolador: str = Field(min_length=1, max_length=50)
    activo: bool

class ComandoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=60)
    codigo: int = Field(ge=1)
    descripcion: str = Field(default="", max_length=255)

class ComandoActualizar(BaseModel):
    nombre: str = Field(min_length=1, max_length=60)
    codigo: int = Field(ge=1)
    descripcion: str = Field(default="", max_length=255)
    activo: bool

class DemoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    descripcion: str = Field(default="", max_length=255)

class DemoActualizar(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    descripcion: str = Field(default="", max_length=255)
    activo: bool

class MovimientoDemoCrear(BaseModel):
    id_comando: int = Field(gt=0)
    orden: int = Field(ge=1)
    duracion_ms: int = Field(gt=0)
    pausa_ms: int = Field(ge=0)

class MovimientoDemoActualizar(BaseModel):
    id_comando: int = Field(gt=0)
    orden: int = Field(ge=1)
    duracion_ms: int = Field(gt=0)
    pausa_ms: int = Field(ge=0)




@router.post("/", dependencies=[Depends(verificar_admin)])
def crear_vehiculo(datos: VehiculoCrear):
    """
    Registra un vehículo IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.crear_vehiculo(
            datos.nombre,
            datos.modelo,
            datos.descripcion,
            datos.microcontrolador
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al crear el vehículo"
        )


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


@router.post(
    "/{id_vehiculo}/movimientos/{id_comando}",
    dependencies=[Depends(verificar_admin)]
)
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
        
        # Notificar al servidor WebSocket del puerto 8765
        # después de guardar el movimiento
        await enviar_notificacion_interna(
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


@router.post(
    "/{id_vehiculo}/demos/{id_demo}/ejecutar",
    dependencies=[Depends(verificar_admin)]
)
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

        # Enviar eventos al servidor WebSocket del puerto 8765
        async def enviar_evento(evento):
            await enviar_notificacion_interna(
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

        # Notificar que terminó correctamente mediante el servidor WebSocket del puerto 8765
        await enviar_notificacion_interna(
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

@router.put("/{id_vehiculo}", dependencies=[Depends(verificar_admin)])
def actualizar_vehiculo(
    id_vehiculo: int,
    datos: VehiculoActualizar
):
    """
    Actualiza los datos de un vehículo IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.actualizar_vehiculo(
            id_vehiculo,
            datos.nombre,
            datos.modelo,
            datos.descripcion,
            datos.microcontrolador,
            int(datos.activo)
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el vehículo"
        )

@router.delete("/{id_vehiculo}", dependencies=[Depends(verificar_admin)])
def eliminar_vehiculo(id_vehiculo: int):
    """
    Elimina un vehículo IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.eliminar_vehiculo(id_vehiculo)

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el vehículo"
        )

@router.post(
    "/{id_vehiculo}/comandos",
    dependencies=[Depends(verificar_admin)]
)
def crear_comando(
    id_vehiculo: int,
    datos: ComandoCrear
):
    """
    Registra un comando para un vehículo IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.crear_comando(
            id_vehiculo,
            datos.nombre,
            datos.codigo,
            datos.descripcion
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al crear el comando"
        )

@router.put(
    "/comandos/{id_comando}",
    dependencies=[Depends(verificar_admin)]
)
def actualizar_comando(
    id_comando: int,
    datos: ComandoActualizar
):
    """
    Actualiza un comando IoT existente.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.actualizar_comando(
            id_comando,
            datos.nombre,
            datos.codigo,
            datos.descripcion,
            int(datos.activo)
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el comando"
        )

@router.delete(
    "/comandos/{id_comando}",
    dependencies=[Depends(verificar_admin)]
)
def eliminar_comando(id_comando: int):
    """
    Elimina un comando IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.eliminar_comando(id_comando)

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el comando"
        )

@router.post(
    "/{id_vehiculo}/demos",
    dependencies=[Depends(verificar_admin)]
)
def crear_demo(
    id_vehiculo: int,
    datos: DemoCrear
):
    """
    Registra una nueva demostración para un vehículo IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.crear_demo(
            id_vehiculo,
            datos.nombre,
            datos.descripcion
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al crear la demostración"
        )

@router.put(
    "/demos/{id_demo}",
    dependencies=[Depends(verificar_admin)]
)
def actualizar_demo(
    id_demo: int,
    datos: DemoActualizar
):
    """
    Actualiza una demostración IoT existente.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.actualizar_demo(
            id_demo,
            datos.nombre,
            datos.descripcion,
            int(datos.activo)
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la demostración"
        )

@router.delete(
    "/demos/{id_demo}",
    dependencies=[Depends(verificar_admin)]
)
def eliminar_demo(id_demo: int):
    """
    Elimina una demostración IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.eliminar_demo(id_demo)

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la demostración"
        )

@router.post(
    "/demos/{id_demo}/movimientos",
    dependencies=[Depends(verificar_admin)]
)
def agregar_movimiento_demo(
    id_demo: int,
    datos: MovimientoDemoCrear
):
    """
    Agrega un movimiento a una demostración IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.agregar_movimiento_demo(
            id_demo,
            datos.id_comando,
            datos.orden,
            datos.duracion_ms,
            datos.pausa_ms
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al agregar el movimiento a la DEMO"
        )

@router.put(
    "/demos/movimientos/{id_demo_movimiento}",
    dependencies=[Depends(verificar_admin)]
)
def actualizar_movimiento_demo(
    id_demo_movimiento: int,
    datos: MovimientoDemoActualizar
):
    """
    Actualiza un movimiento de una demostración IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.actualizar_movimiento_demo(
            id_demo_movimiento,
            datos.id_comando,
            datos.orden,
            datos.duracion_ms,
            datos.pausa_ms
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el movimiento de la DEMO"
        )

@router.delete(
    "/demos/movimientos/{id_demo_movimiento}",
    dependencies=[Depends(verificar_admin)]
)
def eliminar_movimiento_demo(id_demo_movimiento: int):
    """
    Elimina un movimiento de una demostración IoT.
    Requiere clave de administración.
    """

    try:
        servicio = VehiculoService()

        resultado = servicio.eliminar_movimiento_demo(
            id_demo_movimiento
        )

        if not resultado["exito"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensaje"]
            )

        return resultado

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el movimiento de la DEMO"
        )
