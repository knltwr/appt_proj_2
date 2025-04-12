### MOST OF THIS MODULE IS FROM FASTAPI DOC
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import timedelta, datetime, timezone
from app.schemas import oauth2 as schemas_oauth2
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config import CONFIG

# TODO: change secret key when moving to env vars
SECRET_KEY = CONFIG.OAUTH2_SECRET_KEY # openssl rand -hex 32
ALGORITHM = CONFIG.OAUTH2_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = CONFIG.OAUTH2_ACCESS_TOKEN_LIFE_MINUTES
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login") # this parameter route where the user logins to receive a token

def create_access_token(data: dict) -> schemas_oauth2.Token:
    to_encode = data.copy()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES) # need UTC here
    if "expires_at" in to_encode:
        raise Exception("Could not generate token due to \"exp\" field in data")
    to_encode["expires_at"] = str(expires_at)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return schemas_oauth2.Token(access_token=encoded_jwt, token_type = "Bearer")

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM]) # function excepts a sequence of ALGORITHMs
        user_id = int(payload.get("user_id"))
        if user_id is None:
            raise credentials_exception
        token_data = schemas_oauth2.TokenPayload(user_id = user_id)
        return token_data
    except InvalidTokenError:
        raise credentials_exception
    
def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(token, credentials_exception) # this can raise error ... let it pass through