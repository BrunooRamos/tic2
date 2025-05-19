from Database.Queries import Queries
from sqlalchemy.orm import Session
from statistics import mean
from datetime import datetime, timezone
from Database.models.Info import Info
import requests
import json
import Criptografia

class ProcessToEC2:
    def __init__(self, raspberry_id = "rpi-001", api_endpoint="http://18.190.33.134:5000", session=None):
        self.api_endpoint = f"{api_endpoint}/measurements/{raspberry_id}" # Acá hay que decirle a Rodri 
        self.session = session                                            # que corrija el endpoint
        self.raspberry_id = raspberry_id                                  # y ponga la nueva id de la raspi

        Criptografia.ensure_keys(raspberry_id)

    def _build_signed_request(self, data: dict) -> dict:
        
        """
        Devuelve un JSON que incluye:
         - raspi_id
         - timestamp
         - data
         - signature (base64)
        """

        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "raspi_id": self.raspberry_id,
            "timestamp": timestamp,
            "data": data
        }

        # Convertir a bytes siempre de la misma forma
        payload_bytes = json.dumps(payload, sort_keys = True).encode("utf-8")
        
        # Firmar
        sig = Criptografia.sign_payload(payload_bytes)

        # Inyectar la firma
        payload["signature"] = sig
        return payload

    def send_to_api(self, data: dict) -> bool:
        
        """
        Envía los datos firmados a la API externa.
        """

        # Construir el payload firmado
        signed_payload = self._build_signed_request(data)

        try:
            response = requests.post(self.api_endpoint, json = signed_payload, timeout = 5)
            print(response)
            
            if response.status_code == 201:
                print("Datos enviados a la API de EC2 con exito.")
                return True
            else:
                print(f"Error al enviar datos: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"Excepción al enviar datos a la API: {e}")
            return False

    def process(self, session: Session):
        
        """
        Procesa las entradas no procesadas, calcula promedios,
        guarda un único registro resumen y elimina las entradas originales.
        """

        data = Queries.get_unprocessed_data(session)

        if not data:
            print("No hay datos no procesados.")
            return

        # Calcular promedios
        avg_humidity = mean([d.humidity for d in data])
        avg_temperature = mean([d.temperature for d in data])
        avg_co2 = mean([d.co2 for d in data])
        avg_people = round(mean([d.people for d in data]))

        # Tomamos el raspberry_id del primero (asumiendo que son del mismo)
        raspberry_id = data[0].raspberry_id

        # Crear una nueva entrada con el resumen
        summarized_entry = Info(
            raspberry_id = raspberry_id,
            people = avg_people,
            humidity = avg_humidity,
            temperature = avg_temperature,
            co2 = avg_co2,
            timestamp = datetime.now(),
            processed = True
        )

        # Eliminar las entradas originales
        latest_ts = data[0].timestamp
        Queries.delete_data_from_date(session, latest_ts)

        # Insertar entrada resumida
        Queries.insert_data(session, summarized_entry)
        print("Datos procesados, resumidos y antiguos eliminados.")

        # Enviar a la API
        message = {
            "people": avg_people,
            "humidity": avg_humidity,
            "temperature": avg_temperature,
            "co2": avg_co2
        }

        self.send_to_api(message)
