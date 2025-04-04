from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import users
from app.utils.utils import get_hashed_salted_password
from app.database.db import Database
import psycopg

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("", status_code = status.HTTP_201_CREATED, response_model = users.UserCreateResponse)
def user_create(user: users.UserCreateRequest, db: Database = Depends(Database)):
      
    user.password = get_hashed_salted_password(user.password)

    try:
        ret = db.insert_user(**user.model_dump())
        return ret
    except psycopg.errors.UniqueViolation as e:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Email in use") # instead of checking whether email is in use beforehand, using the database error
    except psycopg.Error:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Database issue occurred")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Non-database issue occurred")