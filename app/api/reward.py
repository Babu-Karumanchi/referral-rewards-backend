from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import get_db
from app.core.security import require_admin
from app.crud import reward as reward_crud
from app.schemas.reward import RewardSummaryResponse, RewardHistoryItem, RewardConfigResponse

router = APIRouter(prefix="/api/rewards", tags=["rewards"])

@router.get("/summary", response_model=RewardSummaryResponse)
def get_reward_summary(db: Session = Depends(get_db)):
    try:
        user_id = 1  # TODO: JWT
        summary = reward_crud.get_reward_summary(db, user_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=list[RewardHistoryItem])
def get_reward_history(db: Session = Depends(get_db)):
    try:
        user_id = 1  # TODO: JWT
        history = reward_crud.get_reward_history(db, user_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ADMIN ROUTES (protected)
@router.post("/admin/rewards/{reward_id}/credit")
def credit_reward(
    reward_id: int, 
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    try:
        reward_crud.credit_reward(db, reward_id)
        return {"status": "credited"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/rewards/{reward_id}/revoke")
def revoke_reward(
    reward_id: int, 
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    try:
        reward_crud.revoke_reward(db, reward_id)
        return {"status": "revoked"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/config")
def create_reward_config(
    reward_type: str,
    reward_value: int,
    reward_unit: str,
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    try:
        config = reward_crud.create_reward_config(db, reward_type, reward_value, reward_unit)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/config", response_model=list[RewardConfigResponse])
def get_all_reward_configs(
    db: Session = Depends(get_db),
    admin: Annotated[bool, Depends(require_admin)] = None
):
    try:
        configs = reward_crud.get_all_reward_configs(db)
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
