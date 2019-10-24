echo 'This script will delete input realm'
read -p 'Input realm number ' number

docker-compose down -v
rm -rf docker/mangos_$number
rm -rf docker/database/generate-db-1_$number.sql
rm -rf docker/database/generate-db-2_$number.sh
rm -rf vmangos/etc/mangosd_$number.conf
rm -rf server_$number.env
sed -i "/server_$number.env/d" docker-compose.yml
sed -e "s#COPY docker/database/generate-db-1_$number.sql /docker-entrypoint-initdb.d##g" -i docker/database/Dockerfile
sed -e "s#COPY docker/database/generate-db-2_$number.sh /docker-entrypoint-initdb.d##g" -i docker/database/Dockerfile
