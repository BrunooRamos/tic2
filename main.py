"""
Módulo principal del sistema de monitoreo ambiental.

Este módulo coordina la recolección de datos de sensores, el procesamiento
y el envío de información al servidor central. Implementa un sistema de
logging detallado y manejo robusto de errores.

Flujo principal:
1. Recolección de datos en tiempo real
2. Procesamiento periódico cada 2 minutos
3. Envío de datos procesados al servidor
4. Manejo de errores y reintentos
"""

import time
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from database.models.Info import Info
from database.queries import Queries
from camara.count_people import get_people_stream
from database.db_handler import DatabaseHandler
from process_to_ec2.process import ProcessToEC2
from sensor.sensor_script import read_sensor

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuraciones
RASPBERRY_ID = int(os.getenv('RASPBERRY_ID', '1'))
PROCESSING_INTERVAL = int(os.getenv('PROCESSING_INTERVAL', '120'))  # 2 minutos en segundos
MAX_RETRIES = 3
RETRY_DELAY = 120  # 2 minutos en segundos

def process_and_send_data(session, process_to_ec2, retry_count=0):
    """
    Procesa y envía los datos al endpoint, con manejo de reintentos.
    
    Args:
        session: Sesión de base de datos SQLAlchemy
        process_to_ec2: Instancia de ProcessToEC2 para procesamiento
        retry_count: Contador de reintentos actual
    
    Returns:
        None
    
    Raises:
        Exception: Si ocurre un error crítico en el procesamiento
    """
    try:
        # Obtener datos no procesados
        unprocessed_data = Queries.get_unprocessed_data(session)
        if not unprocessed_data:
            logger.info("No hay datos nuevos para procesar")
            return

        # Procesar los datos y obtener el resultado
        processed_result = process_to_ec2.procesar_entradas(session)
        
        if processed_result and processed_result.get('status_code') == 200:
            logger.info("Datos procesados y enviados exitosamente")
        else:
            error_msg = processed_result.get('error', 'Error desconocido') if processed_result else 'Error al procesar datos'
            logger.warning(f"Error en el procesamiento: {error_msg}")
            if retry_count < MAX_RETRIES:
                logger.info(f"Reintentando en {RETRY_DELAY} segundos... (Intento {retry_count + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
                process_and_send_data(session, process_to_ec2, retry_count + 1)
            else:
                logger.error("Se alcanzó el máximo número de reintentos")

    except Exception as e:
        logger.error(f"Error al procesar datos: {str(e)}")
        if retry_count < MAX_RETRIES:
            logger.info(f"Reintentando en {RETRY_DELAY} segundos... (Intento {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
            process_and_send_data(session, process_to_ec2, retry_count + 1)
        else:
            logger.error("Se alcanzó el máximo número de reintentos")

def main():
    """
    Función principal que coordina el flujo del sistema.

    Esta función:
    1. Inicializa la conexión a la base de datos
    2. Configura el procesador de datos
    3. Inicia el bucle principal de recolección
    4. Maneja el procesamiento periódico
    5. Gestiona errores y reintentos
    
    Raises:
        Exception: Si ocurre un error crítico en la inicialización
    """
    try:
        logger.info("Iniciando sistema de monitoreo ambiental")
        
        # Inicializar conexión a base de datos
        db_handler = DatabaseHandler()
        _, Session = db_handler.connect_to_database()
        session = Session()
        logger.info("Conexión a base de datos establecida")

        # Inicializar el proceso de EC2
        process_to_ec2 = ProcessToEC2(session=session)
        logger.info("Procesador de datos inicializado")

        last_process_time = time.time()
        logger.info("Iniciando bucle principal de recolección")

        for people_count in get_people_stream():
            try:
                # Leer sensor
                medida = read_sensor()
                if medida is None:
                    logger.warning("No se pudo obtener lectura del sensor")
                    continue

                # Guardar datos inmediatamente cuando hay nueva lectura
                info = Info(
                    raspberry_id=RASPBERRY_ID,
                    people=people_count,
                    humidity=medida["humidity"],
                    temperature=medida["temperature"],
                    co2=medida["co2"],
                    processed=False
                )
                
                try:
                    Queries.insert_data(session, info)
                    session.commit()
                    logger.debug(f"Datos guardados: {info.__dict__}")
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error al guardar datos en la base de datos: {str(e)}")
                    continue

                # Procesar cada 2 minutos
                current_time = time.time()
                if current_time - last_process_time >= PROCESSING_INTERVAL:
                    logger.info("Iniciando procesamiento periódico")
                    process_and_send_data(session, process_to_ec2)
                    last_process_time = current_time

            except Exception as e:
                logger.error(f"Error en el bucle principal: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {str(e)}")
    finally:
        try:
            session.close()
            logger.info("Sesión de base de datos cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar la sesión de la base de datos: {str(e)}")

if __name__ == "__main__":
    main()
