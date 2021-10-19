#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
DYNAMIC_HOSTNAME=$1
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"
VALUES="values-uat-static.yaml"
if [ $DYNAMIC_HOSTNAME = true ]; then
  VALUES="values-uat.yaml"
fi
helm upgrade $RELEASE_NAME \
  $HELM_DIR \
  --namespace=${KUBE_ENV_UAT_NAMESPACE} \
  --values "${HELM_DIR}/$VALUES" \
  --set fullnameOverride=$RELEASE_NAME \
  --set environment=$RELEASE_NAME \
  --set host=$RELEASE_HOST \
  --set ingress.cluster.name=${INGRESS_CLUSTER_NAME} \
  --set ingress.cluster.weight=${INGRESS_CLUSTER_WEIGHT} \
  --set image.repository=$DOCKER_REPOSITORY \
  --set image.tag=$IMAGE_TAG \
  --set-string pingdomIPs=$PINGDOM_IPS \
  --install
