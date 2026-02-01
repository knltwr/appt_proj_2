import pytest
import psycopg.errors
import datetime
from app.utils.util_funcs import get_formatted_datetime

# can run with "pytest -s" for print statements to show

# parametrize treats each set of inputs w/ the function as its own test, so reset_db will run between each input set
# can add tests for ensuring email unique, and that created_at and updated_at are in fact timestamps
# @pytest.mark.usefixtures("reset_db_class_level")
class TestUsers:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password", 
        [
            ("bruh@email.com", "password123"), # normal
        ])
    async def test_insert_user(self, test_db, email, password):
        
        user = await test_db.insert_user(email, password)
        assert int(user.get("user_id")) is not None
        assert user.get("email") == email
        assert user.get("password") == password
        assert user.get("created_at") is not None
        assert user.get("updated_at") is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, should_raise_exc", 
        [
            (None, "password123", True), # null email (empty string)
            ("bruh@email.com", None, True), # null password
        ])
    async def test_insert_user_constraints_notnull(self, test_db, email, password, should_raise_exc):
        
        if should_raise_exc:
            with pytest.raises(psycopg.errors.NotNullViolation):
                user = await test_db.insert_user(email, password)
        else:
            user = await test_db.insert_user(email, password)
            assert int(user.get("user_id")) is not None
            assert user.get("email") == email
            assert user.get("password") == password
            assert user.get("created_at") is not None
            assert user.get("updated_at") is not None
    
    @pytest.mark.asyncio
    async def test_insert_user_constraints_unique(self, test_db):
        
        test_data = [
            ("bruh@email.com", "password123", False), # normal
            ("bruh1@email.com", "password123", False), # normal
            ("bruh1@email.com", "password1234", True), # error
        ]
        
        for (email, password, should_raise_exc) in test_data:
            if should_raise_exc:
                with pytest.raises(psycopg.errors.UniqueViolation):
                    user = await test_db.insert_user(email, password)
            else:
                user = await test_db.insert_user(email, password)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password", 
        [
            ("bruh@email.com", "password123"),
        ])
    async def test_get_user_by_email(self, test_db, email, password):
        
        await test_db.insert_user(email, password)
        user = await test_db.get_user_by_email(email)
        user2 = await test_db.get_user_by_email(f"fake_{email}") # should be None

        assert user.get("email") == email
        assert user2 is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password", 
        [
            ("bruh@email.com", "password123"),
        ])
    async def test_get_user_by_user_id(self, test_db, email, password):
        
        inserted_user = await test_db.insert_user(email, password)
        user_id = int(inserted_user.get("user_id"))
        user = await test_db.get_user_by_user_id(user_id)
        user2 = await test_db.get_user_by_user_id(user_id + 999999999999) # should be None
        
        assert int(user.get("user_id")) == user_id
        assert user.get("email") == email
        assert user2 is None

class TestServices:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"),
        ])
    async def test_insert_service(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su):
        
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        
        assert int(inserted_service.get("service_id")) is not None
        assert int(inserted_service.get("host_id")) == host_id
        assert inserted_service.get("service_name") == service_name
        assert inserted_service.get("street_address") == street_address
        assert inserted_service.get("city") == city
        assert inserted_service.get("state") == state
        assert inserted_service.get("zip_code") == zip_code
        assert inserted_service.get("phone_number") == phone_number
        assert int(inserted_service.get("is_open_mo")) == is_open_mo
        assert inserted_service.get("open_time_mo") == open_time_mo
        assert inserted_service.get("close_time_mo") == close_time_mo
        assert int(inserted_service.get("is_open_tu")) == is_open_tu
        assert inserted_service.get("open_time_tu") == open_time_tu
        assert inserted_service.get("close_time_tu") == close_time_tu
        assert int(inserted_service.get("is_open_we")) == is_open_we
        assert inserted_service.get("open_time_we") == open_time_we
        assert inserted_service.get("close_time_we") == close_time_we
        assert int(inserted_service.get("is_open_th")) == is_open_th
        assert inserted_service.get("open_time_th") == open_time_th
        assert inserted_service.get("close_time_th") == close_time_th
        assert int(inserted_service.get("is_open_fr")) == is_open_fr
        assert inserted_service.get("open_time_fr") == open_time_fr
        assert inserted_service.get("close_time_fr") == close_time_fr
        assert int(inserted_service.get("is_open_sa")) == is_open_sa
        assert inserted_service.get("open_time_sa") == open_time_sa
        assert inserted_service.get("close_time_sa") == close_time_sa
        assert int(inserted_service.get("is_open_su")) == is_open_su
        assert inserted_service.get("open_time_su") == open_time_su
        assert inserted_service.get("close_time_su") == close_time_su
        assert inserted_service.get("created_at") is not None
        assert inserted_service.get("updated_at") is not None

    @pytest.mark.asyncio
    async def test_insert_service_constraints_notnull(self, test_db):
        
        email = "bruh@email.com"
        password = "password123"
        test_data = ["Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"]

        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        for i in range(len(test_data)):
            temp = test_data[i]
            test_data[i] = None
            with pytest.raises(psycopg.errors.NotNullViolation):
                inserted_service = await test_db.insert_service(host_id, *test_data)

    @pytest.mark.asyncio
    async def test_insert_service_constraints_unique(self, test_db):
        
        email1 = "bruh@email.com"
        password1 = "password123"
        email2 = "bruh2@email.com"
        password2 = "password1234"
        test_data1 = ["Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"]
        test_data2 = ["Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"]

        inserted_user1 = await test_db.insert_user(email1, password1)
        inserted_user2 = await test_db.insert_user(email2, password2)
        host_id1 = int(inserted_user1.get("user_id"))
        host_id2 = int(inserted_user2.get("user_id"))

        inserted_service1 = await test_db.insert_service(host_id1, *test_data1)
        with pytest.raises(psycopg.errors.UniqueViolation):
            inserted_service2 = await test_db.insert_service(host_id2, *test_data2)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"),
        ])
    async def test_insert_service_constraints_fkey(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su):
        
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
           inserted_service = await test_db.insert_service(host_id + 999999999, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59"),
        ])
    async def test_get_service_by_service_id(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su):
        
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))
        service = await test_db.get_service_by_service_id(service_id)
        service2 = await test_db.get_service_by_service_id(service_id + 999999999)
        
        assert service.get("phone_number") == phone_number
        assert service2 is None

