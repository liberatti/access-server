import json
import os
import traceback
from datetime import timedelta, datetime

from nxcore.middleware.logging_manager import logger

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

    from api.tools.vpn_tool import VPNTool
    if not VPNTool.is_initialized():
        default_config = {
            "name": "vpnserver",
            "admin_user": "admin",
            "admin_pass": "admin",
            "network": "10.8.0.0",
            "netmask": "255.255.255.0",
            "port": 1194,
            "protocol": "udp"
        }
        VPNTool.initialize(default_config)


def update_task(override_existing=False):
    """
    Updates all feeds that are due for an update based on their intervals.

    Args:
        override_existing (bool): If True, updates all feeds regardless of their update interval.
    """
    pass
