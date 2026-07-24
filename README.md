# Access Server

It's a full network tunneling VPN software solution that integrates OpenVPN server capabilities and enterprise management capabilities.


[![Docker Image](https://img.shields.io/badge/docker-ready-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/liberatti/access-server)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-♥-ea4aaa?style=flat&logo=github)](https://github.com/sponsors/liberatti)


## Host Configuration
Before diving into the container setup, ensure the following configurations on your host machine:

### Enable the TUN kernel module:
The TUN module is a kernel driver that allows user-space programs to create virtual network interfaces, which can be used to transport network traffic securely between two points.

```
modprobe tun
```

### Enable Ip forward
If your container will forward requests, modify /etc/sysctl.conf:

```
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p
```

## Executing container
Container VPN service will need to know its publication IP and port to pre-build client configuration:
```
docker volume create access-server_config
docker run --privileged -p 1194:1194 -p 5000:5000 \
    -v access-server_config:/opt/access-server/data \
    --name access-server \
    liberatti/access-server:latest
```

After startup, it is possible to configure vpn service on http://localhost:5000

This may take a wile, all the pki wil be generated


### Default screenshots of configuration pages

- **Users:** Gerenciamento de contas de usuários e credenciais de acesso.
  ![Users](.docs/01-users.png)

- **Policy:** Definição de regras de acesso e políticas de tráfego.
  ![Policy](.docs/02-policy.png)

- **Services:** Cadastro de serviços e destinos disponíveis na rede.
  ![Services](.docs/03-services.png)

- **Configuration:** Configurações globais do servidor VPN e parâmetros de rede.
  ![Configuration](.docs/04-config.png)


## Agent Configurations

This repository contains localized rules and skills for agentic AI workflows. For more details, see the [.agents/README.md](file:///home/liberatti/workspace/github.com/liberatti/access-server/.agents/README.md).


## License Terms

This product utilizes OpenVPN, an open-source software application that provides a secure, point-to-point or site-to-site connection in a routed or bridged configuration. OpenVPN is developed and maintained by the OpenVPN Project.

### Overview

The GNU General Public License (GPL) is an open-source software license developed by the Free Software Foundation (FSF). It is designed to ensure the freedom to use, modify, and distribute software while preserving user rights.

### Full License Text

For the complete text of the GNU General Public License, refer to the [official GPL page](https://www.gnu.org/licenses/gpl.html).


### OpenVPN Project

- **Website:** [OpenVPN Project](https://openvpn.net/)
- **GitHub Repository:** [OpenVPN on GitHub](https://github.com/OpenVPN)