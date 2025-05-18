from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()

class DatabaseHandler:
    def __init__(self):
        self.engine = None
        self.Session = None

    def connect_to_database(self):
        """Conectar a la base de datos PostgreSQL"""
        #DATABASE_URL = os.getenv("DATABASE_URL")
        
        DATABASE_URL = "postgresql://room:room13@localhost:5432/roomdb"
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        return self.engine, self.Session