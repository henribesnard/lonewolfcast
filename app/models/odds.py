from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from .base import Base

class OddsBookmaker(Base):
    __tablename__ = 'odds_bookmakers'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    bookmaker_id = Column(Integer, nullable=False)
    bookmaker_name = Column(String(100), nullable=False)
    bet_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    match = relationship("Match", back_populates="odds_bookmakers")
    odds_values = relationship("OddsValue", back_populates="bookmaker", cascade="all, delete-orphan")

class OddsValue(Base):
    __tablename__ = 'odds_values'
    
    id = Column(Integer, primary_key=True)
    bookmaker_id = Column(Integer, ForeignKey('odds_bookmakers.id'), nullable=False)
    outcome = Column(String(50), nullable=False)
    odd = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bookmaker = relationship("OddsBookmaker", back_populates="odds_values")

