from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import get_db
from app.core.security import require_admin
from app.crud import referral as referral_crud
from app.crud import reward as reward_crud
from app.models.models import User, Referral, RewardLedger
from sqlalchemy import func, desc

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Get comprehensive admin dashboard stats"""
    
    # Total users
    total_users = db.query(User).count()
    
    # Total referrals
    total_referrals = db.query(Referral).count()
    
    # Successful referrals
    successful_referrals = db.query(Referral).filter(
        Referral.referred_user_id.isnot(None)
    ).count()
    
    # Conversion rate
    conversion_rate = 0
    if total_referrals > 0:
        conversion_rate = (successful_referrals / total_referrals) * 100
    
    # Total rewards
    total_rewards = db.query(RewardLedger).count()
    pending_rewards = db.query(RewardLedger).filter(
        RewardLedger.status == "PENDING"
    ).count()
    credited_rewards = db.query(RewardLedger).filter(
        RewardLedger.status == "CREDITED"
    ).count()
    
    # Total reward value
    total_value = db.query(func.sum(RewardLedger.reward_value)).filter(
        RewardLedger.status == "CREDITED"
    ).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_referrals": total_referrals,
        "successful_referrals": successful_referrals,
        "conversion_rate": f"{conversion_rate:.1f}%",
        "total_rewards": total_rewards,
        "pending_rewards": pending_rewards,
        "credited_rewards": credited_rewards,
        "total_reward_value": total_value
    }

@router.get("/analytics/daily")
def get_daily_analytics(
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Get daily analytics for charting"""
    # Get referrals per day (last 30 days)
    from datetime import datetime, timedelta
    import json
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # This is a simplified version - in production you'd use proper date grouping
    referrals = db.query(Referral).filter(
        Referral.created_at >= start_date
    ).all()
    
    # Group by date
    daily_counts = {}
    for ref in referrals:
        date_str = ref.created_at.date().isoformat() if ref.created_at else end_date.date().isoformat()
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
    
    # Format for chart
    chart_data = [
        {"date": date, "count": count}
        for date, count in sorted(daily_counts.items())
    ]
    
    return chart_data