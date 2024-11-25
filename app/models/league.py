from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class League(Base):
   __tablename__ = 'leagues'
   
   id = Column(Integer, primary_key=True)
   api_id = Column(Integer, unique=True, index=True)
   name = Column(String(255), nullable=False)
   country = Column(String(100), nullable=True)
   logo = Column(String(255), nullable=True)
   flag = Column(String(255), nullable=True)
   type = Column(String(50), nullable=True)  
   is_active = Column(Boolean, default=True)
   created_at = Column(DateTime(timezone=True), server_default=func.now())
   updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

   matches = relationship("Match", back_populates="league")
   seasons = relationship("Season", back_populates="league", cascade="all, delete-orphan")

class Season(Base):
   __tablename__ = 'seasons'
   
   id = Column(Integer, primary_key=True)
   league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
   year = Column(Integer, nullable=False)
   start_date = Column(DateTime(timezone=True), nullable=False)
   end_date = Column(DateTime(timezone=True), nullable=False)
   current = Column(Boolean, default=False)
   
   # Coverage info
   has_predictions = Column(Boolean, default=False)
   has_odds = Column(Boolean, default=False)

   # New fields
   matches_synced = Column(Boolean, default=False, nullable=False)  # Indique si les matchs sont synchronisés
   last_match_sync = Column(DateTime(timezone=True), nullable=True)  # Date de la dernière synchronisation des matchs
   
   created_at = Column(DateTime(timezone=True), server_default=func.now())
   updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

   league = relationship("League", back_populates="seasons")
