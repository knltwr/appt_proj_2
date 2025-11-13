from fastapi import APIRouter, status, Depends
from app.schemas import oauth2 as schemas_oauth2
from app.utils.util_funcs import is_correct_password
from app.database.db import Database
from fastapi.security import OAuth2PasswordRequestForm
from app.services.service_login import service_login

router = APIRouter(prefix="/login", tags=['Authentication'])

@router.post("", status_code = status.HTTP_200_OK, response_model = schemas_oauth2.Token)
async def login(login_req: OAuth2PasswordRequestForm = Depends(), db: Database = Depends()): # login_req: auth.LoginRequest ... OAuth2PasswordRequestForm looks for Form Data in request
    
    access_token = await service_login(login_req, db)
    
    return access_token
