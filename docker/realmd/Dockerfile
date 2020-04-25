FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y \
	libace-dev \
	libtbb-dev \
	openssl \
	libssl-dev \
	zlib1g-dev \
	libmysqlclient-dev 

COPY ./vmangos/bin/realmd /opt/vmangos/bin/realmd

WORKDIR /opt/vmangos/bin

RUN chmod +x realmd

CMD ./realmd -c ../etc/realmd.conf
