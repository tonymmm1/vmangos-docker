FROM ubuntu:18.04

RUN apt-get update -y && apt-get install libace-dev libtbb-dev openssl libssl-dev zlib1g-dev libmysqlclient-dev -y

COPY src/data/vmaps /opt/vmangos/bin/vmaps
COPY src/data/mmaps /opt/vmangos/bin/mmaps
COPY src/data/maps /opt/vmangos/bin/maps
COPY src/data/5875 /opt/vmangos/bin/5875

COPY vmangos/bin/mangosd /opt/vmangos/bin/mangosd
COPY vmangos/etc/mangosd.conf /opt/vmangos/etc/mangosd.conf
RUN sed -i "s/127.0.0.1;3306;mangos;mangos/vmangos_database;3306;mangos;mangos/g" /opt/vmangos/etc/mangosd.conf 
RUN chmod +x /opt/vmangos/bin/mangosd
WORKDIR /opt/vmangos/bin
CMD ./mangosd -c ../etc/mangosd.conf

