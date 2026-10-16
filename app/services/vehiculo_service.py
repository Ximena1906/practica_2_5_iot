
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

    def crear_vehiculo(
        self,
        nombre,
        modelo,
        descripcion,
        microcontrolador
    ):
        """
        Valida y registra un nuevo vehículo IoT.
        """

        if not nombre or not nombre.strip():
            return {
                "exito": False,
                "mensaje": "El nombre del vehículo es obligatorio"
            }

        if not modelo or not modelo.strip():
            return {
                "exito": False,
                "mensaje": "El modelo del vehículo es obligatorio"
            }

        if not microcontrolador or not microcontrolador.strip():
            return {
                "exito": False,
                "mensaje": "El microcontrolador es obligatorio"
            }

        self.repositorio.crear_vehiculo(
            nombre.strip(),
            modelo.strip(),
            descripcion.strip() if descripcion else "",
            microcontrolador.strip()
        )

        return {
            "exito": True,
            "mensaje": "Vehículo creado correctamente"
        }

    def actualizar_vehiculo(
        self,
        id_vehiculo,
        nombre,
        modelo,
        descripcion,
        microcontrolador,
        activo
    ):
        """
        Valida y actualiza un vehículo IoT.
        """

        if id_vehiculo <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador debe ser mayor que cero"
            }

        vehiculo = self.repositorio.obtener_vehiculo(id_vehiculo)

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado"
            }

        if not nombre or not nombre.strip():
            return {
                "exito": False,
                "mensaje": "El nombre del vehículo es obligatorio"
            }

        if not modelo or not modelo.strip():
            return {
                "exito": False,
                "mensaje": "El modelo del vehículo es obligatorio"
            }

        if not microcontrolador or not microcontrolador.strip():
            return {
                "exito": False,
                "mensaje": "El microcontrolador es obligatorio"
            }

        if activo not in (0, 1):
            return {
                "exito": False,
                "mensaje": "El estado activo debe ser 0 o 1"
            }

        self.repositorio.actualizar_vehiculo(
            id_vehiculo,
            nombre.strip(),
            modelo.strip(),
            descripcion.strip() if descripcion else "",
            microcontrolador.strip(),
            activo
        )

        return {
            "exito": True,
            "mensaje": "Vehículo actualizado correctamente",
            "id_vehiculo": id_vehiculo
        }

    def eliminar_vehiculo(self, id_vehiculo):
        """
        Verifica que el vehículo exista antes
        de solicitar su eliminación.
        
        La autorización deberá validarse
        en el endpoint protegido.
        """

        if id_vehiculo <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador debe ser mayor que cero"
            }

        vehiculo = self.repositorio.obtener_vehiculo(id_vehiculo)

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado"
            }

        self.repositorio.eliminar_vehiculo(id_vehiculo)

        return {
            "exito": True,
            "mensaje": "Vehículo eliminado correctamente",
            "id_vehiculo": id_vehiculo
        }

    def crear_comando(
        self,
        id_vehiculo,
        nombre,
        codigo,
        descripcion
    ):
        """
        Valida y crea un comando para un vehículo IoT.
        """

        if id_vehiculo <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador del vehículo debe ser mayor que cero"
            }

        vehiculo = self.repositorio.obtener_vehiculo(id_vehiculo)

        if vehiculo is None:
            return {
                "exito": False,
                "mensaje": "Vehículo no encontrado"
            }

        if not nombre or not nombre.strip():
            return {
                "exito": False,
                "mensaje": "El nombre del comando es obligatorio"
            }

        if codigo < 0:
            return {
                "exito": False,
                "mensaje": "El código del comando no puede ser negativo"
            }

        self.repositorio.crear_comando(
            id_vehiculo,
            nombre.strip(),
            codigo,
            descripcion.strip() if descripcion else ""
        )

        return {
            "exito": True,
            "mensaje": "Comando creado correctamente",
            "id_vehiculo": id_vehiculo
        }

    def actualizar_comando(
        self,
        id_comando,
        nombre,
        codigo,
        descripcion,
        activo
    ):
        """
        Valida y actualiza un comando IoT.
        """

        if id_comando <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador del comando debe ser mayor que cero"
            }

        if not nombre or not nombre.strip():
            return {
                "exito": False,
                "mensaje": "El nombre del comando es obligatorio"
            }

        if codigo < 0:
            return {
                "exito": False,
                "mensaje": "El código del comando no puede ser negativo"
            }

        if activo not in (0, 1):
            return {
                "exito": False,
                "mensaje": "El estado activo debe ser 0 o 1"
            }

        self.repositorio.actualizar_comando(
            id_comando,
            nombre.strip(),
            codigo,
            descripcion.strip() if descripcion else "",
            activo
        )

        return {
            "exito": True,
            "mensaje": "Comando actualizado correctamente",
            "id_comando": id_comando
        }

    def eliminar_comando(self, id_comando):
        """
        Valida el identificador y solicita
        la eliminación de un comando IoT.

        Requiere autorización antes de invocarse.
        """

        if id_comando <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador del comando debe ser mayor que cero"
            }

        self.repositorio.eliminar_comando(id_comando)

        return {
            "exito": True,
            "mensaje": "Solicitud de eliminación ejecutada correctamente",
            "id_comando": id_comando
        }

    def crear_demo(self, id_vehiculo, nombre, descripcion):
        """
        Valida y crea una DEMO para un vehículo IoT.
        """

        if id_vehiculo <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador del vehículo debe ser mayor que cero"
            }

        vehiculo = self.repositorio.obtener_vehiculo(id_vehiculo)

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

        if not nombre or not nombre.strip():
            return {
                "exito": False,
                "mensaje": "El nombre de la DEMO es obligatorio"
            }

        if len(nombre.strip()) > 80:
            return {
                "exito": False,
                "mensaje": "El nombre no puede superar los 80 caracteres"
            }

        if descripcion and len(descripcion.strip()) > 255:
            return {
                "exito": False,
                "mensaje": "La descripción no puede superar los 255 caracteres"
            }

        self.repositorio.crear_demo(
            id_vehiculo,
            nombre.strip(),
            descripcion.strip() if descripcion else ""
        )

        return {
            "exito": True,
            "mensaje": "DEMO creada correctamente",
            "id_vehiculo": id_vehiculo
        }

    def actualizar_demo(
        self,
        id_demo,
        nombre,
        descripcion,
        activo
    ):
        """
        Valida y actualiza una DEMO existente.
        """

        if id_demo <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador de la DEMO debe ser mayor que cero"
            }

        if not nombre or not nombre.strip():
            return {
                "exito": False,
                "mensaje": "El nombre de la DEMO es obligatorio"
            }

        if len(nombre.strip()) > 80:
            return {
                "exito": False,
                "mensaje": "El nombre no puede superar los 80 caracteres"
            }

        if descripcion and len(descripcion.strip()) > 255:
            return {
                "exito": False,
                "mensaje": "La descripción no puede superar los 255 caracteres"
            }

        if activo not in (0, 1):
            return {
                "exito": False,
                "mensaje": "El estado activo debe ser 0 o 1"
            }

        self.repositorio.actualizar_demo(
            id_demo,
            nombre.strip(),
            descripcion.strip() if descripcion else "",
            activo
        )

        return {
            "exito": True,
            "mensaje": "DEMO actualizada correctamente",
            "id_demo": id_demo
        }

    def eliminar_demo(self, id_demo):
        """
        Valida el identificador y solicita
        la eliminación de una DEMO.

        Requiere autorización antes de invocarse.
        """

        if id_demo <= 0:
            return {
                "exito": False,
                "mensaje": "El identificador de la DEMO debe ser mayor que cero"
            }

        self.repositorio.eliminar_demo(id_demo)

        return {
            "exito": True,
            "mensaje": "Solicitud de eliminación ejecutada correctamente",
            "id_demo": id_demo
        }

    def agregar_movimiento_demo(
        self,
        id_demo,
        id_comando,
        orden,
        duracion_ms,
        pausa_ms
    ):
        """
        Valida y agrega un movimiento
        a una DEMO existente.
        """

        if id_demo <= 0 or id_comando <= 0:
            return {
                "exito": False,
                "mensaje": "Los identificadores deben ser mayores que cero"
            }

        if orden <= 0:
            return {
                "exito": False,
                "mensaje": "El orden debe ser mayor que cero"
            }

        if duracion_ms < 0 or pausa_ms < 0:
            return {
                "exito": False,
                "mensaje": "La duración y la pausa no pueden ser negativas"
            }

        self.repositorio.agregar_movimiento_demo(
            id_demo,
            id_comando,
            orden,
            duracion_ms,
            pausa_ms
        )

        return {
            "exito": True,
            "mensaje": "Movimiento agregado correctamente a la DEMO",
            "id_demo": id_demo,
            "id_comando": id_comando
        }

    def actualizar_movimiento_demo(
        self,
        id_demo_movimiento,
        id_comando,
        orden,
        duracion_ms,
        pausa_ms
    ):
        """
        Valida y actualiza un movimiento
        existente dentro de una DEMO.
        """

        if id_demo_movimiento <= 0 or id_comando <= 0:
            return {
                "exito": False,
                "mensaje": "Los identificadores deben ser mayores que cero"
            }

        if orden <= 0:
            return {
                "exito": False,
                "mensaje": "El orden debe ser mayor que cero"
            }

        if duracion_ms < 0 or pausa_ms < 0:
            return {
                "exito": False,
                "mensaje": "La duración y la pausa no pueden ser negativas"
            }

        self.repositorio.actualizar_movimiento_demo(
            id_demo_movimiento,
            id_comando,
            orden,
            duracion_ms,
            pausa_ms
        )

        return {
            "exito": True,
            "mensaje": "Movimiento DEMO actualizado correctamente",
            "id_demo_movimiento": id_demo_movimiento
        }

    def eliminar_movimiento_demo(self, id_demo_movimiento):
        """
        Valida el identificador y solicita
        la eliminación de un movimiento DEMO.

        Requiere autorización antes de invocarse.
        """

        if id_demo_movimiento <= 0:
            return {
                "exito": False,
                "mensaje": (
                    "El identificador del movimiento "
                    "debe ser mayor que cero"
                )
            }

        self.repositorio.eliminar_movimiento_demo(
            id_demo_movimiento
        )

        return {
            "exito": True,
            "mensaje": "Movimiento DEMO eliminado correctamente",
            "id_demo_movimiento": id_demo_movimiento
        }
