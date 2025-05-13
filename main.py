import time
from Camara.count_people import get_people_stream
from Database.models.info import Info
from Database.queries import Queries
from Sensor.get_measure import get_random_measure

from Sensor.SensorScript import read_sensor

from iot_handler import connect_to_iot_core, subscribe_to_topic, publish_data
from Database.db_handler import DatabaseHandler
from Process_to_EC2.procces import ProcessToEC2

def main():
    connect_to_iot_core()
    subscribe_to_topic()

    db_handler = DatabaseHandler()
    _, Session = db_handler.connect_to_database()
    session = Session()

    # Inicializar el proceso de EC2
    process_to_ec2 = ProcessToEC2( session=session)

    last_process_time = time.time()

    for people_count in get_people_stream():
        #medida = get_random_measure()

        # Usamos las medidas reales del sensor
        medida = read_sensor()
        if medida is None:
            print("Error al leer el sensor. Intentando de nuevo...")
            continue
        # Enviar datos al servidor EC2

        mensaje = {
            "people": people_count,
            "humidity": medida["humidity"],
            "temperature": medida["temperature"],
            "co2": medida["co2"]
        }
        publish_data(mensaje)

        info = Info(
            raspberry_id=1,
            people=people_count,
            humidity=medida["humidity"],
            temperature=medida["temperature"],
            co2=medida["co2"]
        )
        Queries.insert_data(session, info)

        # Procesar cada 10 segundos
        if time.time() - last_process_time >= 10:
            # Procesar los datos no procesados
            process_to_ec2.process(session)
            last_process_time = time.time()

    session.close()

if __name__ == "__main__":
    main()
