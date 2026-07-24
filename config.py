import os
import secrets

SECURITY_ENABLED = os.environ.get("SECURITY_ENABLED", "true") == "true"
KEY_SIZE = 2048
DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
JWT_EXPIRATION_DELTA = 1800
main_path = os.path.dirname(os.path.abspath(__file__))
ADMIN_ROLE = ["viewer", "superuser"]
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin")
BASE_BATH = "/opt/access-server"

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_EXPIRE = 1800
JWT_AUD = "as"
API_KEY = os.environ.get("API_KEY", "dev_api_key")
DB_PATH = os.environ.get("DB_PATH", "data")
WORKERS = int(os.environ.get("WORKERS", 1))
THREADS = int(os.environ.get("THREADS", 1))
