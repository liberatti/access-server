import os
import subprocess
from jinja2 import Template
import config

from nxcore.middleware.logging_manager import logger

from api.model.user_model import UserDao
from api.model.policy_model import PolicyDao
from api.model.dmz_model import DMZServiceDao, PortMappingDao
from api.model.vpn_model import VPNSessionDao


from api.utils import get_template_path


class FirewallTool:
    """Utility class for managing iptables firewall rules and ipsets."""

    @classmethod
    def remove_user(cls, user_id):
        """Remove the ipset associated with a user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        subprocess.run(
            f"ipset del {user_id}_set",
            shell=True,
        )
        logger.info(f"{user_id}")

    @classmethod
    def create_user(cls, user_id):
        """Create a new hash:ip ipset for a user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        subprocess.run(
            f"ipset create {user_id}_set hash:ip",
            shell=True,
        )
        logger.info(f"{user_id}")

    @classmethod
    def refresh_service(cls, dmz_id):
        """Refresh iptables forward and NAT rules for a specific DMZ service using Jinja2 template.

        :param dmz_id: DMZ service identifier.
        :type dmz_id: str
        """
        fw_idx = cls.get_rule_ids(f"srv_{dmz_id}")
        if fw_idx:
            for id in fw_idx:
                subprocess.run(f"iptables -D FORWARD {id}", shell=True, check=True)

        nat_idx = cls.get_rule_ids(f"srv_{dmz_id}", table="nat", chain="PREROUTING")
        if nat_idx:
            for id in nat_idx:
                subprocess.run(
                    f"iptables -t nat -D PREROUTING {id}", shell=True, check=True
                )

        with PortMappingDao() as m_model:
            mappings = m_model.get_by_dmz_id(dmz_id)

        if mappings:
            template_path = get_template_path("dmz_rules.j2")
            with open(template_path, "r") as f:
                template = Template(f.read())

            script = template.render(dmz_id=dmz_id, mappings=mappings)
            subprocess.run(script, shell=True, check=True)

    @classmethod
    def get_rule_ids(cls, user_id, table=None, chain="FORWARD"):
        """Get iptables rule line numbers matching a specific comment or string.

        :param user_id: Comment string or identifier to search for in rules.
        :type user_id: str
        :param table: Optional iptables table name (e.g. 'nat').
        :type table: str or None
        :param chain: Target chain name.
        :type chain: str
        :return: List of rule IDs sorted in reverse order, or None.
        :rtype: list[int] or None
        """
        try:
            cmd = f"iptables -L {chain} -n --line-numbers -v"
            if table:
                cmd = f"iptables -t {table} -L {chain} -n --line-numbers -v"
            result = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.DEVNULL,
            )
            if result:
                rule_ids = []
                lines = result.decode("utf-8").splitlines()
                for line in lines:
                    if user_id in line:
                        parts = line.split()
                        rule_ids.append(int(parts[0]))
                return sorted(rule_ids, reverse=True)
            return None
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando iptables: {e}")
            return None

    @classmethod
    def create_firewall(cls):
        """Build initial firewall rules, ipsets, and policy chains from database."""
        logger.info("Loading basic firewall")
        try:
            with open("/etc/sysctl.d/99-openvpn-forward.conf", "w") as f:
                f.write("net.ipv4.ip_forward=1")
        except Exception:
            pass

        subprocess.run(
            "iptables-restore < iptables-start.save",
            shell=True,
        )
        logger.info("Build firewall")

        with UserDao() as user_dao:
            user_page = user_dao.query_all()
            for u in user_page["data"]:
                cls.create_user(u["id"])

        with PolicyDao() as policy_dao:
            policy_page = policy_dao.query_all()
            if "data" in policy_page:
                for p in policy_page["data"]:
                    cls.create_policy_chain(p["id"])
                    cls.refresh_policy_chain(p["id"])

        with DMZServiceDao() as srv_dao:
            srv_page = srv_dao.query_all()
            if "data" in srv_page:
                for s in srv_page["data"]:
                    cls.refresh_service(s["id"])

    @classmethod
    def refresh_user_chain(cls, user_id):
        """Refresh active session firewall rules and ipset for a user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        logger.info(f"Refresh {user_id} chain")
        with VPNSessionDao() as s_model:
            session = s_model.get_by_user_id(user_id)
            if session and session.get("local_ip"):
                subprocess.run(
                    f"ipset add {user_id}_set {session['local_ip']} -exist",
                    shell=True,
                )

    refresh_sessions = refresh_user_chain

    @classmethod
    def create_policy_chain(cls, policy_id):
        """Create a custom iptables chain for a policy.

        :param policy_id: Policy identifier.
        :type policy_id: str
        """
        subprocess.run(f"iptables -N p_{policy_id}", shell=True, check=True)

    @classmethod
    def refresh_policy_chain(cls, policy_id):
        """Flush and rebuild iptables rules for a policy chain using Jinja2 template.

        :param policy_id: Policy identifier.
        :type policy_id: str
        """
        logger.info(f"Refresh policy p_{policy_id}")

        with PolicyDao() as model:
            policy = model.get_by_id(policy_id)

        if policy:
            template_path = get_template_path("policy_rules.j2")
            with open(template_path, "r") as f:
                template = Template(f.read())

            script = template.render(
                policy_id=policy_id,
                networks=policy.get("networks", []),
                clients=policy.get("clients", []),
            )
            subprocess.run(script, shell=True, check=True, stderr=subprocess.DEVNULL)
