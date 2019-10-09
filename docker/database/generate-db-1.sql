CREATE DATABASE IF NOT EXISTS realmd DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS characters DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS mangos DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS logs DEFAULT CHARSET utf8 COLLATE utf8_general_ci;

create user 'mangos'@'localhost' identified by 'mangos';
SET PASSWORD FOR 'mangos'@'localhost' = PASSWORD('mangos');
GRANT ALL PRIVILEGES ON *.* TO 'mangos'@'%' IDENTIFIED BY 'mangos';
flush privileges;
grant all on realmd.* to mangos@'localhost' with grant option;
grant all on characters.* to mangos@'localhost' with grant option;
grant all on mangos.* to mangos@'localhost' with grant option;
grant all on logs.* to mangos@'localhost' with grant option;

