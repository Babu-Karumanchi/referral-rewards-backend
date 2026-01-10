from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from app.models.models import RewardLedger, RewardConfig, User

def get_reward_summary(db: Session, user_id: str) -> dict:
    """Get reward summary for a user"""
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        return {"total_earned": 0, "pending": 0, "credited": 0, "unit": "points"}
    
    result = db.query(
        func.sum(RewardLedger.reward_value).filter(RewardLedger.status == "CREDITED").label("credited"),
        func.sum(RewardLedger.reward_value).filter(RewardLedger.status == "PENDING").label("pending"),
        func.max(RewardLedger.reward_unit).label("unit")
    ).filter(
        RewardLedger.user_id == user.id
    ).first()
    
    total_earned = (result.credited or 0) + (result.pending or 0)
    
    return {
        "total_earned": total_earned,
        "pending": result.pending or 0,
        "credited": result.credited or 0,
        "unit": result.unit or "points"
    }

def get_reward_history(db: Session, user_id: str) -> list:
    """Get reward history for a user"""
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        return []
    
    rewards = db.query(RewardLedger).filter(
        RewardLedger.user_id == user.id
    ).order_by(
        RewardLedger.created_at.desc()
    ).all()
    
    return rewards

def get_pending_rewards(db: Session) -> list:
    """Get all pending rewards for admin approval"""
    rewards = db.query(RewardLedger).filter(
        RewardLedger.status == "PENDING"
    ).order_by(
        RewardLedger.created_at.desc()
    ).all()
    
    result = []
    for reward in rewards:
        user = db.query(User).filter(User.id == reward.user_id).first()
        result.append({
            "id": reward.id,
            "user_id": user.username if user else str(reward.user_id),
            "reward_type": reward.reward_type,
            "reward_value": reward.reward_value,
            "reward_unit": reward.reward_unit,
            "created_at": reward.created_at,
            "referral_id": reward.referral_id
        })
    
    return result

def credit_reward(db: Session, reward_id: int) -> None:
    """Credit a pending reward"""
    reward = db.query(RewardLedger).filter(RewardLedger.id == reward_id).first()
    if not reward:
        raise ValueError("Reward not found")
    
    if reward.status != "PENDING":
        raise ValueError(f"Reward is already {reward.status.lower()}")
    
    reward.status = "CREDITED"
    reward.credited_at = datetime.now()
    db.commit()

def revoke_reward(db: Session, reward_id: int) -> None:
    """Revoke a reward"""
    reward = db.query(RewardLedger).filter(RewardLedger.id == reward_id).first()
    if not reward:
        raise ValueError("Reward not found")
    
    reward.status = "REVOKED"
    db.commit()

def create_reward_config(db: Session, reward_type: str, reward_value: int, reward_unit: str) -> dict:
    """Create a new reward configuration"""
    existing = db.query(RewardConfig).filter(RewardConfig.reward_type == reward_type).first()
    if existing:
        existing.reward_value = reward_value
        existing.reward_unit = reward_unit
    else:
        config = RewardConfig(
            reward_type=reward_type,
            reward_value=reward_value,
            reward_unit=reward_unit
        )
        db.add(config)
    
    db.commit()
    db.refresh(existing if existing else config)
    
    return existing if existing else config

def get_all_reward_configs(db: Session) -> list:
    """Get all reward configurations"""
    return db.query(RewardConfig).order_by(RewardConfig.reward_type).all()