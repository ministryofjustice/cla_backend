#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

helm upgrade $RELEASE_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_STAGING_NAMESPACE} \
  --values ${HELM_DIR}/values-staging.yaml \
  --set host=$RELEASE_HOST \
  --set ingress.cluster.name=${INGRESS_CLUSTER_NAME} \
  --set ingress.cluster.weight=${INGRESS_CLUSTER_WEIGHT} \
  --set secretName=tls-certificate \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --install
