FROM mariadb:10.11.19

ENV WORLD=world_full_14_june_2021

COPY docker/database/generate-db-1.sql /docker-entrypoint-initdb.d/10-create-databases.sql
COPY docker/database/generate-db-2.sh /docker-entrypoint-initdb.d/20-initialize-vmangos.sh
