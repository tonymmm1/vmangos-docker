FROM mariadb:latest
ENV WORLD world_full_14_june_2021
RUN apt-get update -y && \
	apt-get install -y \
		mariadb-client
COPY docker/database/generate-db-1.sql /docker-entrypoint-initdb.d
COPY docker/database/generate-db-2.sh /docker-entrypoint-initdb.d
