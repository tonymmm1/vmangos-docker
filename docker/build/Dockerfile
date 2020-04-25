FROM ubuntu:18.04

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y \
	build-essential \ 
	git \
	cmake \
	libtbb-dev \
	openssl \
	libssl-dev \
	libace-dev \
	p7zip-full \ 
	zlib1g-dev \
	libmysqlclient-dev \ 
	ccache 
		
RUN ln -s /usr/bin/ccache /usr/local/bin/gcc \ 
	&& ln -s /usr/bin/ccache /usr/local/bin/g++ \
	&& ln -s /usr/bin/ccache /usr/local/bin/cc \
        && ln -s /usr/bin/ccache /usr/local/bin/c++

RUN export ACE_ROOT=/usr/include/ace && export TBB_ROOT_DIR=/usr/include/tbb

COPY /src/core/ /opt/core

ENV vmangos_src /opt/core
ENV vmangos /opt/vmangos
ENV world world_full_05_october_2019
ENV threads 2

CMD mkdir $vmangos_src/build && cd $vmangos_src/build && \
	cmake -DDEBUG=0 -DSUPPORTED_CLIENT_BUILD=5875 \
	-DUSE_EXTRACTORS=1 \
	-DCMAKE_INSTALL_PREFIX=$vmangos ../ && \
	make -j $threads && \
	make install && \
	mkdir $vmangos/data && \
	mkdir $vmangos/logs && \
	cp $vmangos/etc/mangosd.conf.dist $vmangos/etc/mangosd.conf && \
	cp $vmangos/etc/realmd.conf.dist $vmangos/etc/realmd.conf && \
	cp -r /opt/vmangos/* /vmangos && cd /database && 7z e $world.7z



