<h1>Release: 0.5.0</h1>

This is a project that is based on the VMaNGOS core running on Docker. 

Source code from https://github.com/vmangos/core.

Website code from https://github.com/FusionGen/FusionGen.

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

* [Git 1.8.3+ installed](https://git-scm.com/)

* [Docker-CE 18.06.00+ installed](https://docs.docker.com/get-docker/)

* [Docker Compose 1.22.0+ installed](https://docs.docker.com/compose/install/)

* [Operating System that is 64 bit](https://en.wikipedia.org/wiki/64-bit_computing)[Currently Raspbian is only 64bit beta](https://www.raspberrypi.org/blog/latest-raspberry-pi-os-update-may-2020/)

* Python 3.5+ installed

* [Tmux(recommended for docker attach)](https://github.com/tmux/tmux/wiki/Getting-Started)

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
* Database config: 	/db/my.cnf
* VMaNGOS: 		/vmangos
* Database volume: 	/var/lib/docker/volumes/vmangos_database
* Website config: 	/web

<h2>Step 3:</h2>
<h3>a). Run setup.py for creating containers and for managing this project.Default flags are already applied and a help menu can be shown.</h3>
  
```
chmod +x 
./setup.py 
```

Help menu:

```
./setup.py -h
```

<h3>b). Configure realm ip address</h3>
Use mysql-workbench or from the vmangos_database container edit the ip address column in realmd.realmlist to set the ip that will be exposed for connections(public ip required for internet). Using the account and password for the mangos user or the root user as can be configured in db.env. 

<h2>Step 4:</h2>
<h3> a). Website file configuration</h3>

Make sure to edit /web/site.conf and change the server_name

```
vim web/site.conf
server_name ${FQDN};
```

<h3> b). Website installation</h3>

1. Visit http://${FQDN}/install
2. Proceed with installation steps 

<h2>Step 5: Maintenence</h2>
<h3> a). Updating all repos</h3>

```
./setup.py -m 0 --update
```

<h3> b). Cleaning CCache</h3>

```
./setup.py --ccache
```

<h3> c). Cleaning unused Docker Containers</h3>

```
./setup.py --docker
```

<h2> Command line options:</h2>

```
Vmangos-Docker cli

optional arguments:
  -h, --help  show this help message and exit
  -m M        Select mode
              	0 = website(default)
              	1 = no website
              	3 = reset all files
  --update    Use update mode
  -t T        Input number of threads to use for compiling, values 1-2(2 default) for <4GB ram
  -u U        Use user:group 1000:1000(default) 
  -c C        Input Client version to compile
              	4222 = 1.2.4
              	4297 = 1.3.1
              	4375 = 1.4.2
              	4449 = 1.5.1
              	4544 = 1.6.1
              	4695 = 1.7.1
              	4878 = 1.8.4
              	5086 = 1.9.4
              	5302 = 1.10.2
              	5464 = 1.11.2
              	5875 = 1.12.1(default)
  -a A        Enable anticheat
              	0 = Disable Anticheat(default)
              	1 = Enable Anticheat
  --ccache    Clean CCache(exclusive)
  --docker    Docker Clean(exclusive)
  -v          Increase output verbosity
```

Example command config

```
./setup.py -m 0 -t 2 -u 1000:1000 -c 5875 -a 0 
```

<h2>List of Commands:</h2>
<h3>General commands(All docker-compose commands must be run from within the project directory)</h3>

For non-website configs make sure to replace docker-compose with docker-compose -f noweb-docker-compose.yml

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
docker attach (applies to the vmangos_mangos/realmd/database) session
```
