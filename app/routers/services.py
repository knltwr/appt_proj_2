from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import oauth2 as schemas_oauth2
from app.utils.utils import get_hashed_salted_password
from app.database.db import Database
import psycopg
from app.utils.oauth2 import get_current_user
from app.schemas import services as schemas_services

router = APIRouter(prefix="/services", tags=['Services'])
# POST route to create a service when a user is logged in
# GET /{service_id} w/ path parameter for service id to see its details, must be logged in and must be service of logged in user
# GET gets all services for logged in user

@router.post("", status_code = status.HTTP_201_CREATED, response_model = schemas_services.ServiceCreateResponse)
def service_create(service: schemas_services.ServiceCreateRequest, db: Database = Depends(Database), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):
      
    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    print(service)
    data_for_db: dict = service.model_dump()
    print(data_for_db)
    data_for_db.update({"host_id": user_id})
    print
    try:
        service_from_db = db.insert_service(**data_for_db)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return schemas_services.ServiceCreateResponse(**service_from_db) # if Pydantic model is not followed, this throws error