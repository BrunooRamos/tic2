from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from .models.info import Info   

class Queries:
    """
    This class contains SQL queries for the database.
    """

    @staticmethod
    def get_proccesed_data(session: Session):
        """
        SQL query to get processed data from the database.
        """
        stmt = (
            select(Info)
            .where(Info.processed == True)
            .order_by(Info.timestamp.desc())
        )

        return session.execute(stmt).all()
    
    @staticmethod
    def get_unprocessed_data(session: Session):
        """
        SQL query to get unprocessed data from the database.
        """
        stmt = (
            select(Info)
            .where(Info.processed == False)
            .order_by(Info.timestamp.desc())
        )

        return session.execute(stmt).all()
        # Esto lo cambié, el que estaba antes es el de abajo, 
        # hay que probar a ver si funcionaba antes de usar el session.execute
     
        #return session.query(Info).filter_by(processed=False).all()
    

    @staticmethod
    def insert_data(session: Session, data: Info):
        """
        SQL query to insert data into the database.
        """
        session.add(data)
        session.commit()

    @staticmethod
    def delete_data_from_date(session: Session, cutoff_date):
        """
        Elimina todas las filas con processed=False cuyo timestamp
        sea menor o igual a cutoff_date.
        """
        stmt = (
            delete(Info)
            .where(
                (Info.processed == False),

                # Acá agregue esta condición que antes no se estaba
                # considerando, porque sino se iban a eliminar todos los datos
                # que no estaban procesados, y no solo los que eran
                # anteriores a la fecha de corte
                (Info.timestamp <= cutoff_date)
            )
        )
        ejecucion = session.execute(stmt)
        session.commit()
        return ejecucion.rowcount  # Devuelve la cantidad de filas que eliminamos


    @staticmethod
    def mark_as_processed(session: Session, data: Info):
        """
        SQL query to mark data as processed.
        """
        stmt = (
            update(Info)
            .where(Info.id == data.id)
            .values(processed=True)
        )
        session.execute(stmt)
        session.commit()