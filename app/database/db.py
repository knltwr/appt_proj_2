import psycopg
from psycopg import sql
from psycopg.rows import dict_row
import re
import traceback
from app.config import CONFIG

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
        except psycopg.OperationalError as e:            
            if re.search(r"database.*does not exist", e.args[0]) and create_if_not_exists_db is True: # regex ".*" matches any characters
                try:
                    self.conn = self.setup_database(dbname = dbname)
                    self.dbname = dbname
                except Exception as e2:
                    if self.conn:
                        self.conn.close()
                    traceback.print_exc()
                    raise e2
            else:
                traceback.print_exc()
                raise e

    def setup_database(self,
                       dbname: str = CONFIG.DATABASE_NAME
                       ) -> psycopg.Connection:
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
                
                cur.execute(sql.SQL(
                    """
                        CREATE TABLE users (
                            user_id SERIAL PRIMARY KEY,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            UNIQUE (email)
                        );
                    """) # TIMESTAMP type should ignore timezone
                )
                cur.execute(sql.SQL(
                    """
                        CREATE TABLE IF NOT EXISTS services (
                            service_id SERIAL PRIMARY KEY,
                            host_id INTEGER NOT NULL,
                            service_name TEXT NOT NULL,
                            street_address TEXT NOT NULL,
                            city TEXT NOT NULL,
                            state TEXT NOT NULL,
                            zip_code TEXT NOT NULL,
                            phone_number TEXT UNIQUE NOT NULL,
                            is_open_mo INTEGER NOT NULL DEFAULT 0,
                            open_time_mo TEXT NOT NULL,
                            close_time_mo TEXT NOT NULL,
                            is_open_tu INTEGER NOT NULL DEFAULT 0,
                            open_time_tu TEXT NOT NULL,
                            close_time_tu TEXT NOT NULL,
                            is_open_we INTEGER NOT NULL DEFAULT 0,
                            open_time_we TEXT NOT NULL,
                            close_time_we TEXT NOT NULL,
                            is_open_th INTEGER NOT NULL DEFAULT 0,
                            open_time_th TEXT NOT NULL,
                            close_time_th TEXT NOT NULL,
                            is_open_fr INTEGER NOT NULL DEFAULT 0,
                            open_time_fr TEXT NOT NULL,
                            close_time_fr TEXT NOT NULL,
                            is_open_sa INTEGER NOT NULL DEFAULT 0,
                            open_time_sa TEXT NOT NULL,
                            close_time_sa TEXT NOT NULL,
                            is_open_su INTEGER NOT NULL DEFAULT 0,
                            open_time_su TEXT NOT NULL,
                            close_time_su TEXT NOT NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE
                        );
                    """)
                )
                cur.execute(sql.SQL(
                    """
                        CREATE TABLE IF NOT EXISTS appt_types (
                            appt_type_id SERIAL PRIMARY KEY,
                            service_id INTEGER NOT NULL,
                            appt_type_name TEXT NOT NULL,
                            appt_duration_minutes INTEGER NOT NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            UNIQUE (service_id, appt_type_name),
                            CHECK (appt_duration_minutes > 0),
                            FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
                        );
                    """)
                )
                cur.execute(sql.SQL(
                    """
                        CREATE TABLE IF NOT EXISTS appts (
                            appt_id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            service_id INTEGER NOT NULL,
                            appt_type_id INTEGER NOT NULL,
                            appt_starts_at TEXT NOT NULL,
                            appt_ends_at TEXT NOT NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
                            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                            FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE,
                            FOREIGN KEY (appt_type_id) REFERENCES appt_types(appt_type_id) ON DELETE CASCADE
                        );
                    """)
                )
                cur.close()
            return conn
        except Exception as e:
            if self.conn:
                self.conn.close() # if database did not set up correctly, do not want to continue
            traceback.print_exc()
            exit(1)
        
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
        
    def insert_user(self,
                    email: str, 
                    password: str
                    ) -> dict:
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
                          email: str
                          ) -> dict: # add in annotation for user model as return type? causes issue though if None returned from query
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
                          user_id: int
                          ) -> dict: # add in annotation for user model as return type? causes issue though if None returned from query
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
    
    def insert_service(self, 
                       host_id: int,
                       service_name: str, 
                       street_address: str, city: str, state: str, zip_code: str, 
                       phone_number: str, 
                       is_open_mo: int, open_time_mo: str, close_time_mo: str, 
                       is_open_tu: int, open_time_tu: str, close_time_tu: str,
                       is_open_we: int, open_time_we: str, close_time_we: str,
                       is_open_th: int, open_time_th: str, close_time_th: str,
                       is_open_fr: int, open_time_fr: str, close_time_fr: str,
                       is_open_sa: int, open_time_sa: str, close_time_sa: str,
                       is_open_su: int, open_time_su: str, close_time_su: str,
                       ) -> dict:
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        INSERT INTO services (
                            host_id,
                            service_name, 
                            street_address, city, state, zip_code, 
                            phone_number, 
                            is_open_mo, open_time_mo, close_time_mo, 
                            is_open_tu, open_time_tu, close_time_tu, 
                            is_open_we, open_time_we, close_time_we,
                            is_open_th, open_time_th, close_time_th,
                            is_open_fr, open_time_fr, close_time_fr,
                            is_open_sa, open_time_sa, close_time_sa,
                            is_open_su, open_time_su, close_time_su
                        ) 
                        VALUES (
                            %s,
                            %s, 
                            %s, %s, %s, %s,
                            %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s
                        )
                        RETURNING *;
                    """, 
                    (host_id,
                    service_name, 
                    street_address, city, state, zip_code, 
                    phone_number,
                    is_open_mo, open_time_mo, close_time_mo,
                    is_open_tu, open_time_tu, close_time_tu,
                    is_open_we, open_time_we, close_time_we,
                    is_open_th, open_time_th, close_time_th,
                    is_open_fr, open_time_fr, close_time_fr,
                    is_open_sa, open_time_sa, close_time_sa,
                    is_open_su, open_time_su, close_time_su,
                    )
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e
        
    def get_services_by_host_id(self,
                                host_id: int):
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        SELECT * FROM services WHERE host_id=%s;
                    """,
                    (host_id, )
                )
                return cursor.fetchall()
        except Exception as e:
            traceback.print_exc()
            raise e
    
    def get_service_by_service_id(self,
                                service_id: int):
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        SELECT * FROM services WHERE service_id=%s;
                    """,
                    (service_id, )
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e
        
    def insert_appt_type(self,
                    service_id: int, 
                    appt_type_name: str, 
                    appt_duration_minutes: int
                    ):
        try:
            # for some reason, could not use self.conn here b/c it would be closed when creating cursor, so created a new connection for just this function
            with psycopg.connect(dbname = self.dbname, 
                                   user = CONFIG.DATABASE_USERNAME, 
                                   password = CONFIG.DATABASE_PASSWORD, 
                                   host = CONFIG.DATABASE_HOSTNAME, 
                                   port = CONFIG.DATABASE_PORT, 
                                   row_factory = dict_row
                                   ) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                        INSERT INTO appt_types (service_id, appt_type_name, appt_duration_minutes) VALUES (%s, %s, %s) RETURNING *;
                    """, 
                    (service_id, appt_type_name, appt_duration_minutes)
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e