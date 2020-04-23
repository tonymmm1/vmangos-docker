FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y \
	libace-dev \
	libtbb-dev \
	openssl \
	libssl-dev \
	zlib1g-dev \
	libmysqlclient-dev 

WORKDIR /opt/vmangos/bin

CMD ./mangosd -c ../etc/mangosd.conf

