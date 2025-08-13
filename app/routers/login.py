from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import oauth2 as schemas_oauth2
from app.schemas import users as schemas_users
from app.utils.util_funcs import is_correct_password
from app.database.db import Database
import psycopg
import app.utils.oauth2 as oauth2
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/login", tags=['Authentication'])

@router.post("", status_code = status.HTTP_200_OK, response_model = schemas_oauth2.Token)
async def login(login_req: OAuth2PasswordRequestForm = Depends(), db: Database = Depends()): # login_req: auth.LoginRequest ... OAuth2PasswordRequestForm looks for Form Data in request

    try:
        user_from_db = await db.get_user_by_email(login_req.username) # username is the term OAuth2PasswordRequestForm uses, but it maps to the email for us
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")

    if user_from_db is None:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Invalid login")
    
    user = schemas_users.UserFromDB(**user_from_db)
            
    if not is_correct_password(login_req.password, user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Invalid login")
    
    user_id = int(user.user_id)
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Some issue occurred")
    
    access_token = oauth2.create_access_token({"user_id": user_id})
    return access_token
