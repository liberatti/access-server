FROM node:20.14 as build-frontend

WORKDIR /opt/access-server

ADD package*.json .
RUN npm install

ADD . .
RUN npm run build

FROM rockylinux:8 as main

WORKDIR /opt/access-server

RUN dnf -y install epel-release \
 && dnf -y install git wget openvpn kmod iptables python3.12 python3.12-pip python3.12-setuptools gcc python3.12-devel\
 && dnf clean all

ENV EASYRSA_VERSION 3.1.7
RUN wget https://github.com/OpenVPN/easy-rsa/releases/download/v$EASYRSA_VERSION/EasyRSA-$EASYRSA_VERSION.tgz \
 && mkdir -p easy-rsa\
 && tar xzf EasyRSA-$EASYRSA_VERSION.tgz -C easy-rsa/ --strip-components 1 \
 && rm -f EasyRSA-$EASYRSA_VERSION.tgz \
 && chown -R root:root easy-rsa

ADD requirements.txt .
RUN pip3 install -U pip setuptools wheel\
 && pip3 install -r requirements.txt

ADD api api
ADD *.py .
ADD iptables-start.save .
COPY --from=build-frontend /opt/access-server/dist/index.html templates/
COPY --from=build-frontend /opt/access-server/dist static

ENV HOME /opt/access-server
ENTRYPOINT ["gunicorn","--bind=0.0.0.0:5000","--workers=2","main:create_app()"]