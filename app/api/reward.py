from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.core.database import get_db
from app.core.security import require_admin
from app.crud import reward as reward_crud
from app.schemas.reward import RewardSummaryResponse, RewardHistoryItem, RewardConfigResponse

router = APIRouter(prefix="/api/rewards", tags=["rewards"])

# User routes
@router.get("/summary", response_model=RewardSummaryResponse)
def get_reward_summary(user_id: str, db: Session = Depends(get_db)):
    """Get reward summary for user"""
    return reward_crud.get_reward_summary(db, user_id)

@router.get("/history", response_model=List[RewardHistoryItem])
def get_reward_history(user_id: str, db: Session = Depends(get_db)):
    """Get reward history for user"""
    return reward_crud.get_reward_history(db, user_id)

# Admin routes
@router.get("/admin/pending")
def get_pending_rewards(
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Get pending rewards for admin approval"""
    return reward_crud.get_pending_rewards(db)

@router.post("/admin/rewards/{reward_id}/credit")
def credit_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Credit a pending reward"""
    try:
        reward_crud.credit_reward(db, reward_id)
        return {"status": "success", "message": f"Reward {reward_id} credited"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/rewards/{reward_id}/revoke")
def revoke_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Revoke a reward"""
    try:
        reward_crud.revoke_reward(db, reward_id)
        return {"status": "success", "message": f"Reward {reward_id} revoked"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/config", response_model=RewardConfigResponse)
def create_reward_config(
    reward_type: str,
    reward_value: int,
    reward_unit: str = "points",
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Create or update reward configuration"""
    return reward_crud.create_reward_config(db, reward_type, reward_value, reward_unit)

@router.get("/admin/configs", response_model=List[RewardConfigResponse])
def list_reward_configs(
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    """Get all reward configurations"""
    return reward_crud.get_all_reward_configs(db)