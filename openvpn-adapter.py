#!/usr/bin/python3.12
import os
import sys
import bcrypt
from api.model.user_model import UserDao
from api.model.vpn_model import VPNSessionDao
from nxcore.middleware.logging_manager import LoggingManager, logger

LoggingManager(loglevel="DEBUG")


def print_env():
    for var, value in os.environ.items():
        logger.info(f"{var} = {value}")


def auth_user(username, password):
    with UserDao() as model:
        user = model.find_by_username(username)
        stored_pw = (
            user["password"].encode("utf-8")
            if isinstance(user.get("password"), str)
            else user.get("password")
        )
        if user and stored_pw and bcrypt.checkpw(password, stored_pw):
            logger.info(f"auth success for user {username}")
            return True
    logger.warning(f"auth failed for user {username}")
    return False


def connect(user_id, remote_port, remote_ip, local_ip):
    with VPNSessionDao() as model:
        session = {
            "user_id": user_id,
            "remote_port": int(remote_port) if remote_port else None,
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


try:
    action = os.environ.get("script_type") or ""
    if "user-pass-verify" in action and len(sys.argv) > 1:
        with open(sys.argv[1], "r") as tmpFile:
            lines = tmpFile.readlines()
            if len(lines) >= 2:
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
        disconnect(os.environ.get("common_name"))
except Exception as err:
    logger.error(f"Error executing {action}: {err}")

logger.error(f"{action} failed")
sys.exit(1)
