FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ACE_ROOT=/usr/include/ace
ENV TBB_ROOT_DIR=/usr/include/tbb
ENV VMANGOS_SRC=/opt/core
ENV VMANGOS_BIN=/opt/vmangos
ENV WORLD_DB=world_full_14_june_2021

# Compile Variables
ENV THREADS=2
ENV MALLOC=0
ENV CLIENT=5875
ENV EXTRACTORS=1
ENV ANTICHEAT=1
ENV SCRIPTS=1
ENV LIBCURL=1

RUN apt-get update -y && \
	apt-get install -y \
		build-essential \
		ccache \
		cmake \
		git \
		libace-dev \
		libcurl4-openssl-dev \
		libmysql++-dev \
		libreadline-dev \
		libssl-dev \
		libtbb-dev \
		make \
		openssl \
		p7zip-full
		
RUN ln -s /usr/bin/ccache /usr/local/bin/gcc \ 
	&& ln -s /usr/bin/ccache /usr/local/bin/g++ \
	&& ln -s /usr/bin/ccache /usr/local/bin/cc \
	&& ln -s /usr/bin/ccache /usr/local/bin/c++

RUN export ACE_ROOT=/usr/include/ace && export TBB_ROOT_DIR=/usr/include/tbb

COPY /src/core/ /opt/core

CMD mkdir $VMANGOS_SRC/build && cd $VMANGOS_SRC/build && \
	cmake \
	-DUSE_STD_MALLOC=$MALLOC \
	-DSUPPORTED_CLIENT_BUILD=$CLIENT \
	-DUSE_EXTRACTORS=$EXTRACTORS \
	-DUSE_ANTICHEAT=$ANTICHEAT \
	-DSCRIPTS=$SCRIPTS \
	-DUSE_LIBCURL=$LIBCURL \
	-DCMAKE_INSTALL_PREFIX=$VMANGOS ../ && \
	make -j $THREADS && \
	make install && \
	mkdir $VMANGOS/data && \
	mkdir $VMANGOS/logs && \
	cp $VMANGOS/etc/mangosd.conf.dist $VMANGOS/etc/mangosd.conf && \
	cp $VMANGOS/etc/realmd.conf.dist $VMANGOS/etc/realmd.conf && \
	cp -r /opt/vmangos/* /vmangos && \
	cd /database && 7z e $WORLD_DB.7z
