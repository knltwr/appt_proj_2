import os
import asyncio
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from app.api.router import router
from contextlib import asynccontextmanager
from app.dependencies import get_db

import json

# to make available the database and connection pool before the app is up and running
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await get_db()
    await db.db_open()
    yield # this hands off control to the FastAPI app, and returns to run the below statements when the app is shut down
    await db.db_close()


app = FastAPI(lifespan = lifespan)
app.include_router(router, prefix = '/api')



# RequestValidationError is for when Pydantic throws an error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(json.dumps({"success": False, "data": str(exc)}), status_code= status.HTTP_422_UNPROCESSABLE_ENTITY) # str(exc.errors())}


import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host = "127.0.0.1", port = 8000, reload = False) # had to do this instead of CLI uvicorn b/c of this on windows affecting asyncio