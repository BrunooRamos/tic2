import os

import json, requests
from datetime import datetime, timezone
from seguridad.criptografia import Cripto
from cryptography.hazmat.primitives import serialization

api_endpoint = os.getenv("API_ENDPOINT")
raspberry_id = int(os.getenv("RASPBERRY_ID"))
                
                
def enviarClave(self):
    cripto = Cripto()

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
    enviarClave()