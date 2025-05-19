import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Funciones que ahora reciben el raspi_id para aislar claves por dispositivo

# Este código es el mismo que el de Criptografia.py pero adaptado para que
# cada raspi tenga su par de claves si el día de mañana se quiere probar hacer
# un despliegue masivo de raspberry desde una unica computadora. Porque sino sucede que
# con el código de Criptografia, todas las raspberry tendrían las mismas claves privadas y publicas

# Hay que chequear este código porque no lo probé

def _get_key_paths(raspi_id: str):
    """
    Retorna (KEY_DIR, PRIVATE_KEY_FILE, PUBLIC_KEY_FILE) específicos para cada raspi_id.
    """
    base_dir = os.path.expanduser("~/.raspi_keys")
    key_dir  = os.path.join(base_dir, raspi_id)
    priv_file = os.path.join(key_dir, "private_key.pem")
    pub_file  = os.path.join(key_dir, "public_key.pem")
    return key_dir, priv_file, pub_file


def ensure_keys(raspi_id: str):
    """
    Si no existen las claves para este raspi_id, las genera (RSA 2048 bits)
    y las guarda en ~/.raspi_keys/{raspi_id}/
    """
    key_dir, priv_path, pub_path = _get_key_paths(raspi_id)
    os.makedirs(key_dir, exist_ok=True)

    # Solo genera si no existe la clave privada
    if not os.path.exists(priv_path):
        # 1) Generar par de claves
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # 2) Serializar y guardar clave privada (PEM, sin cifrado)
        with open(priv_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # 3) Serializar y guardar clave pública (PEM)
        with open(pub_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )


def load_private_key(raspi_id: str):
    """
    Carga la clave privada PEM para el raspi_id.
    """
    _, priv_path, _ = _get_key_paths(raspi_id)
    with open(priv_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key(raspi_id: str):
    """
    Carga la clave pública PEM para el raspi_id.
    """
    _, _, pub_path = _get_key_paths(raspi_id)
    with open(pub_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def sign_payload(raspi_id: str, payload_bytes: bytes) -> str:
    """
    Firma el payload con PSS+SHA256 usando la clave privada de raspi_id.
    Devuelve la firma en base64 (string).
    """
    private_key = load_private_key(raspi_id)
    signature = private_key.sign(
        payload_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    # Base64 para que sea JSON-friendly
    return base64.b64encode(signature).decode("ascii")
