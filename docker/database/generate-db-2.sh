#!/bin/sh 

echo 'Importing databases'

echo 'Importing logon'
mysql -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/vmangos/sql/logon.sql

echo 'Importing logs'
mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/vmangos/sql/logs.sql

echo 'Importing characters'
mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/vmangos/sql/characters.sql

echo 'Importing world'
mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/database/$world.sql
echo 'Databases imported'

echo 'Importing changes'
mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/vmangos/sql/migrations/world_db_updates.sql

echo 'Configuring default realm'
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "INSERT INTO realmd.realmlist (name, address, port, icon, realmflags, timezone, allowedSecurityLevel, population, gamebuild_min, gamebuild_max, flag, realmbuilds) VALUES ('$realm_name', '$realm_ip', '$realm_port', '$realm_icon', '$realmflags', '$timezone', '$allowedSecurityLevel', '$population', '$gamebuild_min', '$gamebuild_max', '$flag','');"
echo 'Database creation is complete'

