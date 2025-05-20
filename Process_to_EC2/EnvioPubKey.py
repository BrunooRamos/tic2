import json, requests
from datetime import datetime, timezone
import Criptografia

class EnvioClavePublica:
    def __init__(self, raspberry_id="rpi-001", api_endpoint=..., session=None):
        self.raspberry_id = raspberry_id
        self.api_base     = api_endpoint.rstrip("/") # Esto hay que configurarlo cuando tengamos
        self.session      = session                  # el endpoint

        # 1) Generar/asegurar claves
        Criptografia.crearKeys()

        # 2) Registrar public key en el servidor
        self.enviarClave()

    def enviarClave(self):
        
        # Leer PEM de la clave pública
        public_key = Criptografia.load_public_key()

        # Construir payload de registro
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "raspi_id":   self.raspberry_id,
            "timestamp":  timestamp,
            "public_key": public_key
        }

        # Serializar y firmar 
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature     = Criptografia.sign_payload(payload_bytes)
        payload["signature"] = signature

        # Hacer POST al endpoint /devices/register
        url = f"{self.api_base}/devices/register"
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code != 201:
            raise RuntimeError(f"No se pudo mandar el payload: {resp.status_code} {resp.text}")
        print("Public Key enviada con éxito.")
