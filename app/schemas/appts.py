from pydantic import BaseModel, field_validator
from app.core.config import CONFIG
from datetime import datetime
from app.utils.util_funcs import get_formatted_datetime, get_formatted_time

class ApptCreateRequest(BaseModel):
    service_id: int
    appt_type_name: str 
    appt_starts_at: datetime

    @field_validator("appt_starts_at")
    def validate_appt_starts_at(cls, appt_starts_at):
        return get_formatted_datetime(appt_starts_at)

class ApptCreateResponse(BaseModel):
    appt_id: int
    user_id: int
    service_id: int
    appt_type_name: str
    appt_starts_at: datetime
    appt_ends_at: datetime
    created_at: datetime
    updated_at: datetime