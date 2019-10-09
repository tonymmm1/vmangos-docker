#!/bin/sh

echo "Beginning update script"

echo "Running git pull"
git pull
cd src/database
git pull 
cd ..
cd core/
git pull 

echo "Running migration merge"

cd sql/migrations
./merge.sh
cd ../../../../

echo "Beginning docker-compose build"

./docker-build.sh


