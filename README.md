Release: 0.1.0

This is a project that is based on the vmangos core running on Docker. 

Source code from https://github.com/vmangos/core.

To setup this project first run the docker-build.sh to compile all of the necessary binaries and to create all of the necessary containers. Place dependencies labeled appropriately as listed: /src/data, /src/maps, /src/mmaps, /src/vmaps, /src/5875(adjust according to patch release), /src/5875/tbc. Next run docker-compose up vmangos_database and then exit container once process is finished and run docker-compose up -d.

Changes to most of these configs requires docker container rebuild or a manual change after docker containers are built to apply any changes.
Mangos config: vmangos/etc/mangosd.conf
Realmd config: vmangos/etc/realmd.conf
Server config: server.env
Database config: db.env
Database volume: docker/database/mysql

For updates that are applied on either of the src/ repositories run update.sh at your own risk in case of any breakage or changes. 

