export DOCKER_BUILDKIT=1
export ENVIRONMENT=$1
docker-compose down --remove-orphans
docker-compose build cla_backend
if [ $ENVIRONMENT="test" ]; then
  docker-compose run cla_backend
else
  docker-compose run start_applications
  docker-compose exec cla_backend bin/create_db.sh
fi



