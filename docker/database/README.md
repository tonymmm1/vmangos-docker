# Database image

This image initializes the four VMaNGOS schemas in a persistent MariaDB volume.
The root and application passwords are read from Docker file secrets, and the
application account is granted access only to `realmd`, `characters`, `mangos`,
and `logs`.

The base Compose model keeps MariaDB on an internal network. Use
`docker-compose.admin.yml` only when a host-side administration port is needed.
