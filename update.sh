#!/bin/sh

echo "Beginning update script"

echo "Running git fetch"

git -C src/core/ fetch origin

echo "Running migration merge"

./src/core/sql/migrations/merge.sh

echo "Beginning docker-compose build"

docker-compose build

echo "Launching containers"

docker-compose up -d
