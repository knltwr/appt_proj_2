import bcrypt
from typing import Any
import json


def get_hashed_salted_password(password: str) -> str:
    password_salt = bcrypt.gensalt(rounds = 5) # TODO: config the rounds?
    password_hashed_salted = bcrypt.hashpw(password.encode("utf-8"), password_salt).decode("utf-8") #hashlib.sha256(bytes(password)).hexdigest()
    return password_hashed_salted

def generate_response(success: bool, data: Any):
    return json.dumps({"success": success, "data": data})