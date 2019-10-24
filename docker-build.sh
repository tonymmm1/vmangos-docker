#!/bin/bash

#This script leverages .dockerignore files to help speed up the building process for each container and reduce waiting for docker build context

git submodule init
git submodule update

cd src/core/sql/migrations
chmod +x merge.sh
./merge.sh
cd ../../../../

docker-compose build
docker-compose up -d
