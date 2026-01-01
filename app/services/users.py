from fastapi import APIRouter, status, Depends, HTTPException
from app.utils.util_funcs import get_hashed_salted_password
from app.database.db import Database
import psycopg
from app.core.oauth2 import get_current_user
from app.schemas import users as schemas_users
from app.schemas import oauth2 as schemas_oauth2


async def service_user_create(user: schemas_users.UserCreateRequest, db: Database):
      
    user.password = get_hashed_salted_password(user.password)

    try:
        user_from_db = await db.insert_user(**user.model_dump())
    except psycopg.errors.UniqueViolation as e:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = f"Email in use: {e}") # instead of checking whether email is in use beforehand, using the database error
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if user_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return user_from_db
    

async def service_user_get(db: Database, user_id: int):

    try:
        user_from_db = await db.get_user_by_user_id(user_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if user_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return user_from_db