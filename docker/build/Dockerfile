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
	libcurl4-openssl-dev \
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

#Compile Variables
#--------------------------------------------------------
#Compile threads
ENV threads 2

#Debug mode
ENV DEBUG 0

#0. TBB, 1. malloc
ENV MALLOC 0

#Client versions builds and corresponding values
#define CLIENT_BUILD_1_2_4 4222
#define CLIENT_BUILD_1_3_1 4297
#define CLIENT_BUILD_1_4_2 4375
#define CLIENT_BUILD_1_5_1 4449
#define CLIENT_BUILD_1_6_1 4544
#define CLIENT_BUILD_1_7_1 4695
#define CLIENT_BUILD_1_8_4 4878
#define CLIENT_BUILD_1_9_4 5086
#define CLIENT_BUILD_1_10_2 5302
#define CLIENT_BUILD_1_11_2 5464
#define CLIENT_BUILD_1_12_1 5875
ENV CLIENT 5875

#0. None, 1. Compile extractors
ENV EXTRACTORS 1

#0. None, 1. Compile anticheat
ENV ANTICHEAT 0

#0. None, 1. Compile scripts
ENV SCRIPTS 1

#0. None, 1. Compile with libcurl for email support
ENV LIBCURL 0
#---------------------------------------------------------

CMD mkdir $vmangos_src/build && cd $vmangos_src/build && \
	cmake \
	-DDEBUG=$DEBUG \
	-DUSE_STD_MALLOC=$MALLOC \
	-DSUPPORTED_CLIENT_BUILD=$CLIENT \
	-DUSE_EXTRACTORS=$EXTRACTORS \
	-DUSE_ANTICHEAT=$ANTICHEAT \
	-DSCRIPTS=$SCRIPTS \
	-DUSE_LIBCURL=$LIBCURL \
	-DCMAKE_INSTALL_PREFIX=$vmangos ../ && \
	make -j $threads && \
	make install && \
	mkdir $vmangos/data && \
	mkdir $vmangos/logs && \
	cp $vmangos/etc/mangosd.conf.dist $vmangos/etc/mangosd.conf && \
	cp $vmangos/etc/realmd.conf.dist $vmangos/etc/realmd.conf && \
	cp -r /opt/vmangos/* /vmangos && \
	cd /database && 7z e $world.7z



