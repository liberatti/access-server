import os
import subprocess
from nxcore.middleware.logging_manager import logger
from config import BASE_BATH


class PKITool:
    """Utility class for Easy-RSA Public Key Infrastructure (PKI) management."""

    pki_bin = "/opt/easy-rsa"
    pki_dir = f"{BASE_BATH}/data/pki"
    re_pem = "(-+BEGIN (?:.+)-+[\\r\\n]+(?:[A-Za-z0-9+/=]{1,64}[\\r\\n]+)+-+END (?:.+)-+[\\r\\n]+)"

    @classmethod
    def remove_client(cls, user_id):
        """Revoke client certificate for a user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        subprocess.run(
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} revoke {user_id}",
            shell=True,
        )

    @classmethod
    def create_client(cls, user_id):
        """Generate client certificate and private key without password.

        :param user_id: User identifier.
        :type user_id: str
        """
        subprocess.run(
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} --days=3650 build-client-full {user_id} nopass",
            shell=True,
        )

    @classmethod
    def gen_crl(cls):
        """Generate Certificate Revocation List (CRL)."""
        subprocess.run(
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} --days=3650 gen-crl",
            shell=True,
        )

    @classmethod
    def create_pki(cls, server_name):
        """Initialize PKI directory structure, CA, server certificates, CRL, and keys.

        :param server_name: Common Name for server certificate.
        :type server_name: str
        """
        logger.info("Creating pki")
        if not os.path.exists(cls.pki_dir):
            os.mkdir(cls.pki_dir)

        cmds = [
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} init-pki",
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} build-ca nopass",
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} --days=3650 build-server-full {server_name} nopass",
            f"{cls.pki_bin}/easyrsa --batch --pki={cls.pki_dir} --days=3650 gen-crl",
            f"openvpn --genkey --secret {cls.pki_dir}/tc.key",
            f"openssl dhparam -out {cls.pki_dir}/dh.pem 2048",
        ]
        for cmd in cmds:
            subprocess.run(cmd, shell=True)
