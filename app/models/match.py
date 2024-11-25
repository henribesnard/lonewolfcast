from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from .base import Base

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    api_fixture_id = Column(Integer, unique=True, index=True)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False) 
    status = Column(String(20), nullable=False, default='NOT_STARTED')
    home_team = Column(String(255), nullable=False)
    home_team_id = Column(Integer)
    home_team_logo = Column(String(255), nullable=True)
    away_team = Column(String(255), nullable=False)
    away_team_id = Column(Integer)
    away_team_logo = Column(String(255), nullable=True)
    venue = Column(String(255), nullable=True)
    round = Column(String(50), nullable=True)

    # Nouveau champs pour tracer la synchronisation
    predictions_synced = Column(Boolean, default=False, nullable=False)
    last_predictions_sync = Column(DateTime(timezone=True), nullable=True)  
    odds_synced = Column(Boolean, default=False, nullable=False)  
    last_odds_sync = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    league = relationship("League", back_populates="matches")
    odds_bookmakers = relationship("OddsBookmaker", back_populates="match")
    prediction = relationship("Prediction", back_populates="match", uselist=False)
    h2h_matches = relationship("H2HMatch", back_populates="match")
    prediction_teams = relationship("PredictionTeam", back_populates="match")
    selected_predictions = relationship("SelectedPrediction", back_populates="match")
