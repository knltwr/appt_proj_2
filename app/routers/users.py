from fastapi import APIRouter, status, Depends, HTTPException
from ..schemas import users
from ..utils.utils import get_hashed_salted_password
from app.database.db import Database
import psycopg

router = APIRouter(prefix="/users")


@router.post("", status_code = status.HTTP_201_CREATED, response_model=users.UserCreateResponse)
def user_create(user: users.UserCreateRequest, db: Database = Depends(Database)):
    
    # TODO: check if email already used
    
    user.password = get_hashed_salted_password(user.password)
    try:
        ret = db.insert_user(**user.model_dump())
        return ret
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email in use")
    except psycopg.Error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database issue occurred")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Non-database issue occurred")