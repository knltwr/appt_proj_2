from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import users
from app.utils.utils import get_hashed_salted_password
from app.database.db import Database
import psycopg
from app.utils.oauth2 import get_current_user
from app.schemas import services as schemas_services

router = APIRouter(prefix="/services", tags=['Services'])
# POST route to create a service when a user is logged in
# GET /{service_id} w/ path parameter for service id to see its details, must be logged in and must be service of logged in user
# GET gets all services for logged in user