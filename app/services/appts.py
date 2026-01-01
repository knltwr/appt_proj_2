from fastapi import status, Depends, HTTPException
from app.database.db import Database
import psycopg
from app.schemas import appts as schemas_appts
import datetime
from app.core.config import CONFIG
from app.utils.util_funcs import get_formatted_time
from types import MappingProxyType

IS_OPEN_WEEKDAY_MAPPING = MappingProxyType({1: "is_open_mo", 2: "is_open_tu", 3: "is_open_we", 4: "is_open_th", 5: "is_open_fr", 6: "is_open_sa", 7: "is_open_su"})
OPEN_TIME_WEEKDAY_MAPPING = MappingProxyType({1: "open_time_mo", 2: "open_time_tu", 3: "open_time_we", 4: "open_time_th", 5: "open_time_fr", 6: "open_time_sa", 7: "open_time_su"})
CLOSE_TIME_WEEKDAY_MAPPING = MappingProxyType({1: "close_time_mo", 2: "close_time_tu", 3: "close_time_we", 4: "close_time_th", 5: "close_time_fr", 6: "close_time_sa", 7: "close_time_su"})

async def service_appt_create(appt: schemas_appts.ApptCreateRequest, db: Database, user_id: int):
    appt_dict = appt.model_dump()

    try:
        service_from_db = await db.get_service_by_service_id(appt_dict["service_id"])
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if service_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Service not found")
    
    try:
        appt_type_from_db = await db.get_appt_type_by_service_id_and_appt_type_name(appt_dict["service_id"], appt_dict["appt_type_name"])
    except psycopg.Error as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"Database issue occurred: {e}")
    
    if appt_type_from_db is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Appt type not found")
    
    appt_duration_minutes = appt_type_from_db["appt_duration_minutes"]
    appt_starts_at = appt_dict["appt_starts_at"]
    appt_ends_at = appt_starts_at + datetime.timedelta(minutes = int(appt_duration_minutes))


    # start day
    date_in_check = appt_starts_at.date()
    weekday_in_check = date_in_check.isoweekday()
    if (
        not ( service_from_db[IS_OPEN_WEEKDAY_MAPPING[weekday_in_check]] ) # on a day that service is not open
        or ( appt_starts_at.time() < get_formatted_time(service_from_db[OPEN_TIME_WEEKDAY_MAPPING[weekday_in_check]]) )  # starts before service opens
        or ( appt_starts_at.time() > get_formatted_time(service_from_db[CLOSE_TIME_WEEKDAY_MAPPING[weekday_in_check]]) ) # starts after service closes
    ):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Could not create appointment due to invalid appointment time")
    
    # THE BELOW LOGIC CAN BE MADE MORE EFFICIENT (O(1) by checking only the distinct weekdays in range, i.e. at most 7 days, rather than the entire range from start to end, which could be >> 7 days)
    # IF THE "HOLIDAY" FEATURE GETS ADDED, THAT CAN BE CHECKED THROUGH A QUERY FOR THE RELEVANT TIME RANGE (SIMILAR TO CONFLICT CHECK)
    # inbetween days (i.e. appt stretches across entire day, e.g. hotel booking)
    if appt_starts_at.date() != appt_ends_at.date():
        date_in_check += datetime.timedelta(days = 1)
        while date_in_check < appt_ends_at.date():
            weekday_in_check = date_in_check.isoweekday()
            if (
                not (service_from_db.get(IS_OPEN_WEEKDAY_MAPPING[weekday_in_check])) # on a day that service is not open
                or (str(get_formatted_time(service_from_db[OPEN_TIME_WEEKDAY_MAPPING[weekday_in_check]])) != CONFIG.SERVICE_MIN_TIME) # 00:00:00 # since appt does not end this day, service must be open whole day
                or (str(get_formatted_time(service_from_db[CLOSE_TIME_WEEKDAY_MAPPING[weekday_in_check]])) != CONFIG.SERVICE_MAX_TIME) # 23:59:59 # since appt does not end this day, service must be open whole day
            ):
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Could not create appointment due to invalid appointment time")
            date_in_check += datetime.timedelta(days = 1)
            
    # last day
    weekday_in_check = date_in_check.isoweekday()
    if (
        not ( service_from_db.get(IS_OPEN_WEEKDAY_MAPPING[weekday_in_check]) ) # on a day that service is not open
        or ( appt_ends_at.time() < get_formatted_time(service_from_db[OPEN_TIME_WEEKDAY_MAPPING[weekday_in_check]]) ) # ends before service opens
        or ( appt_ends_at.time() > get_formatted_time(service_from_db[CLOSE_TIME_WEEKDAY_MAPPING[weekday_in_check]]) ) # ends after service closes
    ):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Could not create appointment due to invalid appointment time")

    # NEED TO CHECK IN DB FOR CONFLICT WITH ANY EXISTING APPOINTMENT
    appt_conflict_check = await db.get_conflicting_appt(appt_dict["service_id"], appt_dict["appt_type_name"], str(appt_starts_at), str(appt_ends_at))
    if appt_conflict_check is not None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Could not create appointment due to service having conflict at the time")
        
    created_appt = await db.insert_appt(user_id, appt_dict["service_id"], appt_dict["appt_type_name"], appt_starts_at, appt_ends_at)
    
    return created_appt