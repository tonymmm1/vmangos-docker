Release: 0.2.0

This is a project that is based on the vmangos core running on Docker. 

Source code from https://github.com/vmangos/core.

The configuration should be configured to work with localhost games and can be edited by changing the realmd.realmd table and adding the correct server information.
Changing the exposed port for mysql should also be considered if not removing it all together. 

To setup this project first run the docker-build.sh to compile all of the necessary binaries and to create all of the necessary containers. Next run docker-compose up vmangos_database and wait until mysql has completed setup process. Use cntrl+c to exit the console. Now the project should be ready to go with Vanilla WoW using docker-compose up -d for future launches. This project is set to compile for patch 1.12.1 and use of map extractors will require the build container to be edited from USE_EXTRACTORS=0 -> USE_EXTRACTORS=1. The rest of the information can be found on the vmangos/core github page. Place dependencies labeled appropriately as shown below:
/src/data, /src/maps, /src/mmaps, /src/vmaps, /src/5875(adjust according to patch release), /src/5875/tbc.

Server config: server.env
Database config: db.env
Mangos config: mangos.env
Mangos server: /vmangos
Mangos server configs: /vmangos/etc
Database volume: /var/lib/docker/volumes/vmangos_database
Scripts: /scripts
Development scripts: /development


For updates that are applied on either of the src/ repositories run update.sh at your own risk in case of any breakage or changes. 


Multi-realm:

There is now a script to create a new realm on the same docker host. Copy the script new-realm.sh into the project root folder and execute it. Make sure to run update.sh script first to ensure that db updates are applied into the src/core/sql git submodule. The realm can be custom configured by either manually copying all of the files that are required to start the realm and creating appropriate directories and edits or by executing docker commands to enter the container and editing manually.

List of commands:


#General commands
#Creates and runs containers with serial on
docker-compose up 
#Creates and detaches from running containers
docker-compose up -d
#Stops containers without destroying
docker-compose stop
#Restarts containers
docker-compose restart
#Destroys containers
docker-compose down
#Destroys containers and volumes
docker-compose down -v

#Executes bash inside container of choice
docker-compose exec vmangos_(container) bash
#Lists all running docker processes
docker ps 
#Connects to docker containers with tty
docker attach (applies to the vmangos_mangos container)


