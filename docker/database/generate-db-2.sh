#!/bin/sh
echo 'Importing databases'
mysql -u root -p$MYSQL_ROOT_PASSWORD realmd < /opt/sql/logon.sql
mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/sql/logs.sql
mysql -u root -p$MYSQL_ROOT_PASSWORD characters < /opt/sql/characters.sql
mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/sql/world.sql
echo 'Databases imported'

echo 'Importing changes'
mysql -u root -p$MYSQL_ROOT_PASSWORD logs < /opt/sql/migrations/logs_db_updates.sql
mysql -u root -p$MYSQL_ROOT_PASSWORD mangos < /opt/sql/migrations/world_db_updates.sql
echo 'Changes imported'

mysql -u root -p$MYSQL_ROOT_PASSWORD -e "DELETE FROM realmd.realmlist WHERE id=1;"
mysql -u root -p$MYSQL_ROOT_PASSWORD -e "INSERT INTO realmd.realmlist (id, name, address, port, icon, realmflags, timezone, allowedSecurityLevel) VALUES ('1', 'Servername', 'Server IP Address', '8085', '1', '0', '1', '0');"

