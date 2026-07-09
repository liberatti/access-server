FROM --platform=$BUILDPLATFORM node:lts AS build_frontend

WORKDIR /app/web

COPY web/package*.json .
RUN npm install --legacy-peer-deps

COPY web /app/web

RUN npm run build

FROM rockylinux:9-minimal as main

WORKDIR /opt

RUN microdnf install epel-release -y \
    && microdnf install git wget openvpn kmod ipset iptables python3.12 python3.12-pip python3.12-setuptools gcc python3.12-devel tar -y \
    && microdnf clean all

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
COPY --from=build_frontend /app/web/dist/index.html templates/
COPY --from=build_frontend /app/web/dist static

ENV HOME /opt/access-server
ENTRYPOINT ["gunicorn", "-c", "api/gunicorn_config.py", "main:app"]
