FROM node:20.14 as build-frontend

WORKDIR /src

ADD package*.json .
RUN npm ci

ADD . .
RUN npm run build

FROM rockylinux:9 as main

WORKDIR /opt

RUN dnf -y install epel-release \
    && dnf -y install git wget openvpn kmod ipset iptables python3.12 python3.12-pip python3.12-setuptools gcc python3.12-devel\
    && dnf clean all

ENV EASYRSA_VERSION 3.1.7
RUN wget https://github.com/OpenVPN/easy-rsa/releases/download/v$EASYRSA_VERSION/EasyRSA-$EASYRSA_VERSION.tgz \
    && mkdir -p easy-rsa\
    && tar xzf EasyRSA-$EASYRSA_VERSION.tgz -C easy-rsa/ --strip-components 1 \
    && rm -f EasyRSA-$EASYRSA_VERSION.tgz \
    && chown -R root:root easy-rsa

WORKDIR /opt/access-server

ADD requirements.txt .
RUN pip3.12 install -U pip setuptools>=65.5.1 wheel\
    && pip3.12 install -r requirements.txt

ADD api api
ADD *.py .
ADD iptables-start.save .
COPY --from=build-frontend /src/dist/index.html templates/
COPY --from=build-frontend /src/dist static

ENV HOME /opt/access-server
ENTRYPOINT ["python3.12","main.py"]