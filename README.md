
# 🚜 Práctica 2.5 – API IoT con FastAPI y AWS RDS

## 📌 Descripción

API REST desarrollada en Python con FastAPI para administrar y controlar vehículos IoT mediante una base de datos MySQL alojada en Amazon RDS.

El proyecto permite consultar vehículos, ejecutar comandos de movimiento, visualizar su estado, consultar el historial y ejecutar demostraciones de movimientos.

## 🛠️ Tecnologías utilizadas

- Python
- FastAPI
- MySQL
- Amazon RDS
- WebSocket
- PyMySQL
- Pydantic
- Git y GitHub
- Thunder Client

## 📂 Estructura del proyecto

```text
practica_2_5_iot/
├── app/
│   ├── config/
│   ├── repositories/
│   ├── routers/
│   ├── services/
│   └── websocket/
├── certs/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Instalación

**1. Clonar el repositorio**

```bash
git clone https://github.com/Ximena1906/practica_2_5_iot.git
cd practica_2_5_iot
```

**2. Crear un entorno virtual**

```powershell
py -m venv .venv
```

**3. Activar el entorno virtual en Windows**

```powershell
.\.venv\Scripts\Activate.ps1
```

**4. Instalar las dependencias**

```powershell
pip install -r requirements.txt
```

**5. Configurar las variables de entorno**

Crear un archivo `.env` a partir de `.env.example` y completar los datos de conexión a MySQL en AWS RDS.

> 🔒 Nunca publicar el archivo `.env` ni compartir contraseñas.

## 🚀 Ejecución de la API

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

La API estará disponible en:

http://127.0.0.1:8000

Documentación interactiva Swagger:

http://127.0.0.1:8000/docs

## 📡 Funcionalidades principales

- Consulta de vehículos registrados.
- Consulta del estado actual de un vehículo.
- Consulta de comandos disponibles.
- Ejecución de movimientos individuales.
- Registro del historial de movimientos individuales.
- Consulta de demostraciones y sus movimientos.
- Ejecución de secuencias de demostración.
- Comunicación en tiempo real mediante WebSocket.

## 🧪 Pruebas

Las operaciones GET y POST se pueden probar mediante Swagger y Thunder Client.

La comunicación WebSocket permite recibir eventos relacionados con los movimientos y la finalización de las demostraciones.

## 🔐 Seguridad

Las credenciales de AWS RDS se administran mediante variables de entorno.

La conexión a MySQL utiliza certificados SSL para verificar la comunicación con Amazon RDS.

## 👩‍💻 Autora

Ximena Nava Escamilla

Ingeniería en Sistemas Computacionales
