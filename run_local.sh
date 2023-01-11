export DOCKER_BUILDKIT=1
docker-compose down --remove-orphans
docker-compose build cla_backend
docker-compose run start_applications
docker-compose exec cla_backend bin/create_db.sh
