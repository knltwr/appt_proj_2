import pytest
import psycopg.errors

# parametrize treats each set of inputs w/ the function as its own test, so reset_db will run between each input set
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, password, should_raise_exc", 
    [
        ("bruh@email.com", "password123", False), # normal
        ("", "password123", True), # null email (empty string)
        ("bruh@email.com", "", True),
          # null password
    ])
async def test_insert_user(test_db, email, password, should_raise_exc):
    
    if should_raise_exc:
        with pytest.raises(psycopg.errors.NotNullViolation):
            user = await test_db.insert_user(email, password)
    else:
        user = await test_db.insert_user(email, password)
        # assert isinstance(user.id, int)
        assert user.get("email") == email
        assert user.get("password") == password