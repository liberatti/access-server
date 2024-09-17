import subprocess
from api.utils import logger
from api.model.user_model import UserPolicyDao, PortMappingDao
from api.model.policy_model import PolicyDao
from api.model.vpn_model import VPNSessionDao


class FirewallTool:

    @classmethod
    def get_user_rule_ids(cls, user_id, table=None, chain="FORWARD"):
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
        logger.info(f"Loading basic firewall")
        try:
            with open(f"/etc/sysctl.d/99-openvpn-forward.conf", "w") as f:
                f.write("net.ipv4.ip_forward=1")
        except:
            pass

        subprocess.run(
            f"iptables-restore iptables-start.save",
            shell=True,
        )
        logger.info(f"Build firewall")

        policies = PolicyDao().query_all()
        if "data" in policies:
            for p in policies["data"]:
                cls.create_policy_chain(p["id"])
                cls.refresh_policy_chain(p["id"])

    @classmethod
    def refresh_user_chain(cls, user_id):
        logger.info(f"Refresh {user_id} chain")

        model = UserPolicyDao()
        s_model = VPNSessionDao(connection=model.connection)

        fw_idx = cls.get_user_rule_ids(user_id)
        if fw_idx:
            for id in fw_idx:
                subprocess.run(f"iptables -D FORWARD {id}", shell=True, check=True)

        nat_idx = cls.get_user_rule_ids(user_id, table="nat", chain="PREROUTING")
        if nat_idx:
            for id in nat_idx:
                subprocess.run(
                    f"iptables -t nat -D PREROUTING {id}", shell=True, check=True
                )

        session = s_model.get_by_user_id(user_id)
        if session:
            policies = model.get_by_user_id(user_id)
            if policies:
                for p in policies:
                    subprocess.run(
                        f"""iptables -A FORWARD -m comment --comment '{user_id}'\
                                        -s {session['local_ip']} \
                                        -m state --state NEW,ESTABLISHED,RELATED \
                                        -j p_{p['id']}""",
                        shell=True,
                        check=True,
                    )
            m_model = PortMappingDao(connection=model.connection)
            mappings = m_model.get_by_user_id(user_id)
            if mappings:
                for map in mappings:
                    subprocess.run(
                        f"""iptables -A FORWARD -m comment --comment '{user_id}' -p {map['protocol']} \
                            --dport {map['user_port']} -d {session['local_ip']} -j ACCEPT """,
                        shell=True,
                    )
                    subprocess.run(
                        f"""iptables -t nat -i eth0 -A PREROUTING -m comment --comment '{user_id}' -p {map['protocol']} \
                            --dport {map['bind_port']} -j DNAT \
                            --to-destination {session['local_ip']}:{map['user_port']} """,
                        shell=True,
                    )

    @classmethod
    def create_policy_chain(cls, policy_id):
        subprocess.run(f"iptables -N p_{policy_id}", shell=True, check=True)

    @classmethod
    def refresh_policy_chain(cls, policy_id):
        logger.info(f"Refresh policy p_{policy_id}")

        model = PolicyDao()
        s_model = VPNSessionDao(connection=model.connection)

        subprocess.run(
            f"iptables -F p_{policy_id}",
            shell=True,
            check=True,
            stderr=subprocess.DEVNULL,
        )
        policy = model.get_by_id(policy_id)
        if policy:
            for addr in policy["networks"]:
                subprocess.run(
                    f"""iptables -A p_{policy_id} \
                                    -d {addr} \
                                    -m state --state NEW,ESTABLISHED,RELATED \
                                    -j ACCEPT""",
                    shell=True,
                    check=True,
                    stderr=subprocess.DEVNULL,
                )
            for c in policy["clients"]:
                session = s_model.get_by_user_id(c["id"])
                if session:
                    subprocess.run(
                        f"""iptables -A p_{policy_id} \
                                        -d {session['local_ip']} \
                                        -m state --state NEW,ESTABLISHED,RELATED \
                                        -j ACCEPT""",
                        shell=True,
                        check=True,
                        stderr=subprocess.DEVNULL,
                    )
            subprocess.run(
                f"""iptables -A p_{policy_id} -j RETURN""",
                shell=True,
                check=True,
                stderr=subprocess.DEVNULL,
            )
