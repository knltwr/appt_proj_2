from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import oauth2 as schemas_oauth2
from app.database.db import Database
from app.core.oauth2 import get_current_user
from app.schemas import services as schemas_services
from app.schemas import appt_types as schemas_appt_types
from app.services.services import service_services_create, service_services_get, service_services_get_by_id, service_appt_types_create
from app.dependencies import get_db

router = APIRouter(prefix="/services", tags=['Services'])

@router.post("", status_code = status.HTTP_201_CREATED, response_model = schemas_services.ServiceCreateResponse)
async def services_create(service: schemas_services.ServiceCreateRequest, db: Database = Depends(get_db), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):
      
    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    service_from_db = await service_services_create(service, db, user_id)
    
    return schemas_services.ServiceCreateResponse(**service_from_db) # if Pydantic model is not followed, this throws error

@router.get("", status_code=status.HTTP_200_OK, response_model= list[schemas_services.ServiceGetResponse])
async def services_get(db: Database = Depends(get_db), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though
    
    services_from_db = await service_services_get(db, user_id)
    
    ret = list()
    for service in services_from_db:
        ret.append(schemas_services.ServiceGetResponse(**service))

    return ret # if Pydantic model is not followed, this throws error

@router.get("/{service_id}", status_code=status.HTTP_200_OK, response_model= schemas_services.ServiceGetResponse)
async def services_get_by_id(service_id: int, db: Database = Depends(get_db), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though
    
    service_from_db = await service_services_get_by_id(service_id, db, user_id)
    
    return schemas_services.ServiceGetResponse(**service_from_db)

@router.post("/{service_id}/appt-types", status_code = status.HTTP_201_CREATED, response_model = schemas_appt_types.ApptTypeCreateResponse)
async def appt_types_create(service_id: int, appt_type: schemas_appt_types.ApptTypeCreateRequest, db: Database = Depends(get_db), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):

    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though

    appt_type_from_db = await service_appt_types_create(service_id, appt_type, db, user_id)
    
    return schemas_appt_types.ApptTypeCreateResponse(**appt_type_from_db)
    