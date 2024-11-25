from sqlalchemy import Column, String, Integer, ForeignKey, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from .base import Base

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    winner_id = Column(Integer, nullable=True)
    winner_name = Column(String(255), nullable=True)
    winner_comment = Column(Text, nullable=True)
    win_or_draw = Column(Boolean, nullable=True)
    under_over = Column(String(20), nullable=True)
    goals_home = Column(String(20), nullable=True)
    goals_away = Column(String(20), nullable=True)
    advice = Column(Text, nullable=True)
    percent_home = Column(Float, nullable=True)
    percent_draw = Column(Float, nullable=True)
    percent_away = Column(Float, nullable=True)
    comparison_form_home = Column(Float, nullable=True)
    comparison_form_away = Column(Float, nullable=True)
    comparison_att_home = Column(Float, nullable=True)
    comparison_att_away = Column(Float, nullable=True)
    comparison_def_home = Column(Float, nullable=True)
    comparison_def_away = Column(Float, nullable=True)
    comparison_poisson_home = Column(Float, nullable=True)
    comparison_poisson_away = Column(Float, nullable=True)
    comparison_h2h_home = Column(Float, nullable=True)
    comparison_h2h_away = Column(Float, nullable=True)
    comparison_goals_home = Column(Float, nullable=True)
    comparison_goals_away = Column(Float, nullable=True)
    comparison_total_home = Column(Float, nullable=True)
    comparison_total_away = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    match = relationship("Match", back_populates="prediction")
    selected_predictions = relationship("SelectedPrediction", back_populates="prediction")

class SelectedPrediction(Base):
    __tablename__ = 'selected_predictions'
    
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    odds_value_id = Column(Integer, ForeignKey('odds_values.id'), nullable=False)
    bet_amount = Column(Float, nullable=False)
    status = Column(String(20), default='PENDING')  # PENDING, WIN, LOSS
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    prediction = relationship("Prediction", back_populates="selected_predictions")
    match = relationship("Match", back_populates="selected_predictions")
    odds_value = relationship("OddsValue")

