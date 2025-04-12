from pydantic import BaseModel, field_validator
from app.config import CONFIG
from datetime import datetime

class ServiceCreateRequest(BaseModel):
    service_name: str
    street_address: str
    city: str
    state: str
    zip_code: str
    phone_number: str
    is_open_mo: int = 0
    is_open_tu: int = 0
    is_open_we: int = 0
    is_open_th: int = 0
    is_open_fr: int = 0
    is_open_sa: int = 0
    is_open_su: int = 0
    open_time_mo: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    open_time_tu: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    open_time_we: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    open_time_th: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    open_time_fr: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    open_time_sa: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    open_time_su: str = CONFIG.SERVICE_DEFAULT_OPEN_TIME
    close_time_mo: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME
    close_time_tu: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME
    close_time_we: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME
    close_time_th: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME
    close_time_fr: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME
    close_time_sa: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME
    close_time_su: str = CONFIG.SERVICE_DEFAULT_CLOSE_TIME

    @field_validator("is_open_mo","is_open_tu","is_open_we","is_open_th","is_open_fr","is_open_sa","is_open_su")
    def validate_is_open(cls, is_open):
        if is_open not in (0, 1):
            raise ValueError("is_open_* must be 0 or 1")
        return is_open
        
class ServiceCreateResponse(ServiceCreateRequest):
    host_id: int
    created_at: datetime
    updated_at: datetime