class TestApptType:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "30 Min", 30),
        ])
    async def test_insert_appt_type(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes):
        
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))
        inserted_appt_type = await test_db.insert_appt_type(service_id, appt_type_name, appt_duration_minutes)

        assert int(inserted_appt_type.get("appt_type_id")) is not None
        assert int(inserted_appt_type.get("service_id")) == service_id
        assert inserted_appt_type.get("appt_type_name") == appt_type_name
        assert inserted_appt_type.get("appt_duration_minutes") == appt_duration_minutes
        assert inserted_appt_type.get("created_at") is not None
        assert inserted_appt_type.get("updated_at") is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "30 Min", 30),
        ])
    async def test_insert_appt_type_constraints_fkey(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes):
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            inserted_appt_type = await test_db.insert_appt_type(service_id + 999999999, appt_type_name, appt_duration_minutes)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "0 Min", 0),
        ])
    async def test_insert_appt_type_constraints_check(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes):
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))

        with pytest.raises(psycopg.errors.CheckViolation):
            inserted_appt_type = await test_db.insert_appt_type(service_id, appt_type_name, appt_duration_minutes)

    @pytest.mark.asyncio
    async def test_insert_appt_type_constraints_unique(self, test_db):

        email1 = "bruh@email.com"
        password1 = "password123"
        email2 = "bruh2@email.com"
        password2 = "password1234"
        test_data1 = ["Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"]
        test_data2 = ["Kunal Biz2", "48 Brick Lnz", "NYC", "NY", "11368", "17187777778", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59"]
        test_data1_appt_type1 = ["30 Min", 30]
        test_data1_appt_type2 = ["30 Min", 30]
        test_data2_appt_type1 = ["30 Min", 30]
        
        inserted_user1 = await test_db.insert_user(email1, password1)
        host_id1 = int(inserted_user1.get("user_id"))

        inserted_user2 = await test_db.insert_user(email2, password2)
        host_id2 = int(inserted_user2.get("user_id"))

        inserted_service1 = await test_db.insert_service(host_id1, *test_data1)
        service_id1 = int(inserted_service1.get("service_id"))

        inserted_service2 = await test_db.insert_service(host_id2, *test_data2)
        service_id2 = int(inserted_service2.get("service_id"))

        inserted_appt_type1 = await test_db.insert_appt_type(service_id1, *test_data1_appt_type1)
        inserted_appt_type2 = await test_db.insert_appt_type(service_id2, *test_data2_appt_type1)

        with pytest.raises(psycopg.errors.UniqueViolation):
            inserted_appt_type_err = await test_db.insert_appt_type(service_id1, *test_data2_appt_type1)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "30 Min", 30),
        ])
    async def test_get_appt_type_by_service_id_and_appt_type_name(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes):
        
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))
        inserted_appt_type = await test_db.insert_appt_type(service_id, appt_type_name, appt_duration_minutes)

        appt_type = await test_db.get_appt_type_by_service_id_and_appt_type_name(service_id, appt_type_name)
                                                                                
        assert appt_type.get("appt_type_name") == appt_type_name
        assert appt_type.get("appt_duration_minutes") == appt_duration_minutes

