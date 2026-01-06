import pytest
import psycopg.errors

# parametrize treats each set of inputs w/ the function as its own test, so reset_db will run between each input set
# can add tests for ensuring email unique, and that created_at and updated_at are in fact timestamps
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, password, should_raise_exc", 
    [
        ("bruh@email.com", "password123", False), # normal
        (None, "password123", True), # null email (empty string)
        ("bruh@email.com", None, True),
          # null password
    ])
async def test_insert_user(test_db, email, password, should_raise_exc):
    
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
@pytest.mark.parametrize(
    "email, password", 
    [
        ("bruh@email.com", "password123"),
    ])
async def test_get_user_by_email(test_db, email, password):
    
    await test_db.insert_user(email, password)
    user = await test_db.get_user_by_email(email)

    assert user.get("email") == email

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, password", 
    [
        ("bruh@email.com", "password123"),
    ])
async def test_get_user_by_user_id(test_db, email, password):
    
    inserted_user = await test_db.insert_user(email, password)
    user = await test_db.get_user_by_user_id(int(inserted_user.get("user_id")))
    
    assert user.get("email") == email

# can run with "pytest -s" for print statements to show