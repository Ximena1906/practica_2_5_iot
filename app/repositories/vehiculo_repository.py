
from app.config.database import Database


class VehiculoRepository:
    """
    Repositorio encargado de consultar
    los vehículos almacenados en Amazon RDS.
    """

    def __init__(self):
        self.db = Database()

    def obtener_vehiculos(self):
        """
        Ejecuta el procedimiento almacenado
        sp_obtener_vehiculos.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:

                cursor.callproc("sp_obtener_vehiculos")

                vehiculos = cursor.fetchall()

            return vehiculos

        finally:
            conexion.close()


    def obtener_vehiculo(self, id_vehiculo):
        """
        Consulta un vehículo específico
        mediante su ID.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.callproc(
                    "sp_obtener_vehiculo",
                    (id_vehiculo,)
                )

                vehiculo = cursor.fetchone()

            return vehiculo

        finally:
            conexion.close()

    def obtener_comandos_vehiculo(self, id_vehiculo):
        """
        Obtiene los comandos disponibles
        para un vehículo específico.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.callproc(
                    "sp_obtener_comandos_vehiculo",
                    (id_vehiculo,)
                )

                comandos = cursor.fetchall()

            return comandos

        finally:
            conexion.close()

    def obtener_estado_vehiculo(self, id_vehiculo):
        """
        Consulta el estado actual
        de un vehículo IoT.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.callproc(
                    "sp_obtener_estado",
                    (id_vehiculo,)
                )

                estado = cursor.fetchone()

            return estado

        finally:
            conexion.close()

    def ejecutar_movimiento(self, id_vehiculo, id_comando):
        """
        Actualiza el estado del vehículo
        y registra el movimiento en el historial.

        Ambas operaciones se realizan
        dentro de una misma transacción.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:

                # Actualizar el estado del vehículo
                cursor.callproc(
                    "sp_actualizar_estado",
                    (id_vehiculo, id_comando, 1)
                )

                # Registrar el movimiento individual
                cursor.callproc(
                    "sp_registrar_historial",
                    (id_vehiculo, id_comando, "INDIVIDUAL")
                )

            # Confirmar ambas operaciones
            conexion.commit()

            return True

        except Exception:
            # Revertir ambas operaciones si ocurre un error
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def obtener_historial_vehiculo(self, id_vehiculo):
        """
        Consulta el historial de movimientos
        de un vehículo IoT.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.callproc(
                    "sp_obtener_historial",
                    (id_vehiculo,)
                )

                historial = cursor.fetchall()

            return historial

        finally:
            conexion.close()

    def obtener_demos_vehiculo(self, id_vehiculo):
        """
        Consulta los DEMOS registrados
        para un vehículo IoT.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.callproc(
                    "sp_obtener_demos",
                    (id_vehiculo,)
                )

                demos = cursor.fetchall()

            return demos

        finally:
            conexion.close()

    def obtener_movimientos_demo(self, id_demo):
        """
        Consulta los movimientos programados
        dentro de un DEMO.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.callproc(
                    "sp_obtener_movimientos_demo",
                    (id_demo,)
                )

                movimientos = cursor.fetchall()

            return movimientos

        finally:
            conexion.close()

    def actualizar_estado_demo(self, id_vehiculo, id_comando):
        """
        Actualiza el estado del vehículo
        durante la ejecución de un DEMO.

        No registra movimientos en el historial.
        """

        conexion = self.db.conectar()

        try:
            with conexion.cursor() as cursor:

                cursor.callproc(
                    "sp_actualizar_estado",
                    (id_vehiculo, id_comando, 1)
                )

            conexion.commit()

            return True

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()
