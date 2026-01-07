from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RewardSummaryResponse(BaseModel):
    total_earned: int
    pending: int
    credited: int
    unit: str

class RewardHistoryItem(BaseModel):
    id: int
    reward_type: str
    reward_value: int
    reward_unit: str
    status: str
    created_at: datetime

class RewardConfigCreate(BaseModel):
    reward_type: str
    reward_value: int
    reward_unit: str
    is_active: bool = True

class RewardConfigResponse(BaseModel):
    id: int
    reward_type: str
    reward_value: int
    reward_unit: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
