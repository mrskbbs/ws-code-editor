from datetime import datetime
import logging
import coloredlogs
from flask import Request
from hashlib import sha256
from app.config import LOG_LEVEL, LOG_PATH, SALT, SAVE_LOGS

if SAVE_LOGS:
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL)

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

def createUserToken(request: Request) -> str:
    return sha256(
        request.user_agent.__str__().encode() + 
        datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f").encode() +
        request.remote_addr.encode() + 
        SALT.encode()
    ).hexdigest()