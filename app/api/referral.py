from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.referral import (
    ReferralSummaryResponse, ReferralApplyRequest, ReferralListItem, 
    ReferralTimelineItem, TopReferrerItem
)

router = APIRouter(prefix="/api/referral", tags=["referral"])

# STUBS - will add real CRUD imports after
@router.post("/apply")
def apply_referral_endpoint(request: ReferralApplyRequest, db: Session = Depends(get_db)):
    return {"status": "success", "message": "Referral applied"}

@router.get("/my", response_model=ReferralSummaryResponse)
def get_my_referral(db: Session = Depends(get_db)):
    return {
        "my_referral_code": "SVH-AB12CD",
        "total_referrals": 5,
        "successful_referrals": 2,
        "conversion_rate": "40%"
    }

@router.post("/generate")
def generate_referral_endpoint(db: Session = Depends(get_db)):
    return {"referral_code": "SVH-NEW123"}

@router.get("/analytics/summary", response_model=ReferralSummaryResponse)
def analytics_summary(db: Session = Depends(get_db)):
    return {
        "my_referral_code": "SVH-AB12CD",
        "total_referrals": 10,
        "successful_referrals": 4,
        "conversion_rate": "40%"
    }

@router.get("/analytics/list", response_model=list[ReferralListItem])
def analytics_list(db: Session = Depends(get_db)):
    return [
        {"used_by_user_id": 2, "used_at": "2025-01-12T10:30:00", "status": "SUCCESS"},
        {"used_by_user_id": None, "used_at": None, "status": "PENDING"}
    ]

@router.get("/analytics/timeline", response_model=list[ReferralTimelineItem])
def analytics_timeline(db: Session = Depends(get_db)):
    return [
        {"date": "2025-01-10", "count": 1},
        {"date": "2025-01-12", "count": 3}
    ]

@router.get("/admin/all")
def admin_all(db: Session = Depends(get_db), admin: Annotated[bool, Depends(require_admin)] = None):
    return []

@router.get("/admin/top", response_model=list[TopReferrerItem])
def admin_top(limit: int = 10, db: Session = Depends(get_db), admin: Annotated[bool, Depends(require_admin)] = None):
    return [
        {"user_id": 1, "successful_referrals": 12},
        {"user_id": 2, "successful_referrals": 8}
    ]

@router.post("/admin/reset/{referral_id}")
def admin_reset(referral_id: int, db: Session = Depends(get_db), admin: Annotated[bool, Depends(require_admin)] = None):
    return {"status": "reset"}
