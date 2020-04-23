#!/bin/sh
PATH=$(pwd)
echo "Beginning update script"
docker-compose down
echo "Running git pull"
git pull
git submodule update --remote 

echo "Running migration merge"

cd src/core/sql/migrations
chmod +x merge.sh
./merge.sh
cd $PATH

echo "Beginning docker-compose build"

./docker-build.sh

echo "Launching containers"

docker-compose up -d vmangos_database
echo "Updating mangos database"
docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql' 
echo "Updating characters database"
docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/characters_db_updates.sql' 
docker-compose up -d

