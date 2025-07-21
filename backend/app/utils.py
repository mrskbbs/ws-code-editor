from datetime import datetime
from functools import wraps
import logging
import coloredlogs
from flask import Request, session, g
from hashlib import sha256

from sqlalchemy import and_
from app.config import LOG_LEVEL, LOG_PATH, SALT, SAVE_LOGS

if SAVE_LOGS:
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL)

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

def sha256salt(s: str) -> str:
    return sha256(
        (s + SALT).encode()
    ).hexdigest()

def unwrapForWhereClasue(model, d: dict):
    return and_(getattr(model, k) == v for k,v in d.items())

def injectUser(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs["user"] = session.get("user")
        return f(*args, **kwargs)
    return wrapper