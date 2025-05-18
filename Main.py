import time
from Camara.Count_people import get_people_stream
from Database.models.Info import Info
from Database.Queries import Queries
from Sensor.Get_measure import get_random_measure

from Sensor.SensorScript import read_sensor

from Iot_handler import connect_to_iot_core, subscribe_to_topic, publish_data
from Database.DB_handler import DatabaseHandler
from Process_to_EC2.Process import ProcessToEC2

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
