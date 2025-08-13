from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import oauth2 as schemas_oauth2
from app.database.db import Database
import psycopg
from app.utils.oauth2 import get_current_user
from app.schemas import services as schemas_services
from app.schemas import appt_types as schemas_appt_types

router = APIRouter(prefix="/services", tags=['Services'])

@router.post("", status_code = status.HTTP_201_CREATED, response_model = schemas_services.ServiceCreateResponse)
async def service_create(service: schemas_services.ServiceCreateRequest, db: Database = Depends(Database), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):
      
    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    data_for_db: dict = service.model_dump()
    data_for_db.update({"host_id": user_id})

    try:
        service_from_db = await db.insert_service(**data_for_db)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return schemas_services.ServiceCreateResponse(**service_from_db) # if Pydantic model is not followed, this throws error

@router.get("", status_code=status.HTTP_200_OK, response_model= list[schemas_services.ServiceGetResponse])
async def service_get(db: Database = Depends(Database), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though
    
    try:
        services_from_db = await db.get_services_by_host_id(user_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if services_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Services not found")
    
    ret = list()
    for service in services_from_db:
        ret.append(schemas_services.ServiceGetResponse(**service))

    return ret # if Pydantic model is not followed, this throws error

@router.get("/{service_id}", status_code=status.HTTP_200_OK, response_model= schemas_services.ServiceGetResponse)
async def service_get(service_id: int, db: Database = Depends(Database), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though
    
    try:
        service_from_db = await db.get_service_by_service_id(service_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Service not found")
    
    if service_from_db.get("host_id") != user_id:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid service_id")
    
    return schemas_services.ServiceGetResponse(**service_from_db)

@router.post("/{service_id}/appt-types", status_code = status.HTTP_201_CREATED, response_model = schemas_appt_types.ApptTypeCreateResponse)
async def appt_types_create(service_id: int, appt_type: schemas_appt_types.ApptTypeCreateRequest, db: Database = Depends(Database), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    try:
        service_from_db = await db.get_service_by_service_id(service_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid service_id")
    
    if service_from_db.get("host_id") != user_id:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid service_id")

    try:
        appt_type_dict = appt_type.model_dump()
        appt_type_dict.update({"service_id": service_id})
        appt_type_from_db = await db.insert_appt_type(**appt_type_dict)

    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    return schemas_appt_types.ApptTypeCreateResponse(**appt_type_from_db)
    