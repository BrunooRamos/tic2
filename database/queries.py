"""
Módulo de consultas a la base de datos.
Este módulo contiene las consultas SQL más comunes utilizadas en el sistema,
proporcionando una capa de abstracción sobre las operaciones de base de datos.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

from database.models.Info import Info

class Queries:
    """
    Clase que encapsula las consultas más comunes a la base de datos.
    
    Esta clase proporciona métodos estáticos para realizar operaciones
    CRUD y consultas específicas sobre la tabla 'info'.
    """
    
    @staticmethod
    def insert_data(session: Session, info: Info) -> Info:
        """
        Inserta un nuevo registro en la base de datos.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            info (Info): Objeto Info con los datos a insertar.
            
        Returns:
            Info: El registro insertado con su ID asignado.
            
        Raises:
            Exception: Si ocurre un error durante la inserción.
        """
        try:
            session.add(info)
            session.flush()
            return info
        except Exception as e:
            session.rollback()
            raise Exception(f"Error al insertar datos: {str(e)}")
    
    @staticmethod
    def get_unprocessed_data(session: Session, limit: int = 100) -> List[Info]:
        """
        Obtiene registros no procesados ordenados por timestamp.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            limit (int): Número máximo de registros a devolver.
            
        Returns:
            List[Info]: Lista de registros no procesados.
        """
        return session.query(Info)\
            .filter(Info.processed == False)\
            .order_by(Info.timestamp.asc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_latest_data(session: Session, limit: int = 10) -> List[Info]:
        """
        Obtiene los registros más recientes.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            limit (int): Número máximo de registros a devolver.
            
        Returns:
            List[Info]: Lista de registros ordenados por timestamp descendente.
        """
        return session.query(Info)\
            .order_by(desc(Info.timestamp))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_data_by_date_range(
        session: Session,
        start_date: datetime,
        end_date: datetime
    ) -> List[Info]:
        """
        Obtiene registros dentro de un rango de fechas.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            start_date (datetime): Fecha de inicio del rango.
            end_date (datetime): Fecha de fin del rango.
            
        Returns:
            List[Info]: Lista de registros dentro del rango especificado.
        """
        return session.query(Info)\
            .filter(Info.timestamp.between(start_date, end_date))\
            .order_by(Info.timestamp.asc())\
            .all()
    
    @staticmethod
    def get_data_by_raspberry_id(
        session: Session,
        raspberry_id: int,
        limit: int = 100
    ) -> List[Info]:
        """
        Obtiene registros de un Raspberry Pi específico.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            raspberry_id (int): ID del Raspberry Pi.
            limit (int): Número máximo de registros a devolver.
            
        Returns:
            List[Info]: Lista de registros del Raspberry Pi especificado.
        """
        return session.query(Info)\
            .filter(Info.raspberry_id == raspberry_id)\
            .order_by(desc(Info.timestamp))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_average_metrics(
        session: Session,
        hours: int = 24
    ) -> dict:
        """
        Calcula las métricas promedio para un período de tiempo.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            hours (int): Número de horas hacia atrás para calcular promedios.
            
        Returns:
            dict: Diccionario con las métricas promedio calculadas.
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = session.query(
            Info.raspberry_id,
            Info.temperature,
            Info.humidity,
            Info.co2,
            Info.people
        ).filter(
            Info.timestamp >= start_time
        ).all()
        
        if not result:
            return {
                'temperature': 0,
                'humidity': 0,
                'co2': 0,
                'people': 0
            }
        
        total_records = len(result)
        return {
            'temperature': sum(r.temperature for r in result) / total_records,
            'humidity': sum(r.humidity for r in result) / total_records,
            'co2': sum(r.co2 for r in result) / total_records,
            'people': sum(r.people for r in result) / total_records
        }
    
    @staticmethod
    def delete_old_data(session: Session, days: int = 30) -> int:
        """
        Elimina registros más antiguos que el número de días especificado.
        
        Args:
            session (Session): Sesión de base de datos SQLAlchemy.
            days (int): Número de días a mantener en la base de datos.
            
        Returns:
            int: Número de registros eliminados.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = session.query(Info)\
            .filter(Info.timestamp < cutoff_date)\
            .delete()
        session.commit()
        return result