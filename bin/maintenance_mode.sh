#!/usr/bin/env bash
set -e
ENVIRONMENT=$1
MAINTENANCE_MODE=${2:-True}

if [ "$ENVIRONMENT" == "uat" ]; then
  NAMESPACE="laa-cla-backend-uat"
  URL="https://laa-cla-backend-uat.apps.live-1.cloud-platform.service.justice.gov.uk/maintenance"
elif [ "$ENVIRONMENT" == "staging" ]; then
  NAMESPACE="laa-cla-backend-staging"
  URL="https://staging.fox.civillegaladvice.service.gov.uk/maintenance"
elif [ "$ENVIRONMENT" == "training" ]; then
  NAMESPACE="laa-cla-backend-training"
  URL="https://training.fox.civillegaladvice.service.gov.uk/maintenance"
elif [ "$ENVIRONMENT" == "production" ]; then
  NAMESPACE="laa-cla-backend-production"
  URL="https://fox.civillegaladvice.service.gov.uk/maintenance"
fi

if [ "$MAINTENANCE_MODE" == "True" ]; then
  EXPECTED_STATUS="503"
elif [ "$MAINTENANCE_MODE" == "False" ]; then
    EXPECTED_STATUS="200"
else
  echo "Invalid maintenance value of $MAINTENANCE_MODE"
  exit 1
fi

echo "NAMESPACE $NAMESPACE"
echo "URL $URL"
echo "MAINTENANCE MODE $MAINTENANCE_MODE"
echo "EXPECTED_STATUS $EXPECTED_STATUS"
kubens $NAMESPACE

kubectl -n $NAMESPACE create configmap maintenance-mode --from-literal=value=$MAINTENANCE_MODE --dry-run -o yaml | kubectl apply -f -
kubectl -n $NAMESPACE rollout restart deployment cla-backend-app
kubectl -n $NAMESPACE rollout restart deployment cla-backend-worker
echo "Checking site is in maintenance mode..."
STATUS=$(curl -L --silent --output /dev/null --write-out "%{http_code}" $URL)
while [ "$STATUS" != "$EXPECTED_STATUS" ]; do
    echo "Expecting $EXPECTED_STATUS got $STATUS...trying again"
    sleep 5
    STATUS=$(curl -L --silent --output /dev/null --write-out "%{http_code}" $URL)
done
echo "DONE $EXPECTED_STATUS got $STATUS"
