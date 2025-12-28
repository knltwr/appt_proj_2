from app.database.db_init import init_database, drop_database
from app.database.db import Database
from app.core.config import CONFIG
import traceback


def setup_test_db(): # can make async if needed
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
        test_db.db_open()
        yield test_db
        test_db.db_close()
        drop_database(dbname = CONFIG.DATABASE_TEST_DB_NAME)
    except Exception as e:
        traceback.print_exc()
        raise e
    

