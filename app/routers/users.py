from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import users
from app.utils.utils import get_hashed_salted_password
from app.database.db import Database
import psycopg
from app.utils.oauth2 import get_current_user
from app.schemas.oauth2 import TokenPayload

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("", status_code = status.HTTP_201_CREATED, response_model = users.UserCreateResponse)
def user_create(user: users.UserCreateRequest, db: Database = Depends(Database)):
      
    user.password = get_hashed_salted_password(user.password)

    try:
        user_from_db = db.insert_user(**user.model_dump())
    except psycopg.errors.UniqueViolation as e:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Email in use") # instead of checking whether email is in use beforehand, using the database error
    except psycopg.Error:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Database issue occurred")
    
    return users.UserCreateResponse(**user_from_db) # if Pydantic model is not followed, this throws error
    
@router.get("", status_code = status.HTTP_200_OK, response_model = users.UserGetResponse)
def user_get(db: Database = Depends(Database), payload: TokenPayload = Depends(get_current_user)):
    
    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    try:
        user_from_db: users.UserFromDB = db.get_user_by_user_id(user_id)
    except psycopg.Error:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Database issue occurred")
    
    return users.UserGetResponse(**user_from_db.model_dump()) # if Pydantic model is not followed, this throws error