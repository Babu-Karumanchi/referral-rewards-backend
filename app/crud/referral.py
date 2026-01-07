from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.models import Referral, RewardLedger
from datetime import datetime, timedelta
import random
import string

def generate_referral_code(length=8):
    """SVH-AB12CD format"""
    prefix = "SVH"
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=length))
    return f"{prefix}-{code}"

def apply_referral_code(db: Session, user_id: int, referral_code: str):
    """Apply logic with self-referral check"""
    referral = db.query(Referral).filter(Referral.referral_code == referral_code).first()
    if not referral:
        raise ValueError("Invalid referral code")
    if referral.referred_by == user_id:
        raise ValueError("Cannot self-refer")
    if referral.referral_code_used == user_id:
        raise ValueError("Referral already used")
    
    referral.referral_code_used = user_id
    referral.referral_used_at = datetime.utcnow()
    db.commit()
    return "Referral applied successfully - reward pending"

def get_user_referral(db: Session, user_id: int):
    """My referral analytics"""
    referral = db.query(Referral).filter(Referral.referred_by == user_id).first()
    if not referral:
        referral_code = generate_referral_code()
        referral = Referral(referred_by=user_id, referral_code=referral_code)
        db.add(referral)
        db.commit()
    
    total = db.query(Referral).filter(Referral.referred_by == user_id).count()
    successful = db.query(Referral).filter(
        and_(Referral.referred_by == user_id, Referral.referral_code_used.isnot(None))
    ).count()
    conversion = f"{(successful/total*100):.0f}%" if total > 0 else "0%"
    
    return {
        "my_referral_code": referral.referral_code,
        "total_referrals": total,
        "successful_referrals": successful,
        "conversion_rate": conversion
    }

def get_referral_list(db: Session, user_id: int):
    """List who used my code"""
    referrals = db.query(Referral).filter(Referral.referred_by == user_id).all()
    return [{
        "used_by_user_id": r.referral_code_used,
        "used_at": r.referral_used_at,
        "status": "SUCCESS" if r.referral_code_used else "PENDING"
    } for r in referrals]

def get_referral_timeline(db: Session, user_id: int):
    """Daily counts"""
    week_ago = datetime.utcnow() - timedelta(days=7)
    timeline = db.query(
        func.date(Referral.referral_used_at).label('date'),
        func.count().label('count')
    ).filter(
        and_(
            Referral.referred_by == user_id,
            Referral.referral_used_at >= week_ago
        )
    ).group_by(func.date(Referral.referral_used_at)).all()
    
    return [{"date": str(d.date), "count": int(d.count)} for d in timeline]

def get_top_referrers(db: Session, limit: int = 10):
    """Admin leaderboard"""
    top = db.query(
        Referral.referred_by,
        func.count(Referral.referral_code_used).label('successful')
    ).filter(Referral.referral_code_used.isnot(None)).group_by(Referral.referred_by).order_by('successful desc').limit(limit).all()
    return [{"user_id": r.referred_by, "successful_referrals": int(r.successful)} for r in top]
