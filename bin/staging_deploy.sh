#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

if ! helm ls | grep cla-backend
then
  helm upgrade cla-backend \
    $HELM_DIR \
    --values ${HELM_DIR}/values-staging.yaml \
    --set image.tag=$IMAGE_TAG
fi

helm upgrade cla-backend \
  $HELM_DIR \
  --values ${HELM_DIR}/values-staging.yaml \
  --set image.tag=$IMAGE_TAG