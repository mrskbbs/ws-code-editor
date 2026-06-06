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

