#!/bin/bash 

echo 'This script is for creating a new realm'
number=1
while [ $number -lt 2 ]
do
	read -p 'Input a value higher than 1: ' number
done
export number 

mangos_port=$((8085+$number))

echo 'Editing config files'
#Editing of config files used by docker container
cp server.env server_$number.env
sed -i "s/realm_id=1/realm_id_$number=$number/g" server_$number.env
sed -i "s/realm_port=8085/realm_port_$number=$mangos_port/g" server_$number.env
sed -i "s/realm_name=vmangos/realm_name_$number=vmangos_$number/g" server_$number.env

echo "number=$number" >> server_$number.env
#Mangos portion
echo 'Configuring mangos'
cp vmangos/etc/mangosd.conf vmangos/etc/mangosd_$number.conf
sed -i "s/127.0.0.1;3306;mangos;mangos;realmd/vmangos_database;3306;mangos;mangos;realmd/g" vmangos/etc/mangosd_$number.conf
sed -i "s/127.0.0.1;3306;mangos;mangos;mangos/vmangos_database;3306;mangos;mangos;mangos_$number/g" vmangos/etc/mangosd_$number.conf
sed -i "s/127.0.0.1;3306;mangos;mangos;characters/vmangos_database;3306;mangos;mangos;characters_$number/g" vmangos/etc/mangosd_$number.conf
sed -i "s/127.0.0.1;3306;mangos;mangos;logs/vmangos_database;3306;mangos;mangos;logs_$number/g" vmangos/etc/mangosd_$number.conf
sed -i "s/RealmID = 1/RealmID = $number/g" vmangos/etc/mangosd_$number.conf
sed -i "s/WorldServerPort = 8085/WorldServerPort = $mangos_port/g" vmangos/etc/mangosd_$number.conf
mkdir docker/mangos_$number
cp docker/mangos/Dockerfile docker/mangos_$number/
sed -i "/RUN sed/d" docker/mangos_$number/Dockerfile
sed -i "s|COPY vmangos/etc/mangosd.conf|COPY vmangos/etc/mangosd_$number.conf|g" docker/mangos_$number/Dockerfile

#Database portion
echo 'Configuring database'
cp docker/database/generate-db-1.sql docker/database/generate-db-1_$number.sql
cp docker/database/generate-db-2.sh docker/database/generate-db-2_$number.sh
sed -i '/CREATE DATABASE IF NOT EXISTS realmd DEFAULT CHARSET utf8 COLLATE utf8_general_ci;/d' -i docker/database/generate-db-1_$number.sql
sed -e "s/create user 'mangos'@'localhost' identified by 'mangos';//g" -i docker/database/generate-db-1_$number.sql
sed -e "s/SET PASSWORD FOR 'mangos'@'localhost' = PASSWORD('mangos');//g" -i docker/database/generate-db-1_$number.sql
sed -i "s/CREATE DATABASE IF NOT EXISTS characters/CREATE DATABASE IF NOT EXISTS characters_$number/g" docker/database/generate-db-1_$number.sql
sed -i "s/CREATE DATABASE IF NOT EXISTS mangos/CREATE DATABASE IF NOT EXISTS mangos_$number/g" docker/database/generate-db-1_$number.sql
sed -i "s/CREATE DATABASE IF NOT EXISTS logs/CREATE DATABASE IF NOT EXISTS logs_$number/g" docker/database/generate-db-1_$number.sql
sed -i "s/grant all on characters.* to mangos@'localhost' with grant option;/grant all on characters_$number.* to mangos@'localhost' with grant option;/g" docker/database/generate-db-1_$number.sql
sed -i "s/grant all on mangos.* to mangos@'localhost' with grant option;/grant all on mangos_$number.* to mangos@'localhost' with grant option;/g" docker/database/generate-db-1_$number.sql
sed -i "s/grant all on logs.* to mangos@'localhost' with grant option;/grant all on logs_$number.* to mangos@'localhost' with grant option;/g" docker/database/generate-db-1_$number.sql
sed -i '/sh/a\mysql -u root -p$MYSQL_ROOT_PASSWORD -e "source /docker-entrypoint-initdb.d/generate-db-1_$number.sql;"' docker/database/generate-db-2_$number.sh
sed -i "s/$MYSQL_ROOT_PASSWORD characters/$MYSQL_ROOT_PASSWORD characters_$number/g" docker/database/generate-db-2_$number.sh
sed -i "s/$MYSQL_ROOT_PASSWORD mangos/$MYSQL_ROOT_PASSWORD mangos_$number/g" docker/database/generate-db-2_$number.sh
sed -i "s/$MYSQL_ROOT_PASSWORD logs/$MYSQL_ROOT_PASSWORD logs_$number/g" docker/database/generate-db-2_$number.sh
sed -i '/logon/d' docker/database/generate-db-2_$number.sh
sed -i '/mysql -u root -p$MYSQL_ROOT_PASSWORD -e "DELETE FROM realmd.realmlist WHERE id=1;"/d' docker/database/generate-db-2_$number.sh
sed -i "s/realm_port/realm_port_$number/g" docker/database/generate-db-2_$number.sh
sed -i "s/realm_name/realm_name_$number/g" docker/database/generate-db-2_$number.sh
sed -i "s/realm_id/realm_id_$number/g" docker/database/generate-db-2_$number.sh
sed -i -e "\$aCOPY docker/database/generate-db-1_$number.sql /docker-entrypoint-initdb.d" docker/database/Dockerfile
sed -i -e "\$aCOPY docker/database/generate-db-2_$number.sh /docker-entrypoint-initdb.d"  docker/database/Dockerfile

#Docker compose
docker-compose stop 
sed -i -e "/\- server.env/a \ \ \ \ \ \ - server_$number.env" docker-compose.yml

cat > realm-template << 'EOF'
  vmangos_mangos_Number:
    tty: true
    stdin_open: true
    ports: 
      - Mangos_port:Mangos_port
    build:
      context: .
      dockerfile: docker/mangos_Number/Dockerfile
    depends_on:
      - vmangos_database
    links:
      - vmangos_database
    restart: unless-stopped
EOF

sed -i -e '/#Docker-compose volumes/r realm-template' -e 'x;$G' docker-compose.yml

sed -i "s/Number/$number/g" docker-compose.yml
sed -i "s/Mangos_port/$mangos_port/g" docker-compose.yml

#Rebuilding database container
docker-compose build vmangos_database
docker-compose up -d vmangos_database
docker-compose exec vmangos_database sh -c "chmod +x /docker-entrypoint-initdb.d/generate-db-2_$number.sh"
docker-compose exec vmangos_database sh -c "./docker-entrypoint-initdb.d/generate-db-2_$number.sh"
docker-compose up -d 
