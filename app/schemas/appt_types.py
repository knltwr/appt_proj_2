from pydantic import BaseModel, field_validator
from app.core.config import CONFIG
from datetime import datetime

class ApptTypeCreateRequest(BaseModel):
    appt_type_name: str 
    appt_duration_minutes: int

class ApptTypeCreateResponse(BaseModel):
    appt_type_id: int
    service_id: int
    appt_type_name: str
    appt_duration_minutes: int
    created_at: datetime
    updated_at: datetime