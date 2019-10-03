FROM ubuntu:18.04

RUN apt-get update -y && apt-get install libace-dev libtbb-dev openssl libssl-dev zlib1g-dev libmysqlclient-dev -y
COPY vmangos/bin/realmd /opt/vmangos/bin/realmd
COPY vmangos/etc/realmd.conf /opt/vmangos/etc/realmd.conf
RUN sed -i "s/127.0.0.1/vmangos_database/g" /opt/vmangos/etc/realmd.conf
ENTRYPOINT /opt/vmangos/bin/realmd
