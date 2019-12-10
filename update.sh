#!/bin/sh

echo "Beginning update script"

echo "Running git pull"
git pull
git pull --recurse-submodules
git submodule update --remote 

echo "Running migration merge"

cd src/core/sql/migrations
chmod +x merge.sh
./merge.sh
cd ../../../../

echo "Beginning docker-compose build"

./docker-build.sh

echo "Launching containers"

docker-compose up -d vmangos_database
docker-compose exec vmangos_database sh -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/sql/migrations/world_db_updates.sql' 
docker-compose up -d

