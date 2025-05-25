"""
Modelo de datos para la información de sensores.

Este módulo define la estructura de la tabla 'info' que almacena
las lecturas de los sensores y su estado de procesamiento.
"""

from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, func
from ..db_handler import Base

class Info(Base):
    """
    Modelo que representa una lectura de sensores en la base de datos.

    Esta clase mapea la tabla 'info' que almacena:
    - Lecturas de sensores (temperatura, humedad, CO2)
    - Conteo de personas
    - Timestamp de la lectura
    - Estado de procesamiento
    """

    __tablename__ = "info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    raspberry_id = Column(Integer, nullable=False)
    people = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=False)
    temperature = Column(Integer, nullable=False)
    co2 = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    processed = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        """
        Representación en string del objeto.

        Returns:
            str: Representación legible del registro
        """
        return (
            f"Info(id={self.id}, "
            f"raspberry_id={self.raspberry_id}, "
            f"people={self.people}, "
            f"humidity={self.humidity}, "
            f"temperature={self.temperature}, "
            f"co2={self.co2}, "
            f"timestamp={self.timestamp}, "
            f"processed={self.processed})"
        )