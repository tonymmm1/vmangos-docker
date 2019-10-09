#!/bin/sh

echo 'Importing databases'

echo 'Importing logon'
mysql -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/sql/logon.sql

echo 'Importing logs'
mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/sql/logs.sql

echo 'Importing characters'
mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/sql/characters.sql

echo 'Importing world'
mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/sql/database/$world.sql
echo 'Databases imported'


echo 'Importing changes'
if (test -f /opt/sql/migrations/world_db_updates.sql) ; then
	mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/sql/migrations/world_db_updates.sql
	echo 'World changes imported'
else
	echo 'No world changes to import'
fi

if (test -f /opt/sql/migrations/characters_db_updates.sql) ; then
        mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/sql/migrations/characters_db_updates.sql
        echo 'character changes imported'
else
        echo 'No characters changes to import'
fi

if (test -f /opt/sql/migrations/logs_db_updates.sql) ; then
        mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/sql/migrations/logs_db_updates.sql
        echo 'Logs changes imported'
else
        echo 'No logs changes to import'
fi

if (test -f /opt/sql/migrations/logon_db_updates.sql) ; then
        mysql -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/sql/migrations/logon_db_updates.sql
        echo 'Logon changes imported'
else
        echo 'No logon changes to import'
fi

echo 'Configuring default realm'
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "DELETE FROM realmd.realmlist WHERE id=1;"
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "INSERT INTO realmd.realmlist (id, name, address, port, icon, realmflags, timezone, allowedSecurityLevel, population, gamebuild_min, gamebuild_max, flag) VALUES ('$realm_id', '$realm_name', '$realm_ip', '$realm_port', '$realm_icon', '$realmflags', '$timezone', '$allowedSecurityLevel', '$population', '$gamebuild_min', '$gamebuild_max', '$flag');"
echo 'Database creation is complete'

