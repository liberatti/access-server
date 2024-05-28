import os
import logging
import inspect
import random
import string
from functools import wraps
import sys
import threading
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify
from flask_marshmallow import Marshmallow
from config import SECURITY_ENABLED

ma = Marshmallow()


def gen_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def handle_sigterm(signum, frame):
    threads_ativos = threading.enumerate()
    for thread in threads_ativos:
        thread.active = False
    sys.exit(0)


def chmod_r(path, mode, recursive=False):
    if recursive:
        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                os.chmod(os.path.join(root, dirname), mode)
            for filename in files:
                os.chmod(os.path.join(root, filename), mode)
    os.chmod(path, mode)


def has_any_authority(_authorities):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not SECURITY_ENABLED:
                return fn(*args, **kwargs)
            verify_jwt_in_request()
            jwt_content = get_jwt()
            if jwt_content["role"] in _authorities:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper


class CustomLogger(logging.Logger):
    def info(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        caller_method = frame.f_code.co_name
        filename = os.path.basename(frame.f_globals.get("__file__", ""))
        lineno = frame.f_lineno
        super().info(f"[{filename}][{caller_method}][{lineno}] {msg}", *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        caller_method = frame.f_code.co_name
        filename = os.path.basename(frame.f_globals.get("__file__", ""))
        lineno = frame.f_lineno
        super().error(f"[{filename}][{caller_method}][{lineno}] {msg}", *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        frame = inspect.currentframe().f_back
        caller_method = frame.f_code.co_name
        filename = os.path.basename(frame.f_globals.get("__file__", ""))
        lineno = frame.f_lineno
        super().warn(f"[{filename}][{caller_method}][{lineno}] {msg}", *args, **kwargs)


logger = CustomLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - :name - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
