from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import oauth2 as schemas_oauth2
from app.database.db import Database
from app.core.oauth2 import get_current_user
from app.schemas import appts as schemas_appts
from app.services.service_appts import service_appt_create

router = APIRouter(prefix="/appts", tags=['Appointments'])

@router.post("", status_code = status.HTTP_201_CREATED, response_model = schemas_appts.ApptCreateResponse)
async def appt_create(appt: schemas_appts.ApptCreateRequest, db: Database = Depends(), payload: schemas_oauth2.TokenPayload = Depends(get_current_user)):
      
    user_id = int(payload.user_id)
    
    if user_id is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Something went wrong")  # this shouldn't happen though
    
    created_appt = await service_appt_create.appt_create(appt, db, user_id)
    
    return schemas_appts.ApptCreateResponse(**created_appt) # if Pydantic model is not followed, this throws error