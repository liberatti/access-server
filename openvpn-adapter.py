#!/usr/bin/python3
import os
import sys
import bcrypt
from api.utils import logger
from api.model.user_model import UserDao
from api.model.vpn_model import VPNSessionDao


def print_env():
    for var, value in os.environ.items():
        logger.info(f"{var} = {value}")


def auth_user(username, password):
    model = UserDao()
    user = model.find_by_username(username)
    if bcrypt.checkpw(password, user["password"].encode("utf8")):
        logger.info("auth success! ")
        return True
    return False


def connect(user_id, remote_port, remote_ip, local_ip):
    model = VPNSessionDao()
    session = {
        "user_id": user_id,
        "remote_port": remote_port,
        "remote_ip": remote_ip,
        "local_ip": local_ip,
        "state": "pending",
    }
    model.persist(session)
    model.commit()
    model.close()
    sys.exit(0)


def disconnect(user_id):
    model = VPNSessionDao()
    sessions = model.get_all_by_user_id(user_id)
    for s in sessions:
        model.update_by_id(s["id"], {"state": "disconnect"})
    model.commit()
    model.close()
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
