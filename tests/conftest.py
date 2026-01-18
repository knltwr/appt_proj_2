from app.database.db_init import init_database, drop_database
from app.database.db import Database
from app.core.config import CONFIG
import traceback
import pytest
import pytest_asyncio
from app.dependencies import get_db
from app.main import app
from httpx import AsyncClient

@pytest_asyncio.fixture(scope="session")
async def test_db(): # can make async if needed
    try:
        drop_database(dbname = CONFIG.DATABASE_TEST_DB_NAME)
        init_database(
            dbname = CONFIG.DATABASE_TEST_DB_NAME,
            user = CONFIG.DATABASE_TEST_DB_USERNAME,
            password = CONFIG.DATABASE_TEST_DB_PASSWORD,
            host = CONFIG.DATABASE_TEST_DB_HOSTNAME,
            port = CONFIG.DATABASE_TEST_DB_PORT
        )
        test_db = Database(
            dbname = CONFIG.DATABASE_TEST_DB_NAME,
            user = CONFIG.DATABASE_TEST_DB_USERNAME,
            password = CONFIG.DATABASE_TEST_DB_PASSWORD,
            host = CONFIG.DATABASE_TEST_DB_HOSTNAME,
            port = CONFIG.DATABASE_TEST_DB_PORT 
        )
        print("Test database setup complete")
        await test_db.db_open()
        print("Test database opened")
        yield test_db
        print("Test database closed")
        await test_db.db_close()
        drop_database(dbname = CONFIG.DATABASE_TEST_DB_NAME)
        print("Test database teardown complete")
    except Exception as e:
        traceback.print_exc()
        raise e

@pytest_asyncio.fixture(scope="session")
async def override_dependency_db(test_db): # can make this async w/o an await b/c test_db is async
    app.dependency_overrides[get_db] = lambda: test_db # need to overlay lambda because whatever is assigned here gets called, and test_db is an object not callable
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="class")
async def reset_db_fixture_class_level(override_dependency_db, test_db): # making override_dependency_db, test_db (order matters) dependency to ensure it runs before this
    try:
        await test_db.reset_db()
        yield
    except Exception as e:
        traceback.print_exc()
        raise e
    
@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db_fixture_function_level(override_dependency_db, test_db): # making override_dependency_db, test_db (order matters) dependency to ensure it runs before this
    try:
        await test_db.reset_db()
        yield
    except Exception as e:
        traceback.print_exc()
        raise e
    
@pytest_asyncio.fixture(scope="function")
async def test_client(override_dependency_db): # making override_dependency_db a dependency to ensure it runs before this
    async with app.router.lifespan_context(app): # reusing same lifespan defined in main
        async with AsyncClient(app = app, base_url = "http://test") as test_client:
            yield test_client