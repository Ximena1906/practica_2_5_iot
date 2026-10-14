
from app.repositories.vehiculo_repository import VehiculoRepository


def probar_vehiculos():

    print("\n===== PRUEBA DE VEHÍCULOS RDS =====")

    try:
        repositorio = VehiculoRepository()

        vehiculos = repositorio.obtener_vehiculos()

        print("Consulta ejecutada correctamente")
        print("Total de vehículos:", len(vehiculos))

        for vehiculo in vehiculos:
            print(vehiculo)

    except Exception as error:
        print("Error al consultar vehículos:")
        print(type(error).__name__, str(error))

    print("==================================")


if __name__ == "__main__":
    probar_vehiculos()
