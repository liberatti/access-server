import os
import subprocess
from api.utils import logger


class PKITool:
    pki_dir = f"./data/pki"
    re_pem = "(-+BEGIN (?:.+)-+[\\r\\n]+(?:[A-Za-z0-9+/=]{1,64}[\\r\\n]+)+-+END (?:.+)-+[\\r\\n]+)"

    @classmethod
    def remove_client(cls, user_id):
        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} revoke {user_id}",
            shell=True,
        )

    @classmethod
    def create_client(cls, user_id):
        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} --days=3650 build-client-full {user_id} nopass",
            shell=True,
        )

    def gen_crl(cls):
        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} --days=3650 gen-crl",
            shell=True,
        )

    @classmethod
    def create_pki(cls, server_name):
        logger.info(f"Creating pki")
        if not os.path.exists(cls.pki_dir):
            os.mkdir(cls.pki_dir)

        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} init-pki",
            shell=True,
        )
        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} build-ca nopass",
            shell=True,
        )
        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} --days=3650 build-server-full {server_name} nopass",
            shell=True,
        )
        subprocess.run(
            f"easy-rsa/easyrsa --batch --pki={cls.pki_dir} --days=3650 gen-crl",
            shell=True,
        )
        subprocess.run(f"openvpn --genkey --secret {cls.pki_dir}/tc.key", shell=True)
        subprocess.run(f"openssl dhparam -out {cls.pki_dir}/dh.pem 2048", shell=True)
