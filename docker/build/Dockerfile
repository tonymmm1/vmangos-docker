FROM ubuntu:18.04

RUN apt-get update -y && apt-get install software-properties-common -y && add-apt-repository universe -y && apt-get update -y && apt-get install build-essential gcc g++ automake git-core git autoconf make patch libmysql++-dev libtool libssl-dev grep binutils zlibc libc6 libbz2-dev cmake subversion libboost-all-dev wget tmux p7zip-full libtbb-dev libace-dev libmysqlclient-dev openssl libssl-dev zlib1g-dev -y

RUN export ACE_ROOT=/usr/include/ace && export TBB_ROOT_DIR=/usr/include/tbb

COPY /src/core/ /opt/core

ENV vmangos_src /opt/core
ENV vmangos /opt/vmangos

Entrypoint mkdir $vmangos_src/build && cd $vmangos_src/build && cmake -DDEBUG=0 -DSUPPORTED_CLIENT_BUILD=5875 -DUSE_EXTRACTORS=0 -DCMAKE_INSTALL_PREFIX=$vmangos ../ && make -j $(nproc) && make install && mkdir $vmangos/data && mkdir $vmangos/logs && cp $vmangos/etc/mangosd.conf.dist $vmangos/etc/mangosd.conf && cp $vmangos/etc/realmd.conf.dist $vmangos/etc/realmd.conf && cp -r /opt/vmangos/* /vmangos && cp -r /opt/core/build/* /build 



