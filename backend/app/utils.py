from datetime import datetime
from flask import Request
from hashlib import sha256
from app.config import SALT


def createUserToken(request: Request) -> str:
    return sha256(
        request.user_agent.__str__().encode() + 
        datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f").encode() +
        request.remote_addr.encode() + 
        SALT.encode()
    ).hexdigest()