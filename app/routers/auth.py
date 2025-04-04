from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import auth, users
from app.utils.utils import is_correct_password
from app.database.db import Database
import psycopg

router = APIRouter(prefix="/login", tags=['Authentication'])

@router.post("")
def login(login_req: auth.LoginRequest, db: Database = Depends()):

    try:
        user: users.UserFromDB = db.get_user_by_email(login_req.email)
        if user is None:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Invalid login")
        if not is_correct_password(login_req.password, user.password):
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Invalid login")
        
    except psycopg.Error:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Database issue occurred")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Non-database issue occurred")
