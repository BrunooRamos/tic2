"""
Módulo de procesamiento y envío de datos al servidor EC2.

Este módulo se encarga de:
1. Procesar los datos recolectados
2. Calcular promedios
3. Firmar y enviar los datos al servidor
4. Manejar la limpieza de datos procesados
"""

import json
import requests
import os
import logging
from datetime import datetime, timezone, timedelta
from statistics import mean
from sqlalchemy.orm import Session

from database.models.Info import Info
from database.queries import Queries
from seguridad.criptografia import Cripto

# Configuración de logging
logger = logging.getLogger(__name__)

api_endpoint = os.getenv("API_ENDPOINT")
raspberry_id = int(os.getenv("RASPBERRY_ID"))

class ProcessToEC2:
    """
    Clase para procesar y enviar datos al servidor EC2.

    Esta clase maneja:
    - Procesamiento de datos no procesados
    - Cálculo de promedios
    - Firma de datos
    - Envío al servidor
    - Limpieza de datos procesados
    """

    def __init__(self, session=None):
        """
        Inicializa el procesador de datos.

        Args:
            session: Sesión de base de datos SQLAlchemy (opcional)
        """
        self.api_endpoint = f"{api_endpoint}/measurements/{raspberry_id}"  
        self.session = session                                            
        self.raspberry_id = raspberry_id                                  

        Cripto.crearKeys()
        logger.info(f"Procesador inicializado para Raspberry ID: {raspberry_id}")

    def firmarRequest(self, data: dict) -> dict:
        """
        Firma los datos para su envío seguro.

        Args:
            data: Diccionario con los datos a firmar

        Returns:
            dict: Payload firmado con:
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
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        
        # Firmar
        sig = Cripto.firmarPayload(payload_bytes)

        # Inyectar la firma
        payload["signature"] = sig
        logger.debug(f"Payload firmado: {payload}")
        return payload

    def send_to_api(self, data: dict) -> dict:
        """
        Envía los datos firmados a la API externa.

        Args:
            data: Diccionario con los datos a enviar

        Returns:
            dict: Resultado del envío con:
                - status_code: Código de respuesta HTTP
                - error: Mensaje de error (si existe)
        """
        # Construir el payload firmado
        signed_payload = self.firmarRequest(data)

        try:
            logger.info("Enviando datos a la API")
            response = requests.post(self.api_endpoint, json=signed_payload, timeout=5)
            logger.info(f"Respuesta de la API: {response.status_code}")
            
            if response.status_code == 201:
                logger.info("Datos enviados a la API de EC2 con éxito.")
                return {"status_code": response.status_code}
            else:
                error_msg = f"Error al enviar datos: {response.status_code}"
                logger.error(error_msg)
                return {
                    "status_code": response.status_code,
                    "error": error_msg
                }
        
        except Exception as e:
            error_msg = f"Excepción al enviar datos a la API: {str(e)}"
            logger.error(error_msg)
            return {
                "status_code": 500,
                "error": error_msg
            }

    def procesar_entradas(self, session: Session) -> dict:
        """
        Procesa las entradas no procesadas y envía los datos al servidor.

        Args:
            session: Sesión de base de datos SQLAlchemy

        Returns:
            dict: Resultado del procesamiento con:
                - status_code: Código de respuesta HTTP
                - error: Mensaje de error (si existe)
                - message: Mensaje informativo (si existe)
        """
        try:
            logger.info("Obteniendo datos no procesados")
            data = Queries.get_unprocessed_data(session)

            if not data:
                logger.info("No hay datos no procesados.")
                return {"status_code": 200, "message": "No hay datos para procesar"}

            # Calcular promedios
            logger.info("Calculando promedios de datos")
            avg_humidity = mean([d.humidity for d in data])
            avg_temperature = mean([d.temperature for d in data])
            avg_co2 = mean([d.co2 for d in data])
            avg_people = round(mean([d.people for d in data]))

            logger.debug(f"Promedios calculados: H={avg_humidity}, T={avg_temperature}, CO2={avg_co2}, P={avg_people}")

            # Tomamos el raspberry_id del primero (asumiendo que son del mismo)
            raspberry_id = data[0].raspberry_id

            # Crear una nueva entrada con el resumen
            summarized_entry = Info(
                raspberry_id=raspberry_id,
                people=avg_people,
                humidity=avg_humidity,
                temperature=avg_temperature,
                co2=avg_co2,
                timestamp=datetime.now(),
                processed=True
            )

            # Insertar entrada resumida
            logger.info("Guardando datos procesados")
            Queries.insert_data(session, summarized_entry)
            logger.info("Datos procesados y resumidos correctamente.")

            # Enviar a la API
            message = {
                "people": avg_people,
                "humidity": avg_humidity,
                "temperature": avg_temperature,
                "co2": avg_co2
            }

            # Enviar a la API
            api_result = self.send_to_api(message)

            # Borrar los datos originales de los últimos 2 minutos
            logger.info("Limpiando datos originales")
            cutoff_time = datetime.now() - timedelta(minutes=2)
            deleted_count = Queries.delete_data_from_date(session, cutoff_time)
            logger.info(f"Se eliminaron {deleted_count} registros originales de los últimos 2 minutos")

            # Retornar el resultado del envío a la API
            return api_result

        except Exception as e:
            error_msg = f"Error al procesar entradas: {str(e)}"
            logger.error(error_msg)
            return {
                "status_code": 500,
                "error": error_msg
            }
