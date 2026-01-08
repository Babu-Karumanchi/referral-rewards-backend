from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.models import RewardLedger, RewardConfig, User, Referral
from datetime import datetime
from typing import Dict, List, Any

def get_reward_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """Get reward summary for user - FIXED"""
    rewards = db.query(RewardLedger).filter(RewardLedger.user_id == user_id).all()
    
    if not rewards:
        return {
            "total_earned": 0,
            "pending": 0,
            "credited": 0,
            "revoked": 0,  # ← ADDED
            "unit": "POINTS"
        }
    
    # FIXED: Handle empty rewards safely
    unit = rewards[0].reward_unit if rewards else "POINTS"
    total_earned = sum(r.reward_value for r in rewards)
    pending = sum(r.reward_value for r in rewards if r.status == "PENDING")
    credited = sum(r.reward_value for r in rewards if r.status == "CREDITED")
    revoked = sum(r.reward_value for r in rewards if r.status == "REVOKED")
    
    return {
        "total_earned": total_earned,
        "pending": pending,
        "credited": credited,
        "revoked": revoked,  # ← ADDED
        "unit": unit
    }

def get_reward_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Get reward history for user - OPTIMIZED"""
    rewards = db.query(RewardLedger).filter(
        RewardLedger.user_id == user_id
    ).order_by(RewardLedger.created_at.desc()).all()
    
    return [  # ← ONE LINER (more efficient)
        {
            "id": r.id,
            "reward_type": r.reward_type,
            "reward_value": r.reward_value,
            "reward_unit": r.reward_unit,
            "status": r.status,
            "created_at": r.created_at.isoformat()  # ← JSON serializable
        }
        for r in rewards
    ]

def credit_reward(db: Session, reward_id: int) -> Dict[str, str]:
    """Credit a pending reward - PRODUCTION READY"""
    reward = db.query(RewardLedger).filter(RewardLedger.id == reward_id).first()
    
    if not reward:
        raise ValueError("Reward not found")
    
    if reward.status != "PENDING":
        raise ValueError(f"Only PENDING rewards can be credited. Current: {reward.status}")
    
    reward.status = "CREDITED"
    reward.updated_at = datetime.utcnow()  # ← ADDED audit trail
    db.commit()
    
    return {"status": "success", "message": f"Reward {reward_id} credited"}

def revoke_reward(db: Session, reward_id: int) -> Dict[str, str]:
    """Revoke a reward - PRODUCTION READY"""
    reward = db.query(RewardLedger).filter(RewardLedger.id == reward_id).first()
    
    if not reward:
        raise ValueError("Reward not found")
    
    if reward.status == "REVOKED":
        raise ValueError("Reward already revoked")
    
    reward.status = "REVOKED"
    reward.updated_at = datetime.utcnow()  # ← ADDED audit trail
    db.commit()
    
    return {"status": "success", "message": f"Reward {reward_id} revoked"}

def create_reward_config(db: Session, reward_type: str, reward_value: int, reward_unit: str) -> Dict[str, Any]:
    """Create reward configuration - FIXED"""
    # Check duplicate
    existing = db.query(RewardConfig).filter(
        RewardConfig.reward_type == reward_type,
        RewardConfig.reward_unit == reward_unit
    ).first()
    
    if existing:
        raise ValueError(f"Config for {reward_type}/{reward_unit} exists")
    
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
        "created_at": config.created_at.isoformat()
    }

def get_all_reward_configs(db: Session) -> List[Dict[str, Any]]:
    """Get all reward configurations - OPTIMIZED"""
    configs = db.query(RewardConfig).filter(RewardConfig.is_active == True).all()  # ← Active only
    
    return [  # ← ONE LINER
        {
            "id": c.id,
            "reward_type": c.reward_type,
            "reward_value": c.reward_value,
            "reward_unit": c.reward_unit,
            "is_active": c.is_active,
            "created_at": c.created_at.isoformat()
        }
        for c in configs
    ]

# BONUS: Leaderboard function (for /admin/top)
def get_leaderboard(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Admin leaderboard - TOP referrers"""
    from sqlalchemy import desc
    
    results = db.query(
        User.username,
        func.count(Referral.id).label('referral_count'),
        func.sum(RewardLedger.reward_value).label('total_rewards')
    ).outerjoin(
        Referral, User.id == Referral.referred_by
    ).outerjoin(
        RewardLedger, Referral.id == RewardLedger.referral_id
    ).group_by(User.id, User.username).order_by(
        desc(func.coalesce(func.sum(RewardLedger.reward_value), 0)),
        desc(func.count(Referral.id))
    ).limit(limit).all()
    
    return [{
        "username": r.username,
        "referral_count": r.referral_count,
        "total_rewards": r.total_rewards or 0
    } for r in results]
