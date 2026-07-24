import argparse
import os
import sys
import bcrypt

from nxcore.middleware.logging_manager import logger
from api.model.dmz_model import DMZServiceDao, PortMappingDao
from api.model.policy_model import PolicyClientDao, PolicyDao
from api.model.user_model import UserDao, UserPolicyDao
from api.model.vpn_model import VPNSessionDao
from api.model.server_config_model import ServerConfigDao

import config


def create_db():
    if not os.path.exists(config.DB_PATH):
        os.makedirs(config.DB_PATH, exist_ok=True)
    UserDao().create_schema()
    PolicyDao().create_schema()
    DMZServiceDao().create_schema()
    PolicyClientDao().create_schema()
    UserPolicyDao().create_schema()
    PortMappingDao().create_schema()
    VPNSessionDao().create_schema()
    ServerConfigDao().create_schema()
    logger.info("Database schema created successfully.")


def reset_admin(usr: str, pw: str):
    dao = UserDao()
    try:
        user = dao.find_by_username(usr)
        if user is None:
            logger.error(f"User with username '{usr}' not found.")
            return

        hashed_pw = bcrypt.hashpw(pw.encode("utf8"), bcrypt.gensalt())
        dao.update_by_id(
            user["id"], {"role": "superuser", "password": hashed_pw.decode("utf-8")}
        )
        dao.commit()
        logger.info(f"Password for user '{usr}' successfully updated.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        dao.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Access Server Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("create_db", help="Initialize and create database schema")

    reset_parser = subparsers.add_parser(
        "reset_admin", help="Reset password for an admin user"
    )
    reset_parser.add_argument("username", type=str, help="Username of the admin user")
    reset_parser.add_argument(
        "new_password", type=str, help="New password for the admin user"
    )

    args = parser.parse_args()

    if args.command == "create_db":
        create_db()
    elif args.command == "reset_admin":
        reset_admin(args.username, args.new_password)
    else:
        parser.print_help()
        sys.exit(1)
