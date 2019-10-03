This is a project that is based on the vmangos core running on Docker. 

Source code from https://github.com/vmangos/core.

The configuration should be configured to work with localhost games and can be edited by changing the realmd.realmd table and adding the correct server information.
Changing the exposed port for mysql should also be considered if not removing it all together. 

To setup this project first run the docker-build.sh to compile all of the necessary binaries. Next run a docker-compose up and the project should be ready to go with Vanilla WoW. This project is set to compile for patch 1.12.1 and use of map extractors will require the build container to be edited from USE_EXTRACTORS=0 -> USE_EXTRACTORS=1. The rest of the information can be found on the vmangos/core github page. Place a world file labeled world.sql into the src folder as well as the map files and tbc labeled appropriately as listed below:

/src
 /data
  /maps
  /mmaps
  /vmaps
  /5875(adjust according to patch release)
   /tbc
-world.sql

Finally set a MYSQL_ROOT_PASSWORD in the db.env file to something secure and decide whether or not to keep the vmangos_database service exposed to the outside. Additional setup would include changing the server settings located in the realmd.realmd table under the line realmlist using MySQL Workbench. Then input the actual server ip or hostname and the corresponding configurations. 
An update script will be provided which will gather all of the new migrations via a git pull and will recreate containers. 
