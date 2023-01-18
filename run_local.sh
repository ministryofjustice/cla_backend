#!/bin/bash
export DOCKER_BUILDKIT=1
export ENVIRONMENT=${1:-development}
export UNIT_TEST=${2:-""}
echo "running environment $ENVIRONMENT"
docker-compose down --remove-orphans
docker-compose build cla_backend
if [ $ENVIRONMENT = "test" ]; then
  export DJANGO_SETTINGS=cla_backend.settings.circle
  docker-compose build cla_backend --build-arg specific_test_input=$UNIT_TEST
  docker-compose run cla_backend
else
  docker-compose build cla_backend
  docker-compose run start_applications
  docker-compose exec cla_backend bin/create_db.sh
fi
