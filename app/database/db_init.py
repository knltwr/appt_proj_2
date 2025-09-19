import psycopg
# from app.database.db import Database
from app.config import CONFIG
import traceback
from psycopg.rows import dict_row
from psycopg import sql
from pathlib import Path

def drop_database(self,
                    dbname: str = CONFIG.DATABASE_NAME
                    ) -> None:
    
    if dbname == CONFIG.DATABASE_MAINT_DB_NAME:
        raise Exception(f"Tried to drop maintenance database: {CONFIG.DATABASE_MAINT_DB_NAME}")
    
    try:
        conn = psycopg.connect(dbname = CONFIG.DATABASE_MAINT_DB_NAME, 
                                user = CONFIG.DATABASE_MAINT_DB_USERNAME, 
                                password = CONFIG.DATABASE_MAINT_DB_PASSWORD, 
                                host = CONFIG.DATABASE_MAINT_DB_HOSTNAME, 
                                port = CONFIG.DATABASE_MAINT_DB_PORT, 
                                row_factory = dict_row
                                )
        with conn:
            conn.autocommit = True
            conn.cursor().execute(sql.SQL(
                """
                    DROP DATABASE IF EXISTS {sql_dbname};
                """).format(sql_dbname = sql.Identifier(dbname))
            )
    except Exception as e:
        if conn:
            conn.close()
        traceback.print_exc()
        raise e
    

def init_database(self,
                    dbname: str = CONFIG.DATABASE_NAME
                    ) -> None:
    conn = None
    try:
        conn = psycopg.connect(dbname = CONFIG.DATABASE_MAINT_DB_NAME, 
                                user = CONFIG.DATABASE_MAINT_DB_USERNAME, 
                                password = CONFIG.DATABASE_MAINT_DB_PASSWORD, 
                                host = CONFIG.DATABASE_MAINT_DB_HOSTNAME, 
                                port = CONFIG.DATABASE_MAINT_DB_PORT, 
                                row_factory = dict_row
                                )
        conn.autocommit = True # this is necessary for DDL
        with conn:
            conn.cursor().execute(sql.SQL(
                """
                    CREATE DATABASE {sql_dbname};
                """).format(sql_dbname = sql.Identifier(dbname))
            )
        # exiting context manager commits the change or rollbacks all changes if exception is raised
        conn.close()
        del conn
        
        conn = psycopg.connect(dbname = dbname, 
                                user = CONFIG.DATABASE_USERNAME, 
                                password = CONFIG.DATABASE_PASSWORD, 
                                host = CONFIG.DATABASE_HOSTNAME, 
                                port = CONFIG.DATABASE_PORT, 
                                row_factory = dict_row
                                )
        with conn:
            cur = conn.cursor()
            
            dir = Path(CONFIG.DATABASE_MIGRATIONS_RELATIVE_PATH)
            f_list = list()
            
            # iterate through the files in the migrations directory, and store the filenames
            for f in dir.iterdir():
                if f.name.endswith(".up.sql"): # convention is that up-migrations end with up.sql, and down-migrations end with down.sql
                    f_list.append(f.name)
            
            # want to run scripts in order
            f_list.sort()
            print(f_list)
            
            # execute each script
            for f_name in f_list:
                f_path = dir / f_name
                with open(f_path, "r") as f:
                    cur.execute(f.read())
                    print(f"Executed {str(f_path)}")

            cur.close()
    except Exception as e:
        if self.pool:
            self.pool.close() # if database did not set up correctly, do not want to continue
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    try:
        drop_database(CONFIG.DATABASE_NAME)
        print(f"Dropped {CONFIG.DATABASE_NAME}")
        init_database(CONFIG.DATABASE_NAME)
        print(f"Created {CONFIG.DATABASE_NAME}")    
    except psycopg.Error as e:
        traceback.print_exc()