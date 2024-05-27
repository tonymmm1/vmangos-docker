#!/bin/sh 

echo 'Importing databases'

echo 'Importing logon'
mariadb -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/vmangos/sql/logon.sql

echo 'Importing logs'
mariadb -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/vmangos/sql/logs.sql

echo 'Importing characters'
mariadb -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/characters.sql

echo 'Importing world'
mariadb -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/database/$WORLD.sql
echo 'Databases imported'

echo 'Importing changes'
mariadb -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql
mariadb -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/migrations/characters_db_updates.sql
mariadb -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/vmangos/sql/migrations/logon_db_updates.sql
mariadb -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/vmangos/sql/migrations/logs_db_updates.sql

echo 'Upgrading mysql'
mariadb-upgrade -u root -p$MYSQL_ROOT_PASSWORD

echo 'Configuring default realm'
mariadb -u root -p$MYSQL_ROOT_PASSWORD -e "INSERT INTO realmd.realmlist (name, address, port, icon, realmflags, timezone, allowedSecurityLevel, population, gamebuild_min, gamebuild_max, flag, realmbuilds) VALUES ('$realm_name', '$realm_ip', '$realm_port', '$realm_icon', '$realmflags', '$timezone', '$allowedSecurityLevel', '$population', '$gamebuild_min', '$gamebuild_max', '$flag','');"
echo 'Database creation is complete'