class TestAppt:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes, appt_starts_at", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "30 Min", 30, "2024-11-25 01:00:00"),
        ])
    async def test_insert_appt(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes, appt_starts_at):
        
        inserted_user = await test_db.insert_user(email, password)
        inserted_user2 = await test_db.insert_user(f"ay{email}", password)
        host_id = int(inserted_user.get("user_id"))
        booker_id = int(inserted_user2.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))
        inserted_appt_type = await test_db.insert_appt_type(service_id, appt_type_name, appt_duration_minutes)

        appt_ends_at = str(get_formatted_datetime(appt_starts_at) + datetime.timedelta(minutes = int(appt_duration_minutes)))
        inserted_appt = await test_db.insert_appt(booker_id, service_id, appt_type_name, appt_starts_at, appt_ends_at)
                                                                                
        assert int(inserted_appt.get("appt_id")) is not None
        assert int(inserted_appt.get("user_id")) == booker_id
        assert int(inserted_appt.get("service_id")) == service_id
        assert inserted_appt.get("appt_type_name") == appt_type_name
        assert inserted_appt.get("appt_starts_at") == appt_starts_at
        assert inserted_appt.get("appt_ends_at") == appt_ends_at
        assert inserted_appt_type.get("created_at") is not None
        assert inserted_appt_type.get("updated_at") is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes, appt_starts_at", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "30 Min", 30, "2024-11-25 01:00:00"),
        ])
    async def test_insert_appt_constraints_fkey(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes, appt_starts_at):
        
        inserted_user = await test_db.insert_user(email, password)
        inserted_user2 = await test_db.insert_user(f"ay{email}", password)
        host_id = int(inserted_user.get("user_id"))
        booker_id = int(inserted_user2.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))
        inserted_appt_type = await test_db.insert_appt_type(service_id, appt_type_name, appt_duration_minutes)

        appt_ends_at = str(get_formatted_datetime(appt_starts_at) + datetime.timedelta(minutes = int(appt_duration_minutes)))
        
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            await test_db.insert_appt(booker_id + 999999999, service_id, appt_type_name, appt_starts_at, appt_ends_at)
        
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            await test_db.insert_appt(booker_id, service_id + 999999999, appt_type_name, appt_starts_at, appt_ends_at)

        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            await test_db.insert_appt(booker_id, service_id, f"{appt_type_name}_fake", appt_starts_at, appt_ends_at)

    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes, appt_starts_at", 
        [
            ("bruh@email.com", "password123", "Kunal Biz", "47 Brick Lnz", "NYC", "NY", "11368", "17187777777", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 1, "00:00:00", "23:59:59", 0, "00:00:00", "23:59:59", "30 Min", 30, "2024-11-25 01:00:00"),
        ])
    async def test_get_conflicting_appt(self, test_db, email, password, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su, appt_type_name, appt_duration_minutes, appt_starts_at):
        
        inserted_user = await test_db.insert_user(email, password)
        host_id = int(inserted_user.get("user_id"))

        inserted_service = await test_db.insert_service(host_id, service_name, street_address, city, state, zip_code, phone_number, is_open_mo, open_time_mo, close_time_mo, is_open_tu, open_time_tu, close_time_tu, is_open_we, open_time_we, close_time_we, is_open_th, open_time_th, close_time_th, is_open_fr, open_time_fr, close_time_fr, is_open_sa, open_time_sa, close_time_sa, is_open_su, open_time_su, close_time_su)
        service_id = int(inserted_service.get("service_id"))
        inserted_appt_type = await test_db.insert_appt_type(service_id, appt_type_name, appt_duration_minutes)

        appt_ends_at = str(get_formatted_datetime(appt_starts_at) + datetime.timedelta(minutes = int(appt_duration_minutes)))
        inserted_appt = await test_db.insert_appt(host_id, service_id, appt_type_name, appt_starts_at, appt_ends_at)
        appt_id = int(inserted_appt.get("appt_id"))

        appt_starts_at_1 = str(get_formatted_datetime(appt_ends_at) + datetime.timedelta(minutes = -1)) # 1 minute before 1st appt end should work in any case
        appt_ends_at_1 = str(get_formatted_datetime(appt_starts_at_1) + datetime.timedelta(minutes = int(appt_duration_minutes)))

        appt_starts_at_2 = appt_ends_at
        appt_ends_at_2 = str(get_formatted_datetime(appt_starts_at_2) + datetime.timedelta(minutes = int(appt_duration_minutes)))


        conflict_1 = await test_db.get_conflicting_appt(service_id, appt_type_name, appt_starts_at_1, appt_ends_at_1)
        conflict_2 = await test_db.get_conflicting_appt(service_id, appt_type_name, appt_starts_at_2, appt_ends_at_2)
                                                                            
        assert int(conflict_1.get("appt_id")) == appt_id
        assert conflict_2 is None
