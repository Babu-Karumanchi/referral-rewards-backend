from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Referral(Base):
    __tablename__ = "referral"
    id = Column(Integer, primary_key=True, index=True)
    referral_code = Column(String(10), unique=True, index=True, nullable=False)
    referred_by = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    referred_at = Column(DateTime, default=datetime.utcnow)
    referral_code_used = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    referral_used_at = Column(DateTime, nullable=True)

class RewardConfig(Base):
    __tablename__ = "reward_config"
    id = Column(Integer, primary_key=True, index=True)
    reward_type = Column(String(20), nullable=False)  # 'SIGNUP', 'FIRST_ORDER'
    reward_value = Column(Integer, nullable=False)
    reward_unit = Column(String(10), nullable=False)  # 'POINTS', 'CASH'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RewardLedger(Base):
    __tablename__ = "reward_ledger"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    referral_id = Column(Integer, ForeignKey("referral.id"), index=True, nullable=False)
    reward_type = Column(String(20), nullable=False)
    reward_value = Column(Integer, nullable=False)
    reward_unit = Column(String(10), nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, CREDITED, REVOKED
    created_at = Column(DateTime, default=datetime.utcnow)
