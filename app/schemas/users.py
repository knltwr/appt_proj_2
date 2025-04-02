from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    user_id: int
    created_at: datetime
