#!/usr/bin/env bash
set -e
KUBE_CONTEXT="docker-for-desktop"
ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend-migration/"

kubectl config use-context $KUBE_CONTEXT
helm upgrade cla-backend-migration \
  $HELM_DIR \
  --install \
  --force \
  --debug
