from flask import request, jsonify
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Supongamos que guardaste en tu BD:
#   raspi_id → public_key_pem

@app.route("/measurements/<raspi_id>", methods=["POST"])
def measurements(raspi_id):
    body = request.get_json()
    sig_b64   = body.pop("signature", None)
    if not sig_b64:
        return jsonify({"error":"falta signature"}), 400

    # Reconstruir payload bytes igual que en la Raspi
    payload_bytes = json.dumps(body, sort_keys=True).encode("utf-8")

    # Obtener clave pública de tu almacenamiento
    pub_pem = get_public_key_from_db(raspi_id)
    pub = serialization.load_pem_public_key(pub_pem.encode())

    # Verificar firma
    signature = base64.b64decode(sig_b64)
    try:
        pub.verify(
            signature,
            payload_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception:
        return jsonify({"error":"firma inválida"}), 403

    # Si pasó la verificación, procesar body["data"], body["timestamp"], etc.
    save_measurement(raspi_id, body["data"], body["timestamp"])
    return "", 201
