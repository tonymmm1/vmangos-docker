FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y \
	libace-dev \
	libtbb-dev \
	openssl \
	libssl-dev \
	zlib1g-dev \
	libcurl4-openssl-dev \
	php-soap \
	libmysqlclient-dev 

COPY ./vmangos/bin/mangosd /opt/vmangos/bin/mangosd

WORKDIR /opt/vmangos/bin

RUN chmod +x /opt/vmangos/bin

CMD ./mangosd -c ../etc/mangosd.conf

