import ipaddress
import os
import re
import socket
import subprocess
import time
from flask import json
from jinja2 import Template
import psutil
import config
from api.model.user_model import UserDao
from api.utils import chmod_r, get_template_path
from api.tools.firewall_tool import FirewallTool
from api.tools.pki_tool import PKITool
from api.model.vpn_model import VPNSessionDao
from api.model.policy_model import PolicyClientDao
from api.model.server_config_model import ServerConfigDao
from nxcore.middleware.logging_manager import logger


class VPNTool:
    """Utility class for OpenVPN server management and client configuration."""

    __PORT = 1194

    @classmethod
    def update_crl(cls):
        """Update and regenerate Certificate Revocation List (CRL)."""
        PKITool.gen_crl()

    @classmethod
    def initialize(cls, config):
        """Initialize OpenVPN server configuration, PKI certificates, and start service.

        :param config: Configuration dictionary containing server settings.
        :type config: dict
        """
        logger.info(f"Initialize server {config['name']}")

        with ServerConfigDao() as dao:
            existing = dao.get_config()
            if existing:
                dao.update_by_id(existing["id"], config)
            else:
                dao.persist(config)

        PKITool.create_pki(config["name"])
        cls.create_client(config["admin_pk"])
        cls.start_service()

    @classmethod
    def register_disconnection(cls, user_id):
        """Log user disconnection event.

        :param user_id: User identifier.
        :type user_id: str
        """
        logger.info(f"User {user_id} disconnected")

    @classmethod
    def parse_iptables_traffic(cls):
        """Parse iptables -L -v -n -x to extract bytes received/sent for each active session IP.

        :return: Dictionary mapping local_ip to client stats.
        :rtype: dict
        """
        import re
        res = {}
        try:
            # -x outputs exact bytes instead of rounded values (like K, M, G)
            out = subprocess.check_output("iptables -L -v -n -x", shell=True, text=True)
            for line in out.splitlines():
                # We search for comment: /* traffic_out_10.8.0.2 */ or /* traffic_in_10.8.0.2 */
                m = re.search(r"/\*\s+traffic_(out|in)_(.*?)\s+\*/", line)
                if m:
                    direction = m.group(1) # 'out' or 'in'
                    ip = m.group(2) # e.g. '10.8.0.2'
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            bytes_count = int(parts[1])
                        except ValueError:
                            continue
                        if ip not in res:
                            res[ip] = {"bytes_sent": 0, "bytes_received": 0}
                        if direction == "out":
                            # Traffic from client (received by server / upload)
                            res[ip]["bytes_received"] += bytes_count
                        else:
                            # Traffic to client (sent to client / download)
                            res[ip]["bytes_sent"] += bytes_count
        except Exception as e:
            logger.error(f"Error reading iptables stats: {e}")
        return res


    @classmethod
    def is_active(cls):
        """Check if OpenVPN server is bound and active on management port.

        :return: True if service is active, False otherwise.
        :rtype: bool
        """
        try:
            with socket.create_connection(("127.0.0.1", cls.__PORT), timeout=5):
                return True
        except Exception as e:
            logger.error(f"{e} localhost:{cls.__PORT}")
            return False

    @classmethod
    def wait_bind(cls, interval=5, retry=6):
        """Wait for OpenVPN server to bind to management port.

        :param interval: Seconds between retry attempts.
        :type interval: int
        :param retry: Maximum number of retry attempts.
        :type retry: int
        :return: True if bound successfully, False if timed out.
        :rtype: bool
        """
        r = 0
        while r < retry:
            try:
                with socket.create_connection(("127.0.0.1", cls.__PORT), timeout=5):
                    return True
            except Exception as e:
                logger.error(f"{e} localhost:{cls.__PORT}")
                time.sleep(interval)
                r += 1
        return False

    @classmethod
    def __get_pid(cls):
        """Retrieve active OpenVPN process PID from PID file.

        :return: Process PID if running, else None.
        :rtype: int or None
        """
        pid_file = "server.pid"
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as file:
                    content = file.read().strip()
                    if content:
                        pid = int(content)
                        if psutil.pid_exists(pid):
                            p = psutil.Process(pid)
                            if p.is_running():
                                return pid
            except (ValueError, psutil.NoSuchProcess, OSError):
                pass

            try:
                os.remove(pid_file)
            except OSError:
                pass
        return None

    @classmethod
    def restart_service(cls):
        """Restart active OpenVPN server process."""
        pid = cls.__get_pid()
        if pid:
            logger.info("VPN is running, reload required")
            try:
                p = psutil.Process(pid)
                p.kill()
            except (psutil.NoSuchProcess, OSError) as e:
                logger.warning(f"Process {pid} was not running: {e}")
        cls.start_service(wait=False)

    @classmethod
    def start_service(cls, wait=True):
        """Start OpenVPN server background process.

        :param wait: Whether to wait until server binds to port.
        :type wait: bool
        """
        logger.info("Starting server")

        with VPNSessionDao() as daoSession:
            daoSession.delete_all()

        chmod_r("data", 0o777, recursive=True)
        with ServerConfigDao() as dao:
            config = dao.get_config() or {}
            cls.__create_server(config)
        if not os.path.exists("logs"):
            os.mkdir("logs")

        subprocess.Popen(
            "openvpn --config server.conf --log logs/server.log --writepid server.pid",
            shell=True,
        )
        if wait:
            cls.wait_bind()

    @classmethod
    def __create_server(cls, config):
        """Generate server.conf file based on server configuration dictionary.

        :param config: Configuration dictionary containing server parameters.
        :type config: dict
        """
        logger.info(f"Creating server for {config['name']}")
        subnet = (
            config.get("subnet")
            or f"{config.get('network', '10.8.0.0')} {config.get('netmask', '255.255.255.0')}"
        )
        routes = []
        if "networks" in config:
            for r in config["networks"]:
                rede = ipaddress.IPv4Network(r)
                routes.append(
                    {"ip": str(rede.network_address), "mask": str(rede.netmask)}
                )

        protocol = config.get("protocol") or "udp"
        if "tcp" in protocol:
            protocol = "tcp-server"
        else:
            protocol = "udp"

        auth = config.get("auth") or "SHA512"
        cipher = config.get("cipher") or "AES-256-GCM"
        data_ciphers = (
            config.get("data-ciphers")
            or config.get("data_ciphers")
            or "AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305"
        )

        template_path = get_template_path("server.conf.j2")
        with open(template_path, "r") as f:
            template = Template(f.read())

        server_conf_content = template.render(
            port=cls.__PORT,
            name=config["name"],
            pki_dir=PKITool.pki_dir,
            subnet=subnet,
            routes=routes,
            protocol=protocol,
            auth=auth,
            cipher=cipher,
            data_ciphers=data_ciphers,
        )

        with open("server.conf", "w") as f:
            f.write(server_conf_content)

    @classmethod
    def create_client(cls, user_id):
        """Generate client certificates for a user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        PKITool.create_client(user_id)

    @classmethod
    def remove_client(cls, user_id):
        """Revoke client certificates and refresh policy chains.

        :param user_id: User identifier.
        :type user_id: str
        """
        PKITool.remove_client(user_id)
        with PolicyClientDao() as model:
            policies = model.get_by_client(user_id)
            if policies:
                for p in policies:
                    FirewallTool.refresh_policy_chain(p["id"])

    @classmethod
    def get_openvpn_client(cls, user_id, target="default"):
        """Generate OpenVPN client configuration file content (.ovpn) using Jinja2 template.

        :param user_id: User identifier.
        :type user_id: str
        :param target: Target configuration profile type.
        :type target: str
        :return: Complete OpenVPN client configuration string.
        :rtype: str
        """
        with UserDao() as model:
            user = model.get_by_id(user_id)

        with ServerConfigDao() as dao:
            config = dao.get_config() or {}

        with open(f"{PKITool.pki_dir}/tc.key", "r") as a:
            tls_key = a.read().strip()

        with open(f"{PKITool.pki_dir}/ca.crt", "r") as a:
            ca_cert = a.read().strip()

        with open(f"{PKITool.pki_dir}/issued/{user_id}.crt", "r") as a:
            cli_crt = re.findall(PKITool.re_pem, a.read())[0].strip()

        with open(f"{PKITool.pki_dir}/private/{user_id}.key", "r") as a:
            cli_key = a.read().strip()

        public_addr = config.get("public_address") or config.get("host") or "127.0.0.1"
        public_port = config.get("public_port") or config.get("port") or 1194

        routes = []
        if user and "policies" in user:
            for p in user["policies"]:
                if "networks" in p:
                    for net in p["networks"]:
                        rede = ipaddress.IPv4Network(net)
                        routes.append(
                            {"ip": str(rede.network_address), "mask": str(rede.netmask)}
                        )

        protocol = config.get("protocol") or "udp"
        if "tcp" in protocol:
            protocol = "tcp-client"
        else:
            protocol = "udp"

        auth = config.get("auth") or "SHA512"
        cipher = config.get("cipher") or "AES-256-GCM"
        data_ciphers = (
            config.get("data-ciphers")
            or config.get("data_ciphers")
            or "AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305"
        )

        template_path = get_template_path("client.ovpn.j2")
        with open(template_path, "r") as f:
            template = Template(f.read())

        return template.render(
            public_addr=public_addr,
            public_port=public_port,
            tls_key=tls_key,
            ca_cert=ca_cert,
            cli_crt=cli_crt,
            cli_key=cli_key,
            target=target,
            routes=routes,
            protocol=protocol,
            auth=auth,
            cipher=cipher,
            data_ciphers=data_ciphers,
        )
