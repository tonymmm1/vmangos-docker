FROM mariadb:latest

RUN apt-get update -y && apt-get install -y \
	mariadb-client \
	libmysqlclient-dev \
	libssl-dev \
	openssl \
	zlib1g-dev \
	libcurl4-openssl-dev \
	p7zip-full

ENV world world_full_14_june_2021

COPY docker/database/generate-db-1.sql /docker-entrypoint-initdb.d
COPY docker/database/generate-db-2.sh /docker-entrypoint-initdb.d
