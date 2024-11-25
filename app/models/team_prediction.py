from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class PredictionTeam(Base):
    __tablename__ = 'prediction_teams'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    team_id = Column(Integer, nullable=False)
    team_name = Column(String(255), nullable=False)
    logo = Column(String(255), nullable=True)
    is_home = Column(Boolean, nullable=False)
    last_5_played = Column(Integer, nullable=True)
    last_5_form = Column(Float, nullable=True)
    last_5_att = Column(Float, nullable=True)
    last_5_def = Column(Float, nullable=True)
    last_5_goals_for_total = Column(Integer, nullable=True)
    last_5_goals_for_average = Column(Float, nullable=True)
    last_5_goals_against_total = Column(Integer, nullable=True)
    last_5_goals_against_average = Column(Float, nullable=True)
    league_form = Column(String(50), nullable=True)
    league_played_home = Column(Integer, nullable=True)
    league_played_away = Column(Integer, nullable=True)
    league_played_total = Column(Integer, nullable=True)
    league_wins_home = Column(Integer, nullable=True)
    league_wins_away = Column(Integer, nullable=True)
    league_wins_total = Column(Integer, nullable=True)
    league_draws_home = Column(Integer, nullable=True)
    league_draws_away = Column(Integer, nullable=True)
    league_draws_total = Column(Integer, nullable=True)
    league_loses_home = Column(Integer, nullable=True)
    league_loses_away = Column(Integer, nullable=True)
    league_loses_total = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    match = relationship("Match", back_populates="prediction_teams")