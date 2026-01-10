import random
import string
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from app.models.models import Referral, User, RewardLedger, RewardConfig

def generate_referral_code() -> str:
    """Generate referral code in format SVH-AB12CD"""
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"SVH-{letters1}{digits}{letters2}"

def get_or_create_user(db: Session, username: str) -> User:
    """Get existing user or create new one"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        max_id = db.query(func.max(User.id)).scalar() or 0
        user = User(id=max_id + 1, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_or_create_referral_code(db: Session, username: str) -> dict:
    """Generate or get existing referral code for user"""
    user = get_or_create_user(db, username)
    
    referral = db.query(Referral).filter(Referral.referred_by == user.id).first()
    
    if not referral:
        while True:
            code = generate_referral_code()
            existing = db.query(Referral).filter(Referral.referral_code == code).first()
            if not existing:
                break
        
        referral = Referral(
            referral_code=code,
            referred_by=user.id
        )
        db.add(referral)
        db.commit()
        db.refresh(referral)
    
    return {
        "id": user.id,
        "username": user.username,
        "referral_code": referral.referral_code
    }

def apply_referral_code(db: Session, user_id: str, code: str) -> dict:
    """Apply a referral code to get referred"""
    referred_user = get_or_create_user(db, user_id)
    
    referral = db.query(Referral).filter(Referral.referral_code == code).first()
    if not referral:
        raise ValueError("Invalid referral code")
    
    if referral.referred_by == referred_user.id:
        raise ValueError("Cannot use your own referral code")
    
    if referral.referred_user_id is not None:
        raise ValueError("Referral code already used")
    
    existing_referral = db.query(Referral).filter(
        Referral.referred_user_id == referred_user.id
    ).first()
    if existing_referral:
        raise ValueError("You have already used a referral code")
    
    referral.referred_user_id = referred_user.id
    referral.used_at = datetime.now()
    
    config = db.query(RewardConfig).filter(
        RewardConfig.reward_type == "SIGNUP",
        RewardConfig.is_active == True
    ).first()
    
    if config:
        reward = RewardLedger(
            user_id=referral.referred_by,
            referral_id=referral.id,
            reward_type=config.reward_type,
            reward_value=config.reward_value,
            reward_unit=config.reward_unit,
            status="PENDING"
        )
        db.add(reward)
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Referral code applied successfully",
        "referrer_id": referral.referred_by
    }

def get_analytics_summary(db: Session, user_id: str) -> dict:
    """Get analytics summary for a user"""
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        return {
            "my_referral_code": None,
            "total_referrals": 0,
            "successful_referrals": 0,
            "conversion_rate": "0%"
        }
    
    referral = db.query(Referral).filter(Referral.referred_by == user.id).first()
    
    total = db.query(Referral).filter(Referral.referred_by == user.id).count()
    successful = db.query(Referral).filter(
        Referral.referred_by == user.id,
        Referral.referred_user_id.isnot(None)
    ).count()
    
    conversion_rate = "0%"
    if total > 0:
        rate = (successful / total) * 100
        conversion_rate = f"{rate:.1f}%"
    
    return {
        "my_referral_code": referral.referral_code if referral else None,
        "total_referrals": total,
        "successful_referrals": successful,
        "conversion_rate": conversion_rate
    }

def get_referral_list(db: Session, user_id: str) -> list:
    """Get list of referrals for a user"""
    user = db.query(User).filter(User.username == user_id).first()
    if not user:
        return []
    
    referrals = db.query(Referral).filter(Referral.referred_by == user.id).all()
    
    result = []
    for ref in referrals:
        referred_user = None
        if ref.referred_user_id:
            referred_user = db.query(User).filter(User.id == ref.referred_user_id).first()
        
        result.append({
            "referral_code": ref.referral_code,
            "used_by_user_id": referred_user.username if referred_user else None,
            "used_at": ref.used_at,
            "status": "SUCCESS" if ref.referred_user_id else "PENDING"
        })
    
    return result

def get_top_referrers(db: Session, limit: int = 10) -> list:
    """Get top referrers leaderboard"""
    results = db.query(
        Referral.referred_by,
        func.count(Referral.id).label('successful_referrals')
    ).filter(
        Referral.referred_user_id.isnot(None)
    ).group_by(
        Referral.referred_by
    ).order_by(
        desc('successful_referrals')
    ).limit(limit).all()
    
    top_referrers = []
    for result in results:
        user = db.query(User).filter(User.id == result.referred_by).first()
        if user:
            top_referrers.append({
                "user_id": user.username,
                "successful_referrals": result.successful_referrals
            })
    
    return top_referrers