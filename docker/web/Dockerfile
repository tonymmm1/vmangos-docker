FROM php:7.1-fpm
RUN apt-get update && apt-get install -y \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
	libxml2-dev \
        libpng-dev 
RUN docker-php-ext-configure gd --with-jpeg-dir=/usr/lib --with-freetype-dir=/usr/include/freetype2 --enable-gd-native-ttf \
	&& docker-php-ext-install gd mysqli soap -j$(nproc)
