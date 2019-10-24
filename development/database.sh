#!/bin/bash

docker-compose down
sudo rm -rf docker/database/mysql
docker-compose build vmangos_database
docker-compose up vmangos_database
