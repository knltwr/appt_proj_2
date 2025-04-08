import psycopg
from psycopg import sql
from psycopg.rows import dict_row
import re
import traceback
from app.config import CONFIG

# TODO: use config to rename hard-coded strings like "postgres"
class Database:

    conn = None
    dbname = None
    
    def __init__(self, 
                 dbname: str = CONFIG.DATABASE_NAME, 
                 user: str = CONFIG.DATABASE_USERNAME, 
                 password: str = CONFIG.DATABASE_PASSWORD, 
                 host: str = CONFIG.DATABASE_HOSTNAME, 
                 port: int = CONFIG.DATABASE_PORT, 
                 row_factory: object = dict_row,
                 create_if_not_exists_db: bool = False
                 ):
        try:
            self.conn = psycopg.connect(dbname = dbname, 
                                        user = user, 
                                        password = password, 
                                        host = host, 
                                        port = port, 
                                        row_factory = row_factory
                                        )
            self.dbname = dbname
        except psycopg.OperationalError as e: # want to specifically handle OperationalError for db not existing here ... otherwise, let caller handle exception
            # handle database does not exist error by creating it if the bool is True
            
            if re.search(r"database.*does not exist", e.args[0]) and create_if_not_exists_db is True: # regex ".*" matches any characters
                try:
                    self.conn = self.setup_database(dbname = dbname)
                    self.dbname = dbname
                except Exception as e2:
                    if self.conn:
                        self.conn.close()
                    traceback.print_exc()
                    raise(e2)
            else:
                traceback.print_exc()
                raise e

    def setup_database(self,
                       dbname: str = CONFIG.DATABASE_NAME):
        conn = None
        try:
            conn = psycopg.connect(dbname = CONFIG.DATABASE_DEFAULT_DB_NAME, 
                                   user = CONFIG.DATABASE_DEFAULT_DB_USERNAME, 
                                   password = CONFIG.DATABASE_DEFAULT_DB_PASSWORD, 
                                   host = CONFIG.DATABASE_DEFAULT_DB_HOSTNAME, 
                                   port = CONFIG.DATABASE_DEFAULT_DB_PORT, 
                                   row_factory = dict_row
                                   ) # postgres is default DB always there
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
                                   user = CONFIG.DATABASE_DEFAULT_DB_USERNAME, 
                                   password = CONFIG.DATABASE_DEFAULT_DB_PASSWORD, 
                                   host = CONFIG.DATABASE_DEFAULT_DB_HOSTNAME, 
                                   port = CONFIG.DATABASE_DEFAULT_DB_PORT, 
                                   row_factory = dict_row
                                   )
            with conn:
                conn.cursor().execute(sql.SQL(
                    """
                        CREATE TABLE users (
                        user_id SERIAL PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
                        updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp
                        );
                    """) # TIMESTAMP type should ignore timezone
                )
            return conn
        except Exception as e:
            if self.conn:
                self.conn.close()
            traceback.print_exc()
            raise e
        
    def drop_database(self,
                      dbname: str = CONFIG.DATABASE_NAME):
        if dbname == CONFIG.DATABASE_DEFAULT_DB_NAME:
            raise Exception(f"Tried to drop {CONFIG.DATABASE_DEFAULT_DB_NAME}")
        try:
            conn = psycopg.connect(dbname = CONFIG.DATABASE_DEFAULT_DB_NAME, 
                                   user = CONFIG.DATABASE_DEFAULT_DB_USERNAME, 
                                   password = CONFIG.DATABASE_DEFAULT_DB_PASSWORD, 
                                   host = CONFIG.DATABASE_DEFAULT_DB_HOSTNAME, 
                                   port = CONFIG.DATABASE_DEFAULT_DB_PORT, 
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
        
    def insert_user(self,
                    email: str, 
                    password: str) -> dict:
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        INSERT INTO users(email, password) VALUES (%s, %s) RETURNING *;
                    """,
                    (email, password,)
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e
        
    def get_user_by_email(self,
                          email: str) -> dict: # add in annotation for user model as return type? causes issue though if None returned from query
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        SELECT * FROM users WHERE email=%s;
                    """,
                    (email, )
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e

    def get_user_by_user_id(self,
                          user_id: int) -> dict: # add in annotation for user model as return type? causes issue though if None returned from query
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        SELECT * FROM users WHERE user_id=%s;
                    """,
                    (user_id, )
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e
        
        


### Use singleton?
# def singleton(cls):
#     instances = {}

#     def getinstance():
#         if cls not in instances:
#             instances[cls] = cls()
#         return instances[cls]

#     return getinstance

# Only <=1 instance of the database driver
# exists within the app at all times
# DatabaseDriver = singleton(DatabaseDriver)


### SHOULD USE DATABASE CONNECTION POOL?


# # Open a cursor to perform database operations
# cur = conn.cursor()

# # Execute a query
# cur.execute("SELECT * FROM my_data")

# # Retrieve query results
# records = cur.fetchall()

