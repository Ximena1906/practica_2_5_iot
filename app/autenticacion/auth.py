
import os
import hmac
from dotenv import load_dotenv

load_dotenv()


def validar_token(token_recibido: str, tipo_cliente: str) -> bool:
    """
    Valida la credencial según el tipo de cliente.
    No imprime ni devuelve los tokens privados.
    """

    variables = {
        "esp32": "ESP32_AUTH_TOKEN",
        "control": "CONTROL_AUTH_TOKEN"
    }

    variable = variables.get(tipo_cliente)

    if not variable or not token_recibido:
        return False

    token_esperado = os.getenv(variable, "")

    if not token_esperado:
        return False

    return hmac.compare_digest(
        token_recibido,
        token_esperado
    )
