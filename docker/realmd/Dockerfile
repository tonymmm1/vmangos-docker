FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
	apt-get install -y \
		libace-dev \
		libcurl4-openssl-dev \
		libmysql++-dev \
		libreadline-dev \
		libssl-dev \
		libtbb-dev \
		php-soap
COPY ./vmangos/bin/realmd /opt/vmangos/bin/realmd
COPY ./docker/server-entrypoint.sh /usr/local/bin/vmangos-entrypoint
WORKDIR /opt/vmangos/bin
RUN chmod +x realmd /usr/local/bin/vmangos-entrypoint
ENTRYPOINT ["/usr/local/bin/vmangos-entrypoint"]
CMD ["./realmd", "-c", "/run/vmangos/realmd.conf"]
