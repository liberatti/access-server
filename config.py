import os
import multiprocessing
SECURITY_ENABLED = True
KEY_SIZE = 2048
DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"
JWT_EXPIRATION_DELTA = 1800
main_path = os.path.dirname(os.path.abspath(__file__))
ADMIN_ROLE = ["viewer", "superuser"]

workers = multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:5000'
reload = False
daemon = True
timeout = 30
preload_app = True
threads = 4
accesslog = 'logs/gunicorn.log'
pidfile = 'gunicorn.pid'
errorlog = 'logs/gunicorn.log'