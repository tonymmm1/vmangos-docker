#!/bin/bash

#This script leverages .dockerignore files to help speed up the building process for each container and reduce waiting for docker build context

git submodule init
git submodule update 

cd src/core/sql/migrations
chmod +x merge.sh
./merge.sh
cd ../../../../

docker build -t vmangos_build -f docker/build/Dockerfile . && docker run -v $(pwd)/vmangos:/vmangos -v $(pwd)/src/database:/database vmangos_build

docker-compose build
docker-compose up -d
