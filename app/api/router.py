from fastapi import APIRouter
from app.api.v1 import appts, login, services, users

router = APIRouter()

router.include_router(appts.router, prefix = '/v1')
router.include_router(login.router, prefix = '/v1')
router.include_router(services.router, prefix = '/v1')
router.include_router(users.router, prefix = '/v1')

# do need to need to invalidate old api version ... e.g. with /v1, when /v2 routes are introduced, the above lines will remain