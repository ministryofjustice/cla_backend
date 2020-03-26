#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

CLEANED_BRANCH_NAME=$(echo $CIRCLE_BRANCH | sed 's/^feature[-/]//' | sed 's:^\w*\/::' | tr -s ' _/[]().' '-' | cut -c1-28 | sed 's/-$//')
RELEASE_NAME=${CLEANED_BRANCH_NAME}
RELEASE_HOST="$RELEASE_NAME.$STAGING_HOST"

helm upgrade $RELEASE_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set host=$RELEASE_HOST \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --install