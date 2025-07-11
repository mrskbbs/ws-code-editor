from dotenv import load_dotenv
from logging import INFO as logging_INFO
import os

load_dotenv()

SALT = os.getenv("SALT", "default_sault_value")

DB_URL = os.getenv("DB_URL", "postgresql://username:password@localhost:5432/code_editor")

CONTAINER_NAME = os.getenv("CONTAINER_NAME", "container_python")
CONTAINER_USER = os.getenv("CONTAINER_USER", "container_user")
CONTAINER_WORKDIR = f"/home/{CONTAINER_USER}/"

FRONTEND_DOMAIN_NAME = "localhost:3000"
FRONTEND_URL = f"http://{FRONTEND_DOMAIN_NAME}" 

BACKEND_DOMAIN_NAME = os.getenv("BACKEND_DOMAIN_NAME", "localhost")
BACKEND_PORT = 5000
BACKEND_URL = f"http://{BACKEND_DOMAIN_NAME}:{BACKEND_PORT}"

FLASK_SECERT_KEY = os.getenv("FLASK_SECERT_KEY", "REPLACEME")

SAVE_LOGS = False
LOG_PATH = "./app.log"
LOG_LEVEL = logging_INFO