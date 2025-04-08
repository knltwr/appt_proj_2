from fastapi import APIRouter, status, Depends, HTTPException
from app.utils.utils import get_hashed_salted_password
from app.database.db import Database
import psycopg
from app.utils.oauth2 import get_current_user
from app.schemas import users as schemas_users
from app.schemas import oauth2 as schemas_oauth2

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("", status_code = status.HTTP_201_CREATED, response_model = schemas_users.UserCreateResponse)
def user_create(user: schemas_users.UserCreateRequest, db: Database = Depends(Database)):
      
    user.password = get_hashed_salted_password(user.password)

    try:
        user_from_db = db.insert_user(**user.model_dump())
    except psycopg.errors.UniqueViolation as e:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = f"Email in use: {e}") # instead of checking whether email is in use beforehand, using the database error
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if user_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return schemas_users.UserCreateResponse(**user_from_db) # if Pydantic model is not followed, this throws error
    
@router.get("", status_code = status.HTTP_200_OK, response_model = schemas_users.UserGetResponse)
def user_get(db: Database = Depends(Database), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    try:
        user_from_db = db.get_user_by_user_id(user_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if user_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return schemas_users.UserGetResponse(**user_from_db) # if Pydantic model is not followed, this throws error