from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    user_id: int

class UserFromDB(BaseModel):
    user_id: int
    email: EmailStr
    password: str
    created_at: datetime
    updated_at: datetime

class UserGetResponse(BaseModel):
    user_id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime