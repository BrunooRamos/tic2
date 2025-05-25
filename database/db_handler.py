"""
Manejador de conexión a la base de datos.

Este módulo proporciona la funcionalidad para:
- Establecer conexión con la base de datos PostgreSQL
- Crear las tablas necesarias
- Gestionar sesiones de base de datos
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configuración de logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# URL de conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Base para los modelos declarativos
Base = declarative_base()

class DatabaseHandler:
    """
    Manejador de conexión a la base de datos PostgreSQL.

    Esta clase se encarga de:
    - Establecer la conexión con la base de datos
    - Crear las tablas necesarias
    - Proporcionar sesiones para operaciones en la base de datos
    """

    def __init__(self):
        """
        Inicializa el manejador de base de datos.

        Attributes:
            engine: Motor de SQLAlchemy para la conexión
            Session: Fábrica de sesiones de SQLAlchemy
        """
        self.engine = None
        self.Session = None
        logger.debug("DatabaseHandler inicializado")

    def connect_to_database(self):
        """
        Establece la conexión con la base de datos PostgreSQL.

        Este método:
        1. Crea el motor de SQLAlchemy
        2. Crea todas las tablas definidas en los modelos
        3. Configura la fábrica de sesiones

        Returns:
            tuple: (engine, Session) donde:
                - engine: Motor de SQLAlchemy
                - Session: Fábrica de sesiones

        Raises:
            SQLAlchemyError: Si hay un error al conectar con la base de datos
        """
        try:
            logger.info("Conectando a la base de datos")
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Conexión a la base de datos establecida exitosamente")
            return self.engine, self.Session
        except Exception as e:
            logger.error(f"Error al conectar con la base de datos: {str(e)}")
            raise