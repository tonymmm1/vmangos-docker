<h1>Release: 0.4.0</h1>

This is a project that is based on the VMaNGOS core running on Docker. 

Source code from https://github.com/vmangos/core.

Website code from https://gitlab.com/omghixd/fusiongen.git.

The configuration should be configured to work with localhost games and can be edited by changing the realmd.realmd table and adding the correct server information.
Changing the exposed port for mysql should also be considered if not removing it all together. Website functionality will be configured with a separate function within setup.sh.

<h2>Arm Notice:</h2>

Make sure the change the value of 'make -j$(nprocs)' to 'make -j1' or 'make -j2' in the last line of '/docker/build/Dockerfile' depending on if platform has less than 4GB of ram. 
```
vim /docker/build/Dockerfile
```
```
#change according to platform specs
... make -j$(nproc) ...
```

<h2>Step 1:</h2>
<h3>Requirements:</h3>

* Git installed

* Docker-CE installed

* Docker Compose installed

* Operating System that is 64 bit (Currently Raspbian is only 32bit)

* Python 3 installed

* Tmux(recommended for docker attach)

<h2>Step 2:</h2>
<h3> a.) Place dependencies as listed below:</h3> 

* /src/data 
* /src/data/maps
* /src/data/mmaps
* /src/data/vmaps
* /src/data/5875(adjust according to patch release)
* /src/data/5875/dbc
* /src/ccache

<h3>b.) Configuration Files:(*)</h3>

* Server config: 	/config
* Database config: 	/env/db.env
* VMaNGOS: 		/vmangos
* Database volume: 	/var/lib/docker/volumes/vmangos_database
* Website config: 	/web

<h2>Step 3:</h2>
<h3>a). Run setup.py for creating containers and for managing this project.
```
chmod +x 
./setup.py
```
<h3>b). Configure realm ip address</h3>
Use mysql-workbench or from the vmangos_database container edit the ip address column in realmd.realmlist to set the ip that will be exposed for connections(public ip required for internet). Using the account and password for the mangos user or the root user as can be configured in db.env. 

<h2>List of Commands:</h2>
<h3>General commands(All docker-compose commands must be run from within the project directory)</h3>

```
docker-compose up (Creates and runs containers with console output)
docker-compose up -d (Creates and detaches from running containers)
docker-compose ps (Lists all running containers)
docker-compose stop (Stops containers without destroying)
docker-compose restart (Restart containers)
docker-compose down (Destroys containers)
docker-compose down -v (Destroys containers and volumes)
docker-compose exec vmangos_(container) bash (Executes bash inside container of choice)
docker ps (Lists all running docker processes)
#using tmux/screen is recommended to not kill
docker attach (applies to the vmangos_mangos/realmd/database)  session
```
