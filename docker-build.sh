#!/bin/bash

#This script leverages .dockerignore files to help speed up the building process for each container and reduce waiting for docker build context

#General Purpose dockerignore file that is not used in this script
cp .dockerignore dockerignore/
rm .dockerignore

#Build container
cp dockerignore/build.dockerignore .dockerignore
docker build -t vmangos_build -f docker/build/Dockerfile .
docker run -v $(pwd)/vmangos:/vmangos vmangos_build
rm .dockerignore

#Database container
cp dockerignore/database.dockerignore .dockerignore
docker-compose build vmangos_database
rm .dockerignore

#Mangos container
cp dockerignore/mangos.dockerignore .dockerignore
docker-compose build vmangos_mangos
rm .dockerignore

#Realmd container
cp dockerignore/realmd.dockerignore .dockerignore
docker-compose build vmangos_realmd
rm .dockerignore

cp dockerignore/.dockerignore .dockerignore


