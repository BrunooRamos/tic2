
from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, func
from ..db_handler import Base

class Info(Base):
    __tablename__ = "info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raspberry_id = Column(Integer, nullable=False)
    people        = Column(Integer, nullable=False)
    humidity      = Column(Integer, nullable=False)
    temperature   = Column(Integer, nullable=False)
    co2           = Column(Integer, nullable=False)
    timestamp     = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    processed     = Column(Boolean, default=False, nullable=False)