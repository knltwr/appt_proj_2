import psycopg
from psycopg import sql
from psycopg.rows import dict_row
import re
import traceback
from app.config import CONFIG
from app.utils.other_funcs import singleton
from pathlib import Path

# @singleton
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
                    self.conn = self.init_database(dbname = dbname)
                    self.dbname = dbname
                except Exception as e2:
                    if self.conn:
                        self.conn.close()
                    traceback.print_exc()
                    raise e2
            else:
                traceback.print_exc()
                raise e

    def init_database(self,
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
    
    def get_appt_type_by_service_id_and_appt_type_name(self, 
                                                       service_id: int,
                                                       appt_type_name: str):
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
                        SELECT * FROM appt_types WHERE service_id=%s AND appt_type_name=%s;
                    """,
                    (service_id, appt_type_name, )
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e
        
    def get_conflicting_appt(self, 
                              service_id: int,
                              appt_type_name: str,
                              appt_starts_at: str, 
                              appt_ends_at: str):
        """
        Checks if there exists any appointment that conflicts with the time slot provided in the arguments. Returns None if no conflict.

        :param int service_id: service_id
        :param str appt_starts_at: timestamp of when the appointment should start
        :param str appt_ends_at: timestamp of when the appointment should end
        :return: data of the existing conflicting appointment
        :rtype: dict | None
        """
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
                        SELECT appt_id 
                        FROM appts
                        WHERE service_id = %s -- service_id
                        AND appt_type_name = %s
                        AND (
                            (%s >= appt_starts_at AND %s < appt_ends_at) -- appt_starts_at, appt_starts_at
                            OR 
                            (%s > appt_starts_at AND %s <= appt_ends_at) -- appt_ends_at, appt_ends_at
                        ) 
                    """,
                    (service_id,
                    appt_type_name,
                    appt_starts_at, appt_starts_at, 
                    appt_ends_at, appt_ends_at,)
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e
    
    def insert_appt(self,
                    user_id: int,
                    service_id: int,
                    appt_type_name: str,
                    appt_starts_at: str,
                    appt_ends_at: str
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
                        INSERT INTO appts (user_id, service_id, appt_type_name, appt_starts_at, appt_ends_at) VALUES (%s, %s, %s, %s, %s) RETURNING *;
                    """, 
                    (user_id, service_id, appt_type_name, appt_starts_at, appt_ends_at,)
                )
                return cursor.fetchone()
        except Exception as e:
            traceback.print_exc()
            raise e