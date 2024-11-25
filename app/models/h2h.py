from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class H2HMatch(Base):
    __tablename__ = 'h2h_matches'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    api_fixture_id = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    home_team_id = Column(Integer, nullable=False)
    home_team_name = Column(String(255), nullable=False)
    away_team_id = Column(Integer, nullable=False)
    away_team_name = Column(String(255), nullable=False)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    halftime_home_goals = Column(Integer, nullable=True)
    halftime_away_goals = Column(Integer, nullable=True)
    fulltime_home_goals = Column(Integer, nullable=True)
    fulltime_away_goals = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="h2h_matches")