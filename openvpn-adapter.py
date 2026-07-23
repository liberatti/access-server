#!/usr/bin/python3
import os
import sys
import bcrypt
from api.model.user_model import UserDao
from api.model.vpn_model import VPNSessionDao
from nxcore.middleware.logging_manager import LoggingManager

logger = LoggingManager(loglevel="DEBUG").get_current_instance()


def print_env():
    for var, value in os.environ.items():
        logger.info(f"{var} = {value}")


def auth_user(username, password):
    with UserDao() as model:
        user = model.find_by_username(username)
        if (
            user
            and user.get("password")
            and bcrypt.checkpw(password, user["password"].encode("utf8"))
        ):
            logger.info(f"auth success for user {username}")
            return True
    logger.warning(f"auth failed for user {username}")
    return False


def connect(user_id, remote_port, remote_ip, local_ip):
    with VPNSessionDao() as model:
        session = {
            "user_id": user_id,
            "remote_port": remote_port,
            "remote_ip": remote_ip,
            "local_ip": local_ip,
            "state": "pending",
        }
        model.persist(session)
    sys.exit(0)


def disconnect(user_id):
    with VPNSessionDao() as model:
        sessions = model.get_all_by_user_id(user_id)
        for s in sessions:
            model.update_by_id(s["id"], {"state": "disconnect"})
    sys.exit(0)


action = os.environ.get("script_type")
if "user-pass-verify" in action:
    tmpFile = open(sys.argv[1], "r")
    lines = tmpFile.readlines()
    input_user = lines[0].strip()
    input_pass = lines[1].strip().encode("utf-8")
    if auth_user(input_user, input_pass):
        sys.exit(0)

if "client-connect" in action:
    connect(
        os.environ.get("common_name"),
        os.environ.get("trusted_port"),
        os.environ.get("trusted_ip"),
        os.environ.get("ifconfig_pool_remote_ip"),
    )

if "client-disconnect" in action:
    """
    time_duration = 9
    bytes_sent = 3214
    bytes_received = 6807
    """
    disconnect(os.environ.get("common_name"))

logger.error(f"{action} failed")
sys.exit(1)
