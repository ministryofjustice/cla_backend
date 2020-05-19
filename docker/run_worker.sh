                                                                                                          #!/usr/bin/env bash
set -e
exec celery worker -A cla_backend --concurrency=${WORKER_APP_CONCURRENCY:-4} --loglevel=${LOG_LEVEL:-INFO}
