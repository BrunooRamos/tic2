import os
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

KEY_DIR = os.path.expanduser("~/.raspi_keys")
PRIVATE_KEY_FILE = os.path.join(KEY_DIR, "private_key.pem")
PUBLIC_KEY_FILE  = os.path.join(KEY_DIR, "public_key.pem")

# ---------------- Importante ----------------
# 1) Los datos que estamos mandando al IOT Core (la parte del real-time)
# no los estamos firmando, solo estamos firmando por ahora los datos que
# mandamos a la API de EC2. Esto hay que verlo después cuando se encare el real-time
# 2) Implementar algo que evite los replay attacks. Por ahora no lo estamos haciendo y pienso 
# que sería ir muy al hueso
# --------------------------------------------

def crearKeys():
    
    """
    Si no existen, genera par de claves RSA (2048 bits)
    y las salva en ~/.raspi_keys.
    """

    os.makedirs(KEY_DIR, exist_ok = True)
    if not os.path.exists(PRIVATE_KEY_FILE):
        
        # Generar par de claves
        private_key = rsa.generate_private_key(
            public_exponent = 65537,
            key_size = 2048,
        )
        public_key = private_key.public_key()

        # Serializar y guardar
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding = serialization.Encoding.PEM,
                    format = serialization.PrivateFormat.PKCS8,
                    encryption_algorithm = serialization.NoEncryption()
                )
            )

        with open(PUBLIC_KEY_FILE, "wb") as f:  
            f.write(
                public_key.public_bytes(
                    encoding = serialization.Encoding.PEM,
                    format = serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

def load_private_key():
    
    """
    Carga la clave privada desde PEM.
    """

    with open(PRIVATE_KEY_FILE, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password = None)

def load_public_key():
    """
    Carga la clave pública (por si la necesitamos localmente).
    """
    
    with open(PUBLIC_KEY_FILE, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def firmarPayload(payload_bytes: bytes) -> str:
    """
    Firma el payload con PSS+SHA256 y devuelve
    la firma en base64 (string).
    """
    
    priv = load_private_key()
    signature = priv.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode("ascii")
