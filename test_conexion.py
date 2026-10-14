
from app.config.database import Database

# Crear objeto de conexión
db = Database()

# Verificar conexión con Amazon RDS
resultado = db.verificar_conexion()

print("\n===== PRUEBA DE CONEXIÓN RDS =====")
print("Éxito:", resultado["exito"])
print("Mensaje:", resultado["mensaje"])

if resultado["exito"]:
    print("Base de datos:", resultado["base_datos"])

print("=================================")
