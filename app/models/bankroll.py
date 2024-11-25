from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from .base import Base

class BankrollHistory(Base):
    __tablename__ = 'bankroll_history'
    
    id = Column(Integer, primary_key=True)
    initial_bankroll = Column(Float, nullable=False)
    current_bankroll = Column(Float, nullable=False)
    total_bets = Column(Integer, default=0)
    winning_bets = Column(Integer, default=0)
    losing_bets = Column(Integer, default=0)
    roi = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    average_odds = Column(Float, default=0.0)
    highest_bankroll = Column(Float, nullable=False)
    lowest_bankroll = Column(Float, nullable=False)
    longest_winning_streak = Column(Integer, default=0)
    longest_losing_streak = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BankrollTransaction(Base):
    __tablename__ = 'bankroll_transactions'
    
    id = Column(Integer, primary_key=True)
    selected_prediction_id = Column(Integer, ForeignKey('selected_predictions.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # BET, WIN, LOSS
    amount = Column(Float, nullable=False)
    bankroll_before = Column(Float, nullable=False)
    bankroll_after = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

