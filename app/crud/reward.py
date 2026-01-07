from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import RewardLedger, RewardConfig
from datetime import datetime

def get_reward_summary(db: Session, user_id: int) -> dict:
    """Get reward summary for user"""
    rewards = db.query(RewardLedger).filter(RewardLedger.user_id == user_id).all()
    
    if not rewards:
        return {
            "total_earned": 0,
            "pending": 0,
            "credited": 0,
            "unit": "POINTS"
        }
    
    # Calculate totals
    total_earned = sum(r.reward_value for r in rewards)
    pending = sum(r.reward_value for r in rewards if r.status == "PENDING")
    credited = sum(r.reward_value for r in rewards if r.status == "CREDITED")
    unit = rewards[0].reward_unit if rewards else "POINTS"
    
    return {
        "total_earned": total_earned,
        "pending": pending,
        "credited": credited,
        "unit": unit
    }

def get_reward_history(db: Session, user_id: int) -> list:
    """Get reward history for user"""
    rewards = db.query(RewardLedger).filter(
        RewardLedger.user_id == user_id
    ).order_by(RewardLedger.created_at.desc()).all()
    
    result = []
    for reward in rewards:
        result.append({
            "id": reward.id,
            "reward_type": reward.reward_type,
            "reward_value": reward.reward_value,
            "reward_unit": reward.reward_unit,
            "status": reward.status,
            "created_at": reward.created_at
        })
    
    return result

def credit_reward(db: Session, reward_id: int) -> bool:
    """Credit a pending reward"""
    reward = db.query(RewardLedger).filter(RewardLedger.id == reward_id).first()
    
    if not reward:
        raise ValueError("Reward not found")
    
    if reward.status != "PENDING":
        raise ValueError("Only PENDING rewards can be credited")
    
    reward.status = "CREDITED"
    db.commit()
    
    return True

def revoke_reward(db: Session, reward_id: int) -> bool:
    """Revoke a reward"""
    reward = db.query(RewardLedger).filter(RewardLedger.id == reward_id).first()
    
    if not reward:
        raise ValueError("Reward not found")
    
    if reward.status == "REVOKED":
        raise ValueError("Reward already revoked")
    
    reward.status = "REVOKED"
    db.commit()
    
    return True

def create_reward_config(db: Session, reward_type: str, reward_value: int, reward_unit: str) -> dict:
    """Create reward configuration"""
    config = RewardConfig(
        reward_type=reward_type,
        reward_value=reward_value,
        reward_unit=reward_unit,
        is_active=True
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return {
        "id": config.id,
        "reward_type": config.reward_type,
        "reward_value": config.reward_value,
        "reward_unit": config.reward_unit,
        "is_active": config.is_active,
        "created_at": config.created_at
    }

def get_all_reward_configs(db: Session) -> list:
    """Get all reward configurations"""
    configs = db.query(RewardConfig).all()
    
    result = []
    for config in configs:
        result.append({
            "id": config.id,
            "reward_type": config.reward_type,
            "reward_value": config.reward_value,
            "reward_unit": config.reward_unit,
            "is_active": config.is_active,
            "created_at": config.created_at
        })
    
    return result
 