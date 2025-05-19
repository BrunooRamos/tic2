import json, requests
from datetime import datetime, timezone
import Criptografia

class ProcessToEC2:
    def __init__(self, raspberry_id="rpi-001", api_endpoint=..., session=None):
        self.raspberry_id = raspberry_id
        self.api_base     = api_endpoint.rstrip("/")
        self.session      = session

        # 1) Generar/asegurar claves
        Criptografia.ensure_keys(self.raspberry_id)

        # 2) Registrar public key en el servidor
        self._register_device()

    def _register_device(self):
        # Leer PEM de la clave pública
        with open(Criptografia.PUBLIC_KEY_FILE, "r") as f:
            public_pem = f.read()

        # Construir payload de registro
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "raspi_id":   self.raspberry_id,
            "timestamp":  timestamp,
            "public_key": public_pem
        }

        # Serializar y firmar igual que un mensaje normal
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature     = Criptografia.sign_payload(payload_bytes)
        payload["signature"] = signature

        # Hacer POST al endpoint /devices/register
        url = f"{self.api_base}/devices/register"
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code != 201:
            raise RuntimeError(f"Registro dispositivo falló: {resp.status_code} {resp.text}")
        print("Registro de dispositivo exitoso.")
