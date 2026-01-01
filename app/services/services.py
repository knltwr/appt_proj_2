from fastapi import status, HTTPException
from app.schemas import oauth2 as schemas_oauth2
from app.database.db import Database
import psycopg
from app.core.oauth2 import get_current_user
from app.schemas import services as schemas_services
from app.schemas import appt_types as schemas_appt_types

async def service_services_create(service: schemas_services.ServiceCreateRequest, db: Database, user_id: int):

    data_for_db: dict = service.model_dump()
    data_for_db.update({"host_id": user_id})

    try:
        service_from_db = await db.insert_service(**data_for_db)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    
    return service_from_db


async def service_services_get(db: Database, user_id: int):

    try:
        services_from_db = await db.get_services_by_host_id(user_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if services_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Services not found")
    
    return services_from_db


async def service_services_get_by_id(service_id: int, db: Database, user_id: int):

    try:
        service_from_db = await db.get_service_by_service_id(service_id)
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Service not found")
    
    if service_from_db.get("host_id") != user_id:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid service_id")
    
    return service_from_db

async def service_appt_types_create(service_id: int, appt_type: schemas_appt_types.ApptTypeCreateRequest, db: Database, user_id: int):

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
    
    return appt_type_from_db
    