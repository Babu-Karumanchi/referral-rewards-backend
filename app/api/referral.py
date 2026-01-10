from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import referral as crud
from app.schemas.referral import ReferralApplyRequest, ReferralSummaryResponse, ReferralListItem

router = APIRouter(prefix="/api/referral", tags=["referral"])

@router.post("/generate")
def generate_referral_code(user_id: str, db: Session = Depends(get_db)):
    """Generate a referral code for user"""
    try:
        result = crud.get_or_create_referral_code(db, username=user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply")
def apply_referral_code(
    request: ReferralApplyRequest, 
    user_id: str, 
    db: Session = Depends(get_db)
):
    """Apply a referral code"""
    try:
        result = crud.apply_referral_code(db, user_id=user_id, code=request.referral_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/summary", response_model=ReferralSummaryResponse)
def get_analytics_summary(user_id: str, db: Session = Depends(get_db)):
    """Get analytics summary for user"""
    return crud.get_analytics_summary(db, user_id)

@router.get("/analytics/list", response_model=list[ReferralListItem])
def get_referral_list(user_id: str, db: Session = Depends(get_db)):
    """Get list of referrals for user"""
    return crud.get_referral_list(db, user_id)

@router.get("/admin/top")
def get_top_referrers(db: Session = Depends(get_db)):
    """Get top referrers leaderboard (admin)"""
    return crud.get_top_referrers(db)