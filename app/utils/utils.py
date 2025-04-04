import bcrypt
from typing import Any
import json


def get_hashed_salted_password(password: str) -> str:
    password_salt = bcrypt.gensalt(rounds = 5) # TODO: config the rounds?
    password_hashed_salted = bcrypt.hashpw(password.encode("utf-8"), password_salt).decode("utf-8") #hashlib.sha256(bytes(password)).hexdigest()
    return password_hashed_salted

def is_correct_password(entered_password: str , correct_password: str) -> bool:
    """
    Utility function that returns bool indicating verification of entered_password against correct_password (the latter of which is already hashed and salted)

    :param str entered_password: the password provided (e.g. in the request)
    :param str correct_password: the correct password (e.g. stored in the database hashed and salted)
    :return: boolean indicating success or failure
    :rtype: bool
    """
    return bcrypt.checkpw(entered_password.encode("utf-8"), correct_password.encode("utf-8")) # bcrypt captures salt in hashed_salted version, so dont need to store salt

def generate_response(success: bool, data: Any):
    return json.dumps({"success": success, "data": data})