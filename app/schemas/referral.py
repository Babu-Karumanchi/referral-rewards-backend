from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReferralApplyRequest(BaseModel):
    referral_code: str

class ReferralSummaryResponse(BaseModel):
    my_referral_code: str
    total_referrals: int
    successful_referrals: int
    conversion_rate: str

class ReferralListItem(BaseModel):
    used_by_user_id: Optional[int]
    used_at: Optional[datetime]
    status: str

class ReferralTimelineItem(BaseModel):
    date: str
    count: int

class TopReferrerItem(BaseModel):
    user_id: int
    successful_referrals: int


