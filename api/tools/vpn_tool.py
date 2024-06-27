import ipaddress
import os
import re
import socket
import subprocess
import time
import traceback
import bcrypt
from flask import json
import psutil
from api.model.user_model import UserDao
from api.utils import chmod_r, logger
from api.tools.firewall_tool import FirewallTool
from api.tools.pki_tool import PKITool
from api.model.vpn_model import VPNSessionDao
from api.model.policy_model import PolicyClientDao


class VPNTool:

    __PORT = 1194

    @classmethod
    def update_crl(cls):
        PKITool.gen_crl()

    @classmethod
    def initialize(cls, config):
        logger.info(f"Initialize server {config['name']}")

        user_model = UserDao()
        hashed = bcrypt.hashpw(
            config.pop("admin_pass").encode("utf8"), bcrypt.gensalt()
        )
        pk = user_model.persist(
            {
                "name": "admin",
                "username": config.pop("admin_user"),
                "password": hashed.decode("utf-8"),
                "role": "admin",
            }
        )
        user_model.commit()
        user_model.close()

        with open(f"data/config.json", "w") as f:
            f.write(json.dumps(config))

        PKITool.create_pki(config["name"])
        cls.create_client(pk)
        cls.start_service()

    @classmethod
    def register_disconnection(cls, user_id):
        logger.info(f"User {user_id} disconnected")

    @classmethod
    def session_monitor(cls):
        logger.debug(f"Session monitor has started")
        model = VPNSessionDao()
        sessions = model.query_all()
        for s in sessions["data"]:
            if "pending" in s["state"]:
                logger.info(f"User {s['user_id']} connected, bind {s['local_ip']}")
                model.update_by_id(s["id"], {"state": "activated"})
                model.commit()
                FirewallTool.refresh_user_chain(s["user_id"])

                policies = PolicyClientDao().get_by_client(s["user_id"])
                for p in policies:
                    FirewallTool.refresh_policy_chain(p["id"])

            if "disconnect" in s["state"]:
                logger.info(f"User {s['user_id']} disconnected")
                model.delete_by_user_id(s["user_id"])
                model.commit()
                FirewallTool.refresh_user_chain(s["user_id"])

                policies = PolicyClientDao().get_by_client(s["user_id"])
                for p in policies:
                    FirewallTool.refresh_policy_chain(p["id"])
        model.close()

    @classmethod
    def is_active(cls):
        try:
            with socket.create_connection(("127.0.0.1", cls.__PORT), timeout=5):
                return True
        except Exception as e:
            logger.error(f"{e} localhost:{cls.__PORT}")
            return False

    @classmethod
    def wait_bind(cls, interval=5, retry=6):
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
        pid_file = f"server.pid"
        pid = None
        if os.path.exists(pid_file):
            with open(pid_file, "r") as file:
                try:
                    pid = int("".join(file.readlines()))
                    if pid:
                        processo = psutil.Process(pid)
                        is_running = processo.is_running()
                        if not is_running:
                            os.remove(pid_file)
                        else:
                            return pid
                except Exception:
                    os.remove(pid_file)
        return pid

    @classmethod
    def restart_service(cls):
        pid = cls.__get_pid()
        if pid:
            logger.info(f"VPN is running, reload required")
            p = psutil.Process(pid)
            p.kill()
        cls.start_service(wait=False)

    @classmethod
    def start_service(cls, wait=True):
        logger.info(f"Starting server")

        daoSession = VPNSessionDao()
        daoSession.delete_all()
        daoSession.commit()

        daoUser = UserDao()
        user_page = daoUser.query_all()
        if "data" in user_page:
            for u in user_page["data"]:
                FirewallTool.refresh_user_chain(u["id"])

        chmod_r("data", 0o777, recursive=True)
        with open(f"data/config.json", "r") as a:
            config = json.loads(a.read())
            cls.__create_server(config)
        if not os.path.exists(f"logs"):
            os.mkdir(f"logs")

        subprocess.Popen(
            f"openvpn --config server.conf --log logs/server.log --writepid server.pid",
            shell=True,
        )
        if wait:
            cls.wait_bind()

    @classmethod
    def is_initialized(cls):
        return os.path.exists(f"data/config.json")

    @classmethod
    def __create_server(cls, config):
        logger.info(f"Creating server for {config['name']}")
        srv_config = [
            f"port {cls.__PORT}",
            "proto tcp",
            "dev tun",
            f"ca {PKITool.pki_dir}/ca.crt",
            f"cert {PKITool.pki_dir}/issued/{config['name']}.crt",
            f"key {PKITool.pki_dir}/private/{config['name']}.key",
            f"dh {PKITool.pki_dir}/dh.pem",
            "auth SHA512",
            f"tls-crypt {PKITool.pki_dir}/tc.key",
            "topology subnet",
            f"server {config['subnet']}",
            "user nobody",
            "group nobody",
            "persist-key",
            "persist-tun",
            "verb 3",
            "keepalive 10 60",
            "script-security 2",
            f"auth-user-pass-verify openvpn-adapter.py via-file",
            f"client-connect openvpn-adapter.py",
            f"client-disconnect openvpn-adapter.py",
            f"crl-verify {PKITool.pki_dir}/crl.pem",
            f"management 127.0.0.1 23000",
        ]
        if "networks" in config:
            for r in config["networks"]:
                rede = ipaddress.IPv4Network(r)
                ip = str(rede.network_address)
                mask = str(rede.netmask)
                srv_config.append(f"route {ip} {mask}")

        with open(f"server.conf", "w") as f:
            f.write("\n".join(srv_config))

    @classmethod
    def create_client(cls, user_id):
        PKITool.create_client(user_id)

    @classmethod
    def remove_client(cls, user_id):
        PKITool.remove_client(user_id)
        model = PolicyClientDao()
        policies = model.get_by_client(user_id)
        if policies:
            for p in policies:
                FirewallTool.refresh_policy_chain(p["id"])

    @classmethod
    def get_openvpn_client(cls, user_id, target="default"):
        model = UserDao()
        with open(f"data/config.json", "r") as a:
            config = json.loads(a.read())

        with open(f"{PKITool.pki_dir}/tc.key", "r") as a:
            tls_key = a.read()

        with open(f"{PKITool.pki_dir}/ca.crt", "r") as a:
            ca_cert = a.read()

        with open(f"{PKITool.pki_dir}/issued/{user_id}.crt", "r") as a:
            cli_crt = re.findall(PKITool.re_pem, a.read())[0]

        with open(f"{PKITool.pki_dir}/private/{user_id}.key", "r") as a:
            cli_key = a.read()

        cli_config = [
            "client",
            "dev tun",
            "proto tcp",
            f"remote {config['public_address']} {config['public_port']}",
            "nobind",
            "remote-cert-tls server",
            "auth SHA512",
            "verb 3",
            "keepalive 10 60",
            "auth-user-pass",
            "<tls-crypt>",
            tls_key,
            "</tls-crypt>",
            "<ca>",
            ca_cert,
            "</ca>",
            "<cert>",
            cli_crt,
            "</cert>",
            "<key>",
            cli_key,
            "</key>",
        ]

        if "default" in target:
            cli_config.append("persist-key")
            cli_config.append("persist-tun")
            cli_config.append("resolv-retry infinite")
            cli_config.append("ping-timer-rem")

        user = model.get_by_id(user_id)
        if "policies" in user:
            for p in user["policies"]:
                if "networks" in p:
                    for net in p["networks"]:
                        rede = ipaddress.IPv4Network(net)
                        ip = str(rede.network_address)
                        mask = str(rede.netmask)
                        cli_config.append(f"route {ip} {mask}")
        return "\n".join(cli_config)
