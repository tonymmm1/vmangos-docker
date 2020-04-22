FROM ubuntu:18.04

#RUN apt-get update -y && apt-get install software-properties-common -y && add-apt-repository universe -y && apt-get update -y && apt-get install build-essential gcc g++ automake git-core git autoconf make patch libmysql++-dev libtool libssl-dev grep binutils zlibc libc6 libbz2-dev cmake subversion libboost-all-dev wget tmux p7zip-full libtbb-dev libace-dev libmysqlclient-dev openssl libssl-dev zlib1g-dev p7zip-full ccache -y

RUN apt-get update -y && apt-get upgrade -y

RUN apt-get install -y \
	g++ \
	cmake \
	libtbb-dev \
	libcurl4-openssl-dev \
	libace-dev \
	libmysql++-dev \ 
	p7zip-full \ 
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

CMD mkdir $vmangos_src/build && cd $vmangos_src/build && cmake -DDEBUG=0 -DSUPPORTED_CLIENT_BUILD=5875 -DUSE_EXTRACTORS=1 -DCMAKE_INSTALL_PREFIX=$vmangos ../ && make -j $(nproc) && make install && mkdir $vmangos/data && mkdir $vmangos/logs && cp $vmangos/etc/mangosd.conf.dist $vmangos/etc/mangosd.conf && cp $vmangos/etc/realmd.conf.dist $vmangos/etc/realmd.conf && cp -r /opt/vmangos/* /vmangos && cd /database && 7z e $world.7z



