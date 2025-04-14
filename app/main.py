from fastapi import FastAPI, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from typing import Optional
from app.routers import login, users, services

import json

app = FastAPI()
app.include_router(users.router)
app.include_router(login.router)
app.include_router(services.router)
app.include_router(appts.router)

# RequestValidationError is for when Pydantic throws an error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(json.dumps({"success": False, "data": str(exc)}), status_code= status.HTTP_422_UNPROCESSABLE_ENTITY) # str(exc.errors())}

@app.get('/')
def root():
    return {
        "success":True,
        "data": "root"
        }