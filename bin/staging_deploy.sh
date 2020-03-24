#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

helm upgrade cla-backend \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --install