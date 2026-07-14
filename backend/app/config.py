import os
from dotenv import load_dotenv

load_dotenv(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "..", 
        ".env"
    )
)

DB_URL = str(os.environ.get("DB_URL"))
TESTS_DB_URL = str(os.environ.get("TESTS_DB_URL"))
JWT_KEY = str(os.environ.get("JWT_KEY"))
JWT_ALGO = str(os.environ.get("JWT_ALGO")) # must be a symmetric algo 
SALT = str(os.environ.get("SALT"))
ORIGIN_REGEX = r"(http[s]{0,1})\:\/\/localhost\:[0-9]{0,5}"
SANDBOX_URL = "http://dockerproxy:1337"
CODE_TIMEOUT = 5.0
