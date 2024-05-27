FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
	apt-get install -y \
		libace-dev \
		libmysql++-dev \
		libreadline-dev \
		libssl-dev \
		libtbb-dev \
		php-soap 
COPY ./vmangos/bin/mangosd /opt/vmangos/bin/mangosd
WORKDIR /opt/vmangos/bin
RUN chmod +x /opt/vmangos/bin
CMD ./mangosd -c ../etc/mangosd.conf
