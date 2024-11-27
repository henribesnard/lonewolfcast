from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    
    # Winner info
    winner_id = Column(Integer, nullable=True)
    winner_name = Column(String(255), nullable=True)
    winner_comment = Column(Text, nullable=True)
    win_or_draw = Column(Boolean, default=False)
    
    # Goals prediction
    under_over = Column(String(10), nullable=True)
    goals_home = Column(String(10), nullable=True)
    goals_away = Column(String(10), nullable=True)
    
    # Advice and percentages
    advice = Column(Text, nullable=True)
    percent_home = Column(Float, nullable=True)
    percent_draw = Column(Float, nullable=True)
    percent_away = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    match = relationship("Match", back_populates="prediction")
    teams_data = relationship("PredictionTeam", back_populates="prediction", cascade="all, delete-orphan")
    comparison = relationship("PredictionComparison", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
    outcome = relationship("PredictionOutcome", back_populates="prediction", uselist=False, cascade="all, delete-orphan")

class PredictionTeam(Base):
    __tablename__ = 'prediction_teams'

    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id', ondelete="CASCADE"), nullable=False)
    is_home = Column(Boolean, nullable=False)  # Pour différencier équipe domicile/extérieur
    
    # Team info
    team_id = Column(Integer, nullable=False)
    team_name = Column(String(255), nullable=False)
    team_logo = Column(String(255), nullable=True)

    # Last 5 matches stats
    last_5_played = Column(Integer, nullable=True)
    last_5_form = Column(Float, nullable=True)
    last_5_att = Column(Float, nullable=True)
    last_5_def = Column(Float, nullable=True)
    
    # Goals stats
    goals_for_total = Column(Integer, nullable=True)
    goals_for_avg = Column(Float, nullable=True)
    goals_against_total = Column(Integer, nullable=True)
    goals_against_avg = Column(Float, nullable=True)

    # League form
    league_form = Column(String(50), nullable=True)
    league_fixtures_played_home = Column(Integer, nullable=True)
    league_fixtures_played_away = Column(Integer, nullable=True)
    league_fixtures_played_total = Column(Integer, nullable=True)

    # Performance stats
    clean_sheet_home = Column(Integer, nullable=True)
    clean_sheet_away = Column(Integer, nullable=True)
    clean_sheet_total = Column(Integer, nullable=True)
    failed_to_score_home = Column(Integer, nullable=True)
    failed_to_score_away = Column(Integer, nullable=True)
    failed_to_score_total = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    prediction = relationship("Prediction", back_populates="teams_data")

class PredictionComparison(Base):
    __tablename__ = 'prediction_comparisons'

    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id', ondelete="CASCADE"), nullable=False)

    # Form comparison
    form_home = Column(Float, nullable=True)
    form_away = Column(Float, nullable=True)
    
    # Attack & Defense
    att_home = Column(Float, nullable=True)
    att_away = Column(Float, nullable=True)
    def_home = Column(Float, nullable=True)
    def_away = Column(Float, nullable=True)
    
    # Poisson & H2H
    poisson_distribution_home = Column(Float, nullable=True)
    poisson_distribution_away = Column(Float, nullable=True)
    h2h_home = Column(Float, nullable=True)
    h2h_away = Column(Float, nullable=True)
    
    # Goals & Total
    goals_home = Column(Float, nullable=True)
    goals_away = Column(Float, nullable=True)
    total_home = Column(Float, nullable=True)
    total_away = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    prediction = relationship("Prediction", back_populates="comparison")

class PredictionOutcome(Base):
    __tablename__ = 'prediction_outcomes'
    
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id', ondelete="CASCADE"), nullable=False)
    
    # Évaluation de la prédiction winner
    winner_prediction_correct = Column(Boolean, nullable=True)
    win_or_draw_prediction_correct = Column(Boolean, nullable=True)
    
    # Évaluation des prédictions de buts
    under_over_prediction_correct = Column(Boolean, nullable=True)
    goals_prediction_accuracy = Column(Float, nullable=True)  # Pourcentage de précision
    
    # Métriques pour le ML
    pre_match_confidence = Column(Float, nullable=True)  # Basé sur les comparaisons
    form_difference = Column(Float, nullable=True)  # Différence de forme entre les équipes
    historical_accuracy = Column(Float, nullable=True)  # Précision historique pour ce type de match
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    prediction = relationship("Prediction", back_populates="outcome")
