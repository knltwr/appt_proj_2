import psycopg
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
import re
import traceback
from app.config import CONFIG
from app.utils.other_funcs import singleton

@singleton
class Database:

    pool = None
    dbname = None
    
    def __init__(self, 
                 dbname: str = CONFIG.DATABASE_NAME, 
                 user: str = CONFIG.DATABASE_USERNAME, 
                 password: str = CONFIG.DATABASE_PASSWORD, 
                 host: str = CONFIG.DATABASE_HOSTNAME, 
                 port: int = CONFIG.DATABASE_PORT, 
                 row_factory: object = dict_row
                 ):
        try:
            self.pool = AsyncConnectionPool(
                                        min_size = 5,
                                        max_size = 10,
                                        open = True,
                                        dbname = dbname, 
                                        user = user, 
                                        password = password, 
                                        host = host, 
                                        port = port, 
                                        row_factory = row_factory
                                        )
            self.dbname = dbname
        except psycopg.OperationalError as e:            
            if re.search(r"database.*does not exist", e.args[0]): # regex ".*" matches any characters
                print(f'{dbname} does not exist; see db init file')    
            traceback.print_exc()
            raise e
        
    async def insert_user(self,
                    email: str, 
                    password: str
                    ) -> dict:
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            INSERT INTO users(email, password) VALUES (%s, %s) RETURNING *;
                        """,
                        (email, password,)
                    )
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
        
    async def get_user_by_email(self,
                          email: str
                          ) -> dict: # add in annotation for user model as return type? causes issue though if None returned from query
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            SELECT * FROM users WHERE email=%s;
                        """,
                        (email, )
                    )
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e

    async def get_user_by_user_id(self,
                          user_id: int
                          ) -> dict: # add in annotation for user model as return type? causes issue though if None returned from query
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            SELECT * FROM users WHERE user_id=%s;
                        """,
                        (user_id, )
                    )
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
    
    async def insert_service(self, 
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
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
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
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
        
    async def get_services_by_host_id(self,
                                host_id: int):
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            SELECT * FROM services WHERE host_id=%s;
                        """,
                        (host_id, )
                    )
                    res = await cursor.fetchall()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
    
    async def get_service_by_service_id(self,
                                service_id: int):
        try:
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            SELECT * FROM services WHERE service_id=%s;
                        """,
                        (service_id, )
                    )
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
        
    async def insert_appt_type(self,
                    service_id: int, 
                    appt_type_name: str, 
                    appt_duration_minutes: int
                    ):
        try:
            # for some reason, could not use self.conn here b/c it would be closed when creating cursor, so created a new connection for just this function
            # with psycopg.connect(dbname = self.dbname, 
            #                        user = CONFIG.DATABASE_USERNAME, 
            #                        password = CONFIG.DATABASE_PASSWORD, 
            #                        host = CONFIG.DATABASE_HOSTNAME, 
            #                        port = CONFIG.DATABASE_PORT, 
            #                        row_factory = dict_row
            #                        ) as conn:
            #     cursor = conn.cursor()
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            INSERT INTO appt_types (service_id, appt_type_name, appt_duration_minutes) VALUES (%s, %s, %s) RETURNING *;
                        """, 
                        (service_id, appt_type_name, appt_duration_minutes)
                    )
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
    
    async def get_appt_type_by_service_id_and_appt_type_name(self, 
                                                       service_id: int,
                                                       appt_type_name: str):
        try:
            # for some reason, could not use self.conn here b/c it would be closed when creating cursor, so created a new connection for just this function
            # with psycopg.connect(dbname = self.dbname, 
            #                        user = CONFIG.DATABASE_USERNAME, 
            #                        password = CONFIG.DATABASE_PASSWORD, 
            #                        host = CONFIG.DATABASE_HOSTNAME, 
            #                        port = CONFIG.DATABASE_PORT, 
            #                        row_factory = dict_row
            #                        ) as conn:
            #     cursor = conn.cursor()
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            SELECT * FROM appt_types WHERE service_id=%s AND appt_type_name=%s;
                        """,
                        (service_id, appt_type_name, )
                    )
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
        
    async def get_conflicting_appt(self, 
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
            # with psycopg.connect(dbname = self.dbname, 
            #                        user = CONFIG.DATABASE_USERNAME, 
            #                        password = CONFIG.DATABASE_PASSWORD, 
            #                        host = CONFIG.DATABASE_HOSTNAME, 
            #                        port = CONFIG.DATABASE_PORT, 
            #                        row_factory = dict_row
            #                        ) as conn:
            #     cursor = conn.cursor()
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
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
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e
    
    async def insert_appt(self,
                    user_id: int,
                    service_id: int,
                    appt_type_name: str,
                    appt_starts_at: str,
                    appt_ends_at: str
                    ):
        try:
            # for some reason, could not use self.conn here b/c it would be closed when creating cursor, so created a new connection for just this function
            # with psycopg.connect(dbname = self.dbname, 
            #                        user = CONFIG.DATABASE_USERNAME, 
            #                        password = CONFIG.DATABASE_PASSWORD, 
            #                        host = CONFIG.DATABASE_HOSTNAME, 
            #                        port = CONFIG.DATABASE_PORT, 
            #                        row_factory = dict_row
            #                        ) as conn:
            #     cursor = conn.cursor()
            async with self.pool.connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        """
                            INSERT INTO appts (user_id, service_id, appt_type_name, appt_starts_at, appt_ends_at) VALUES (%s, %s, %s, %s, %s) RETURNING *;
                        """, 
                        (user_id, service_id, appt_type_name, appt_starts_at, appt_ends_at,)
                    )
                    res = await cursor.fetchone()
                    return res
        except Exception as e:
            traceback.print_exc()
            raise e