FROM php:7.1-fpm
RUN apt-get update && apt-get install -y \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
	libxml2-dev \
        libpng-dev \
	libicu-dev \
	libldap2-dev \
	libc-client-dev \
	libkrb5-dev \
	libbz2-dev 
RUN docker-php-ext-configure gd --with-jpeg-dir=/usr/lib --with-freetype-dir=/usr/include/freetype2 --enable-gd-native-ttf \
	&& docker-php-ext-configure ldap --with-libdir=lib/x86_64-linux-gnu/ \
	&& docker-php-ext-configure imap --with-kerberos --with-imap-ssl \
	&& docker-php-ext-install gd mysqli soap ldap imap intl exif bz2 gettext -j$(nproc)

