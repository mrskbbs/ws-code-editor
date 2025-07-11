from contextlib import contextmanager
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_URL


engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    bind=engine,
    # autoflush=False, TODO: change if needed
    # autocommit = False
)

@contextmanager
def getDb():
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        

def injectDb(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with getDb() as db:
            kwargs["db"] = db
            return f(*args, **kwargs)
    return wrapper