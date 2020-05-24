#!/bin/bash
#Basic script that builds only non-web version of project

echo "Basic script that builds only non-web version of project"

path=$(pwd)

git submodule update --init --remote

docker build -t vmangos_build -f docker/build/Dockerfile .

docker run \
	-v $(pwd)/vmangos:/vmangos \
	-v $(pwd)/src/database:/database \
	-v $(pwd)/src/ccache:/ccache \
	-e CCACHE_DIR=/ccache \
	-e threads=2 \
	--rm \
	vmangos_build

cd src/core/sql/migrations
chmod +x merge.sh
./merge.sh
cd $path

docker-compose -f noweb-docker-compose.yml up -d

echo "Please wait a few minutes while database is being built"

docker-compose ps

echo ""
echo "Basic setup is complete"
