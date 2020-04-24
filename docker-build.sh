#!/bin/bash

#This script leverages .dockerignore files to help speed up the building process for each container and reduce waiting for docker build context
root=$(pwd)
git submodule init
git submodule update --remote --recursive

cd src/core/sql/migrations
chmod +x merge.sh
./merge.sh
cd $root

docker build -t vmangos_build -f docker/build/Dockerfile . &&\ 
	docker run -v $(pwd)/vmangos:/vmangos \
	-v $(pwd)/src/database:/database \
	-v $(pwd)/src/ccache:/ccache \
	-e CCACHE_DIR=/ccache \
	--rm 
	vmangos_build 
