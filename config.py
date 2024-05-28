import os
SECURITY_ENABLED = True
KEY_SIZE = 2048
DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
JWT_EXPIRATION_DELTA = 1800
main_path = os.path.dirname(os.path.abspath(__file__))