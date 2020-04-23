FROM mariadb:latest

RUN apt-get update -y && apt-get install -y \
	mysql-client \
	libmysqlclient-dev \
	libssl-dev \
	openssl \
	zlib1g-dev \
	p7zip-full

ENV world world_full_05_october_2019

COPY docker/database/generate-db-1.sql /docker-entrypoint-initdb.d
COPY docker/database/generate-db-2.sh /docker-entrypoint-initdb.d
