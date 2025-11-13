from fastapi import APIRouter, status, Depends, HTTPException
from app.utils.util_funcs import get_hashed_salted_password
from app.database.db import Database
import psycopg
from app.core.oauth2 import get_current_user
from app.schemas import users as schemas_users
from app.schemas import oauth2 as schemas_oauth2
from app.services.service_users import service_user_create, service_user_get

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("", status_code = status.HTTP_201_CREATED, response_model = schemas_users.UserCreateResponse)
async def user_create(user: schemas_users.UserCreateRequest, db: Database = Depends()):
      
    user_from_db = await service_user_create(user, db)
    
    return schemas_users.UserCreateResponse(**user_from_db) # if Pydantic model is not followed, this throws error
    
@router.get("", status_code = status.HTTP_200_OK, response_model = schemas_users.UserGetResponse)
async def user_get(db: Database = Depends(), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    user_from_db = await service_user_get(db, user_id)
    
    return schemas_users.UserGetResponse(**user_from_db) # if Pydantic model is not followed, this throws error