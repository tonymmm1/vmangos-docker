FROM ubuntu:18.04

RUN apt-get update -y && apt-get install libace-dev libtbb-dev openssl libssl-dev zlib1g-dev libmysqlclient-dev -y
COPY vmangos/bin/mangosd /opt/vmangos/bin/mangosd
COPY vmangos/bin/run-mangosd /opt/vmangos/bin/run-mangosd
COPY vmangos/etc/mangosd.conf /opt/vmangos/etc/mangosd.conf
COPY src/data/vmaps /opt/vmangos/bin/vmaps
COPY src/data/mmaps /opt/vmangos/bin/mmaps
COPY src/data/maps /opt/vmangos/bin/maps
COPY src/data/5875 /opt/vmangos/bin/5875
RUN sed -i "s/127.0.0.1/vmangos_database/g" /opt/vmangos/etc/mangosd.conf 
RUN chmod +x /opt/vmangos/bin/mangosd
WORKDIR /opt/vmangos/bin
CMD ./mangosd 

