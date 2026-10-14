
from fastapi import FastAPI

from app.routers.vehiculo_router import router as vehiculo_router

from app.routers.websocket_router import router as websocket_router



app = FastAPI(
    title="API Vehículo IoT",
    description="Práctica 2.5 - API para vehículo IoT con FastAPI y Amazon RDS",
    version="1.0.0"
)


app.include_router(vehiculo_router)

app.include_router(websocket_router)



@app.get("/", tags=["Inicio"])
def inicio():
    return {
        "mensaje": "Bienvenido a la API Vehículo IoT",
        "estado": "Servidor funcionando correctamente",
        "practica": "2.5"
    }
