from sqlalchemy import Column, Integer, Date
from sqlalchemy.sql import func
from .base import Base

class ApiUsage(Base):
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)  # Date des appels API
    calls_made = Column(Integer, default=0)  # Nombre d'appels effectués
    reset_time = Column(Date, nullable=False, server_default=func.now())  # Heure de réinitialisation
