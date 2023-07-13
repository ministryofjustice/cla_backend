#!/usr/bin/env bash
set -e
ENVIRONMENT=$1
MAINTENANCE_MODE=${2:-True}

function apply_maintenance_mode() {
  NAMESPACE=$1
  DEPLOYMENTS=$2
  echo "---------------------------------------------------------------------------------------------------------------"
  echo "NAMESPACE $NAMESPACE"
  echo "MAINTENANCE MODE $MAINTENANCE_MODE"
  echo "EXPECTED_STATUS $EXPECTED_STATUS"

  kubectl -n $NAMESPACE create configmap maintenance-mode --from-literal=value=$MAINTENANCE_MODE --dry-run -o yaml | kubectl apply -f -
  kubectl -n $NAMESPACE rollout restart deployment $DEPLOYMENTS
  echo "---------------------------------------------------------------------------------------------------------------"
}

function confirm_maintenance_mode() {
  URL=$1
  echo "Checking $URL is in maintenance mode..."
  STATUS=$(curl -L --silent --output /dev/null --write-out "%{http_code}" $URL)
  while [ "$STATUS" != "$EXPECTED_STATUS" ]; do
      echo "Expecting $EXPECTED_STATUS got $STATUS...trying again"
      sleep 5
      STATUS=$(curl -L --silent --output /dev/null --write-out "%{http_code}" $URL)
  done
  echo "DONE $EXPECTED_STATUS got $STATUS"
}


if [ "$ENVIRONMENT" == "uat" ]; then
  BACKEND_NAMESPACE="laa-cla-backend-uat"
  FRONTEND_NAMESPACE="laa-cla-frontend-uat"
  BACKEND_URL="https://laa-cla-backend-uat.apps.live-1.cloud-platform.service.justice.gov.uk/maintenance"
  FRONTEND_URL="https://laa-cla-frontend-uat.apps.live-1.cloud-platform.service.justice.gov.uk/maintenance"
elif [ "$ENVIRONMENT" == "staging" ]; then
  BACKEND_NAMESPACE="laa-cla-backend-staging"
  FRONTEND_NAMESPACE="laa-cla-frontend-staging"
  PUBLIC_NAMESPACE="laa-cla-public-staging"
  BACKEND_URL="https://staging.fox.civillegaladvice.service.gov.uk/maintenance"
  FRONTEND_URL="https://staging.cases.civillegaladvice.service.gov.uk/maintenance"
  PUBLIC_URL="https://staging.checklegalaid.service.gov.uk/maintenance"
elif [ "$ENVIRONMENT" == "training" ]; then
  BACKEND_NAMESPACE="laa-cla-backend-training"
  FRONTEND_NAMESPACE="laa-cla-frontend-training"
  PUBLIC_NAMESPACE="laa-cla-public-staging"
  BACKEND_URL="https://training.fox.civillegaladvice.service.gov.uk/maintenance"
  FRONTEND_URL="https://training.cases.civillegaladvice.service.gov.uk/maintenance"
  PUBLIC_URL="https://training.checklegalaid.service.gov.uk/maintenance"
elif [ "$ENVIRONMENT" == "production" ]; then
  BACKEND_NAMESPACE="laa-cla-backend-production"
  FRONTEND_NAMESPACE="laa-cla-frontend-production"
  PUBLIC_NAMESPACE="laa-cla-public-production"
  BACKEND_URL="https://fox.civillegaladvice.service.gov.uk/maintenance"
  FRONTEND_URL="https://cases.civillegaladvice.service.gov.uk/maintenance"
  PUBLIC_URL="https://checklegalaid.service.gov.uk/maintenance"
fi

if [ "$MAINTENANCE_MODE" == "True" ]; then
  EXPECTED_STATUS="503"
elif [ "$MAINTENANCE_MODE" == "False" ]; then
    EXPECTED_STATUS="200"
else
  echo "Invalid maintenance value of $MAINTENANCE_MODE"
  exit 1
fi

apply_maintenance_mode $BACKEND_NAMESPACE "cla-backend-app cla-backend-worker"
apply_maintenance_mode $FRONTEND_NAMESPACE "cla-frontend-app cla-frontend-socket-server"
if [ "$ENVIRONMENT" != "uat" ]; then
  apply_maintenance_mode $PUBLIC_NAMESPACE "cla-public-app"
fi

confirm_maintenance_mode $BACKEND_URL
confirm_maintenance_mode $FRONTEND_URL
if [ "$ENVIRONMENT" != "uat" ]; then
  confirm_maintenance_mode $PUBLIC_URL
fi
