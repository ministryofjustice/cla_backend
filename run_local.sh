
docker-compose down --remove-orphans
docker-compose run start_applications
docker-compose exec cla_backend bin/create_db.sh
