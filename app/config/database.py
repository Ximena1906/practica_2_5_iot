
import os
import pymysql

from pathlib import Path
from dotenv import load_dotenv
from pymysql.cursors import DictCursor


# Cargar variables de entorno
load_dotenv()


class Database:
    """
    Clase encargada de administrar
    la conexión segura con Amazon RDS MySQL.
    """

    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")

    def conectar(self):
        """
        Establece una conexión segura
        con Amazon RDS MySQL.
        """

        # Ruta del certificado de Amazon RDS
        ruta_certificado = (
            Path(__file__).resolve().parents[2]
            / "certs"
            / "global-bundle.pem"
        )

        if not ruta_certificado.is_file():
            raise FileNotFoundError(
                "No se encontró el certificado de Amazon RDS"
            )

        conexion = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=DictCursor,
            connect_timeout=10,
            read_timeout=15,
            write_timeout=15,
            autocommit=False,
            ssl_ca=str(ruta_certificado),
            ssl_verify_cert=True,
            ssl_verify_identity=True
        )

        return conexion

    def verificar_conexion(self):
        """
        Comprueba que la conexión funciona.
        """

        conexion = None

        try:
            conexion = self.conectar()

            with conexion.cursor() as cursor:
                cursor.execute("SELECT DATABASE() AS bd")
                resultado = cursor.fetchone()

            return {
                "exito": True,
                "mensaje": "Conexión exitosa con Amazon RDS",
                "base_datos": resultado["bd"]
            }

        except pymysql.MySQLError as error:
            print("Tipo de error:", type(error).__name__)
            print(
                "Código de error:",
                error.args[0] if error.args else "Desconocido"
            )
            print("Detalle:", str(error))

            return {
                "exito": False,
                "mensaje": "No se pudo conectar con Amazon RDS"
            }

        except FileNotFoundError as error:
            print("Error de certificado:", str(error))

            return {
                "exito": False,
                "mensaje": "No se encontró el certificado SSL"
            }

        finally:
            if conexion is not None:
                conexion.close()
