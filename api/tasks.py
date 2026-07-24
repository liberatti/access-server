import bcrypt
from datetime import timedelta

from nxcore.middleware.logging_manager import logger
from api.tools.vpn_tool import VPNTool
from api.model.user_model import UserDao

import config


INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
}


def install_task():
    """
    Performs initial setup tasks, including creating the database schema,
    initializing feeds and other repositories.
    """
    from cli import create_db

    create_db()

    default_config = {
        "name": "vpnserver",
        "network": "10.8.0.0",
        "netmask": "255.255.255.0",
        "port": 1194,
        "protocol": "udp",
    }
    with UserDao() as user_model:
        hashed = bcrypt.hashpw(config.ADMIN_PASS.encode("utf8"), bcrypt.gensalt())
        pk = user_model.persist(
            {
                "name": "admin",
                "username": "admin",
                "password": hashed.decode("utf-8"),
                "role": "superuser",
            }
        )
        default_config.update({"admin_pk": pk})
        logger.info(f"Admin user created with ID {pk}")
        VPNTool.initialize(default_config)


def update_task(override_existing=False):
    """
    Updates all feeds that are due for an update based on their intervals.

    Args:
        override_existing (bool): If True, updates all feeds regardless of their update interval.
    """
    pass
