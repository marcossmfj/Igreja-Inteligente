from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScheduleCreate(BaseModel):
    member_id: int
    position_id: Optional[int] = None
    template_id: Optional[int] = None
    event_name: str
    event_date: datetime

class ScheduleUpdate(BaseModel):
    member_id: Optional[int] = None
    position_id: Optional[int] = None
    confirmed: Optional[bool] = None

class AutoGenerateRequest(BaseModel):
    template_id: int
    event_name: str
    event_date: datetime

class AutoGenerateBatchRequest(BaseModel):
    template_id: int
    event_name: str
    start_date: datetime
    end_date: datetime
    days_of_week: List[int] # 0=Segunda, 6=Domingo
