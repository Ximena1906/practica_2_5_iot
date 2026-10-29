
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routers.vehiculo_router import router as vehiculo_router
from app.routers.websocket_router import router as websocket_router
from app.websocket.internal_notifications import router as internal_router


app = FastAPI(
    title="API Vehículo IoT",
    description="Práctica 2.5 - API para vehículo IoT con FastAPI y Amazon RDS",
    version="1.0.0"
)


app.include_router(vehiculo_router)

app.include_router(websocket_router)

app.include_router(internal_router)


# Carpeta donde se encuentra Pink Night Control
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/", tags=["Inicio"], include_in_schema=False)
def inicio():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api", tags=["Inicio"])
def informacion_api():
    return {
        "mensaje": "Bienvenido a la API Vehículo IoT",
        "estado": "Servidor funcionando correctamente",
        "practica": "2.5"
    }
