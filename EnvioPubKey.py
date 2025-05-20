import json, requests
from datetime import datetime, timezone
from Seguridad import Criptografia
from cryptography.hazmat.primitives import serialization

class EnvioClavePublica:
    def __init__(self, raspberry_id = 1, api_endpoint="http://10.228.119.40:5000", session=None):
        self.raspberry_id = raspberry_id
        self.api_endpoint = f"{api_endpoint}/register_device"
        self.session      = session                  

    def enviarClave(self):

        cripto = Criptografia()

        cripto.crearKeys()  # Generar las claves si no existen
        
        # Leer PEM de la clave pública
        public_key_obj = cripto.load_public_key()

        public_key_pem = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('ascii')  # Convertir bytes a string
        
        # Construir payload de registro
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "raspi_id":   self.raspberry_id,
            "timestamp":  timestamp,
            "public_key": public_key_pem
        }

        # Serializar y firmar 
        payload_bytes = json.dumps(payload, sort_keys = True).encode("utf-8")
        signature     = cripto.firmarPayload(payload_bytes)
        payload["signature"] = signature

        # Hacer POST al endpoint /devices/register
        resp = requests.post(self.api_endpoint, json=payload, timeout=5)
        if resp.status_code != 201:
            raise RuntimeError(f"No se pudo mandar el payload: {resp.status_code} {resp.text}")
        print("Public Key enviada con éxito.")

if __name__ == "__main__":
    # Test
    envio = EnvioClavePublica()
    envio.enviarClave()

