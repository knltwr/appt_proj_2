from fastapi import FastAPI, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from typing import Optional
from app.database.db import Database
from app.routers.users import router as users_router
import json

app = FastAPI()
app.include_router(users_router) # add routers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(json.dumps({"success": False, "data": str(exc)}), status_code= status.HTTP_422_UNPROCESSABLE_ENTITY) # str(exc.errors())}

@app.get('/')
def root():
    return {
        "success":True,
        "data": "root"
        }