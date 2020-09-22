#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

helm upgrade $RELEASE_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_PRODUCTION_NAMESPACE} \
  --set fullnameOverride=$RELEASE_NAME \
  --set host=$RELEASE_HOST \
  --set secretName=tls-certificate \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --install
