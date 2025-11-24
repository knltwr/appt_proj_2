from app.database.db import Database, db

async def get_db() -> Database:
    return db