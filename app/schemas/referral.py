from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# This is the one missing that caused your crash
class ReferralApplyRequest(BaseModel):
    referral_code: str

class ReferralSummaryResponse(BaseModel):
    my_referral_code: str
    total_referrals: int
    successful_referrals: int
    conversion_rate: str
    
    model_config = ConfigDict(from_attributes=True)

class ReferralListItem(BaseModel):
    used_by_user_id: Optional[str]
    used_at: Optional[datetime]
    status: str

    model_config = ConfigDict(from_attributes=True)

class ReferralTimelineItem(BaseModel):
    date: str
    count: int

class TopReferrerItem(BaseModel):
    user_id: str
    successful_referrals: int

    model_config = ConfigDict(from_attributes=True)