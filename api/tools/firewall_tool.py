import subprocess
from api.utils import logger
from api.model.user_model import UserDao, UserPolicyDao
from api.model.policy_model import PolicyDao
from api.model.vpn_model import VPNSessionDao
from api.model.dmz_model import DMZServiceDao, PortMappingDao

class FirewallTool:

    @classmethod
    def remove_user(cls,user_id):
        subprocess.run(
            f"ipset del {user_id}_set",
            shell=True,
        )
        logger.info(f"{user_id}")

    @classmethod
    def create_user(cls,user_id):
        subprocess.run(
            f"ipset create {user_id}_set hash:ip",
            shell=True,
        )
        logger.info(f"{user_id}")
        
    @classmethod
    def refresh_service(cls,dmz_id):
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
        m_model = PortMappingDao()
        mappings = m_model.get_by_dmz_id(dmz_id)
        if mappings:
            for map in mappings:
                subprocess.run(
                    f"""iptables -A FORWARD -m comment --comment 'srv_{dmz_id}' -p {map['protocol']} \
                            --dport {map['user_port']} -m set --match-set {map['user_id']}_set dst -j ACCEPT """,
                        shell=True,
                )

        
    @classmethod
    def get_rule_ids(cls, user_id, table=None, chain="FORWARD"):
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

        user_page = UserDao().query_all()
        for u in user_page['data']:
            cls.create_user(u['id'])
            
        policy_page = PolicyDao().query_all()
        if "data" in policy_page:
            for p in policy_page["data"]:
                cls.create_policy_chain(p["id"])
                cls.refresh_policy_chain(p["id"])
                
        srv_page = DMZServiceDao().query_all()
        if "data" in srv_page:
            for s in srv_page["data"]: 
                cls.refresh_service(s['id'])
                
    @classmethod
    def refresh_sessions(cls, user_id):
        #s_model = VPNSessionDao(connection=model.connection)

        logger.info(f"Refresh {user_id} chain")
        """
        subprocess.run(f\"""iptables -t nat -i eth0 -A PREROUTING -m comment --comment 'srv_{dmz_id}' -p {map['protocol']} \
                            --dport {map['bind_port']} -j DNAT \
                            --to-destination {map['user_id']}_set:{map['user_port']} \""",
                        shell=True,
                )
        """

    @classmethod
    def create_policy_chain(cls, policy_id):
        subprocess.run(f"iptables -N p_{policy_id}", shell=True, check=True)
        
    @classmethod
    def refresh_policy_chain(cls, policy_id):
        logger.info(f"Refresh policy p_{policy_id}")

        model = PolicyDao()

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
                subprocess.run(
                        f"""iptables -A p_{policy_id} \
                                -m set --match-set {c['id']}_set dst \
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
