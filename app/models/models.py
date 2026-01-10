from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    referrals_given = relationship("Referral", foreign_keys="Referral.referred_by", back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="Referral.referred_user_id", back_populates="referred_user")
    rewards = relationship("RewardLedger", back_populates="user")

class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referral_code = Column(String, unique=True, nullable=False)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    referrer = relationship("User", foreign_keys=[referred_by], back_populates="referrals_given")
    referred_user = relationship("User", foreign_keys=[referred_user_id], back_populates="referrals_received")
    reward = relationship("RewardLedger", back_populates="referral", uselist=False)

class RewardLedger(Base):
    __tablename__ = "reward_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referral_id = Column(Integer, ForeignKey("referrals.id"), nullable=True)
    reward_type = Column(String, nullable=False) 
    reward_value = Column(Integer, nullable=False)
    reward_unit = Column(String, nullable=False, default="points")
    status = Column(String, nullable=False, default="PENDING")  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    credited_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", back_populates="rewards")
    referral = relationship("Referral", back_populates="reward")

class RewardConfig(Base):
    __tablename__ = "reward_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    reward_type = Column(String, unique=True, nullable=False)
    reward_value = Column(Integer, nullable=False)
    reward_unit = Column(String, nullable=False, default="points")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())