
from app.repositories.vehiculo_repository import VehiculoRepository


class VehiculoService:
    """
    Capa de servicios para gestionar
    la información de vehículos IoT.
    """

    def __init__(self):
        self.repositorio = VehiculoRepository()

    def listar_vehiculos(self):
        """
        Obtiene los vehículos registrados
        y prepara la respuesta de la API.
        """

        vehiculos = self.repositorio.obtener_vehiculos()

        return {
            "exito": True,
            "mensaje": "Vehículos obtenidos correctamente",
            "total": len(vehiculos),
            "vehiculos": vehiculos
        }

    def consultar_vehiculo(self, id_vehiculo):
        """
        Consulta un vehículo específico
        mediante su identificador.
        """

        vehiculo = self.repositorio.obtener_vehiculo(
            id_vehiculo
        )

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado",
                "vehiculo": None
            }

        return {
            "exito": True,
            "mensaje": "Vehículo obtenido correctamente",
            "vehiculo": vehiculo
        }

    def listar_comandos_vehiculo(self, id_vehiculo):
        """
        Obtiene los comandos disponibles
        para un vehículo específico.
        """

        vehiculo = self.repositorio.obtener_vehiculo(
            id_vehiculo
        )

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado",
                "total": 0,
                "comandos": []
            }

        comandos = self.repositorio.obtener_comandos_vehiculo(
            id_vehiculo
        )

        return {
            "exito": True,
            "mensaje": "Comandos obtenidos correctamente",
            "id_vehiculo": id_vehiculo,
            "total": len(comandos),
            "comandos": comandos
        }

    def consultar_estado_vehiculo(self, id_vehiculo):
        """
        Consulta el estado actual
        de un vehículo IoT.
        """

        vehiculo = self.repositorio.obtener_vehiculo(
            id_vehiculo
        )

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado",
                "estado": None
            }

        estado = self.repositorio.obtener_estado_vehiculo(
            id_vehiculo
        )

        return {
            "exito": True,
            "mensaje": "Estado consultado correctamente",
            "id_vehiculo": id_vehiculo,
            "estado": estado
        }

    def ejecutar_movimiento_individual(
        self,
        id_vehiculo,
        id_comando
    ):
        """
        Valida y ejecuta un movimiento individual
        de un vehículo IoT.
        """

        # Validar identificadores
        if id_vehiculo <= 0 or id_comando <= 0:
            return {
                "exito": False,
                "mensaje": "Los identificadores deben ser mayores que cero"
            }

        # Verificar que el vehículo exista y esté activo
        vehiculo = self.repositorio.obtener_vehiculo(
            id_vehiculo
        )

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado"
            }

        if vehiculo["activo"] != 1:
            return {
                "exito": False,
                "mensaje": "El vehículo está inactivo"
            }

        # Obtener los comandos del vehículo
        comandos = self.repositorio.obtener_comandos_vehiculo(
            id_vehiculo
        )

        # Buscar un comando activo que pertenezca al vehículo
        comando_valido = next(
            (
                comando for comando in comandos
                if comando["id_comando"] == id_comando
                and comando["activo"] == 1
            ),
            None
        )

        if comando_valido is None:
            return {
                "exito": False,
                "mensaje": "El comando no existe, está inactivo o no pertenece al vehículo"
            }

        # Ejecutar la transacción en Amazon RDS
        self.repositorio.ejecutar_movimiento(
            id_vehiculo,
            id_comando
        )

        return {
            "exito": True,
            "mensaje": "Movimiento individual ejecutado correctamente",
            "id_vehiculo": id_vehiculo,
            "id_comando": id_comando,
            "comando": comando_valido["nombre"],
            "origen": "INDIVIDUAL"
        }

    def consultar_historial_vehiculo(self, id_vehiculo):
        """
        Consulta el historial de movimientos
        de un vehículo IoT.
        """

        # Verificar que el vehículo exista
        vehiculo = self.repositorio.obtener_vehiculo(
            id_vehiculo
        )

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado",
                "total": 0,
                "historial": []
            }

        # Consultar los movimientos registrados
        historial = self.repositorio.obtener_historial_vehiculo(
            id_vehiculo
        )

        return {
            "exito": True,
            "mensaje": "Historial obtenido correctamente",
            "id_vehiculo": id_vehiculo,
            "total": len(historial),
            "historial": historial
        }

    def listar_demos_vehiculo(self, id_vehiculo):
        """
        Consulta los DEMOS registrados
        para un vehículo IoT.
        """

        # Verificar que el vehículo exista
        vehiculo = self.repositorio.obtener_vehiculo(
            id_vehiculo
        )

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado",
                "total": 0,
                "demos": []
            }

        # Consultar los DEMOS del vehículo
        demos = self.repositorio.obtener_demos_vehiculo(
            id_vehiculo
        )

        return {
            "exito": True,
            "mensaje": "DEMOS obtenidos correctamente",
            "id_vehiculo": id_vehiculo,
            "total": len(demos),
            "demos": demos
        }

    def consultar_movimientos_demo(self, id_vehiculo, id_demo):
        """
        Consulta los movimientos programados
        de un DEMO perteneciente al vehículo.
        """

        # Validar identificadores
        if id_vehiculo <= 0 or id_demo <= 0:
            return {
                "exito": False,
                "mensaje": "Los identificadores deben ser mayores que cero"
            }

        # Verificar que exista el vehículo
        vehiculo = self.repositorio.obtener_vehiculo(id_vehiculo)

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado"
            }

        # Verificar que el DEMO pertenezca al vehículo
        demos = self.repositorio.obtener_demos_vehiculo(id_vehiculo)

        demo = next(
            (
                d for d in demos
                if d["id_demo"] == id_demo
            ),
            None
        )

        if demo is None:
            return {
                "exito": False,
                "mensaje": "DEMO no encontrado para este vehículo"
            }

        # Consultar movimientos del DEMO
        movimientos = self.repositorio.obtener_movimientos_demo(id_demo)

        # Ordenar por el campo 'orden'
        movimientos = sorted(
            movimientos,
            key=lambda movimiento: movimiento["orden"]
        )

        return {
            "exito": True,
            "mensaje": "Movimientos del DEMO obtenidos correctamente",
            "id_vehiculo": id_vehiculo,
            "id_demo": id_demo,
            "nombre_demo": demo["nombre"],
            "total": len(movimientos),
            "movimientos": movimientos
        }

    async def ejecutar_demo(self, id_vehiculo, id_demo, enviar_evento):
        """
        Ejecuta los movimientos de un DEMO en orden,
        actualiza el estado y envía eventos por WebSocket.

        No registra movimientos en el historial.
        """

        import asyncio

        # Consultar y validar el DEMO
        resultado = self.consultar_movimientos_demo(
            id_vehiculo,
            id_demo
        )

        if not resultado["exito"]:
            return resultado

        # Verificar que el vehículo y el DEMO estén activos
        vehiculo = self.repositorio.obtener_vehiculo(id_vehiculo)
        demos = self.repositorio.obtener_demos_vehiculo(id_vehiculo)

        demo = next(
            (d for d in demos if d["id_demo"] == id_demo),
            None
        )

        if (
            vehiculo["activo"] != 1
            or demo is None
            or demo["activo"] != 1
        ):
            return {
                "exito": False,
                "mensaje": "El vehículo o el DEMO está inactivo"
            }

        movimientos = resultado["movimientos"]

        if not movimientos:
            return {
                "exito": False,
                "mensaje": "El DEMO no tiene movimientos"
            }

        
        # Validar todos los tiempos antes de iniciar
        for movimiento in movimientos:
            duracion = movimiento["duracion_ms"]
            pausa = movimiento["pausa_ms"]

            if (
                duracion is None
                or pausa is None
                or duracion < 0
                or pausa < 0
            ):
                return {
                    "exito": False,
                    "mensaje": "El DEMO contiene tiempos inválidos"
                }
            
        # Verificar que todos los comandos del DEMO
        # pertenezcan al vehículo y estén activos
        comandos = await asyncio.to_thread(
            self.repositorio.obtener_comandos_vehiculo,
            id_vehiculo
        )

        comandos_activos = {
            comando["id_comando"]
            for comando in comandos
            if comando["activo"] == 1
        }

        for movimiento in movimientos:
            if movimiento["id_comando"] not in comandos_activos:
                return {
                    "exito": False,
                    "mensaje": (
                        "El DEMO contiene comandos "
                        "inactivos o no válidos para el vehículo"
                    )
                }



        # Ejecutar la secuencia programada
        for movimiento in movimientos:
            duracion = movimiento["duracion_ms"]
            pausa = movimiento["pausa_ms"]

            if duracion < 0 or pausa < 0:
                return {
                    "exito": False,
                    "mensaje": "El DEMO contiene tiempos inválidos"
                }

            # Actualizar estado sin registrar historial
            await asyncio.to_thread(
                self.repositorio.actualizar_estado_demo,
                id_vehiculo,
                movimiento["id_comando"]
            )

            # Notificar el movimiento mediante WebSocket
            await enviar_evento({
                "tipo": "MOVIMIENTO_DEMO",
                "id_vehiculo": id_vehiculo,
                "id_demo": id_demo,
                "orden": movimiento["orden"],
                "id_comando": movimiento["id_comando"],
                "comando": movimiento["comando"],
                "codigo": movimiento["codigo"],
                "duracion_ms": duracion,
                "pausa_ms": pausa
            })

            # Respetar la duración y pausa del movimiento
            await asyncio.sleep((duracion + pausa) / 1000)

        return {
            "exito": True,
            "mensaje": "DEMO ejecutado correctamente",
            "id_vehiculo": id_vehiculo,
            "id_demo": id_demo,
            "total_movimientos": len(movimientos)
        }
