FROM mysql:5.7

RUN apt-get update -y && apt-get install mysql-client libmysqlclient-dev libssl-dev openssl zlib1g-dev p7zip-full -y

COPY src/core/sql /opt/sql
COPY src/database /opt/sql/database 

ENV world world_full_05_october_2019
RUN cd /opt/sql/database && 7z e $world.7z && rm -rf $world.7z
COPY docker/database/generate-db-1.sql /docker-entrypoint-initdb.d
COPY docker/database/generate-db-2.sh /docker-entrypoint-initdb.d







