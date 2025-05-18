import logging
from awscrt import mqtt
from awsiot import mqtt_connection_builder
import json
import time

# Configurar el logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Ajusta el nivel según necesites (DEBUG, INFO, WARNING, etc.)
)

# Parámetros de conexión (HARDCODEADOS)
clientId = "Raspberry"
host = "a2jyujvas35153-ats.iot.us-east-2.amazonaws.com"  # Endpoint de AWS IoT
rootCAPath = "credentials/root-CA.crt"                     # Ruta al certificado CA
privateKeyPath = "credentials/RaspberryPiGrupo13.private.key"  # Ruta a la clave privada
certificatePath = "credentials/RaspberryPiGrupo13.cert.pem"  # Ruta al certificado del dispositivo
topic = "RecepcionDatos"                          # Tópico para publicar y suscribirse

# Crear la conexión MQTT usando MTLS
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=host,
    port=8883,
    cert_filepath=certificatePath,
    pri_key_filepath=privateKeyPath,
    ca_filepath=rootCAPath,
    client_id=clientId,
    clean_session=False,
    keep_alive_secs=30,
    connect_timeout=60  # Timeout de 60 segundos
)

# ------------------ Callbacks de Conexión ------------------ #
def on_connection_interrupted(connection, error, **kwargs):
    logging.error(f"Conexión interrumpida. Error: {error}")

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    logging.info(f"Conexión reanudada. Código de retorno: {return_code}, session_present: {session_present}")
    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        logging.info("La sesión no se mantuvo. Re-suscribiendo a los tópicos existentes...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    logging.info(f"Resultados de re-suscripción: {resubscribe_results}")

def on_connection_success(connection, callback_data):
    logging.info(f"Conexión exitosa con código de retorno: {callback_data.return_code}, session_present: {callback_data.session_present}")

def on_connection_failure(connection, callback_data):
    logging.error(f"Conexión fallida con código de error: {callback_data.error}")

def on_connection_closed(connection, callback_data):
    logging.info("Conexión cerrada")

# ------------------ Callback para Mensajes ------------------ #
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    #logging.info(f"Mensaje recibido en el tópico '{topic}': {payload}")
    pass

# ------------------ Funciones de Conexión y Operación ------------------ #
def connect_to_iot_core():
    logging.info(f"Conectando a {host} con clientId '{clientId}'...")
    try:
        connect_future = mqtt_connection.connect()
        connect_future.result()
        logging.info("Conectado a AWS IoT Core!")
    except Exception as e:
        logging.error(f"Error al conectar: {e}")

def subscribe_to_topic():
    logging.info(f"Suscribiéndose al tópico '{topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )
    subscribe_result = subscribe_future.result()
    logging.info(f"Suscripción exitosa con QoS: {subscribe_result['qos']}")

def publish_data(payload):
    try:
        mensaje = json.dumps(payload)
        #logging.info(f"Publicando mensaje a tópico '{topic}': {mensaje}")
        mqtt_connection.publish(topic, mensaje, qos=mqtt.QoS.AT_LEAST_ONCE)
    except KeyboardInterrupt:
        logging.info("Finalizando la publicación de mensajes...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        logging.info("Desconectado de AWS IoT Core")

# ------------------ Bloque Principal ------------------ #
if __name__ == '__main__':
    # Configurar callbacks
    mqtt_connection.on_connection_interrupted = on_connection_interrupted
    mqtt_connection.on_connection_resumed = on_connection_resumed
    mqtt_connection.on_connection_success = on_connection_success
    mqtt_connection.on_connection_failure = on_connection_failure
    mqtt_connection.on_connection_closed = on_connection_closed

    # Conectarse a AWS IoT Core
    connect_to_iot_core()

    # Suscribirse al tópico para recibir mensajes
    subscribe_to_topic()

    # Publicar mensajes de manera continua
    publish_data()
