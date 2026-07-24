import bcrypt
import subprocess
from datetime import timedelta
from jinja2 import Template
from nxcore.middleware.logging_manager import logger
from api.tools.vpn_tool import VPNTool
from api.model.user_model import UserDao
from api.model.vpn_model import VPNSessionDao
from api.model.policy_model import PolicyClientDao
from api.tools.firewall_tool import FirewallTool
from api.utils import get_template_path
import config


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
        "public_address": "127.0.0.1",
        "public_port": 1194,
        "auth": "SHA512",
        "cipher": "AES-256-GCM",
        "data-ciphers": "AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305",
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


def session_monitor():
    """Monitor active VPN sessions and refresh firewall rules on state changes."""

    status_data = VPNTool.parse_iptables_traffic()
    with VPNSessionDao() as model:
        sessions = model.query_all()
        logger.debug(
            f"Session monitor has started. Active connections: {len(sessions['data'])}"
        )
        for s in sessions["data"]:
            local_ip = s.get("local_ip")
            if "pending" in s["state"]:
                logger.info(f"User {s['user_id']} connected, bind {s['local_ip']}")
                model.update_by_id(s["id"], {"state": "activated"})
                FirewallTool.refresh_user_chain(s["user_id"])

                if local_ip:
                    template_path = get_template_path("monitor_rules.j2")
                    with open(template_path, "r") as f:
                        template = Template(f.read())
                    script = template.render(local_ip=local_ip, action="insert")
                    subprocess.run(script, shell=True)

                with PolicyClientDao() as p_model:
                    policies = p_model.get_by_client(s["user_id"])
                    for p in policies:
                        FirewallTool.refresh_policy_chain(p["id"])
            elif "activated" in s["state"] and local_ip in status_data:
                stats = status_data[local_ip]
                model.update_by_id(
                    s["id"],
                    {
                        "bytes_received": stats["bytes_received"],
                        "bytes_sent": stats["bytes_sent"],
                    },
                )

            if "disconnect" in s["state"]:
                logger.info(f"User {s['user_id']} disconnected")
                if local_ip:
                    template_path = get_template_path("monitor_rules.j2")
                    with open(template_path, "r") as f:
                        template = Template(f.read())
                    script = template.render(local_ip=local_ip, action="delete")
                    subprocess.run(script, shell=True)
                model.delete_by_user_id(s["user_id"])
                FirewallTool.refresh_user_chain(s["user_id"])

                with PolicyClientDao() as p_model:
                    policies = p_model.get_by_client(s["user_id"])
                    for p in policies:
                        FirewallTool.refresh_policy_chain(p["id"])
